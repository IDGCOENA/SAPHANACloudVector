"""In this scenario, we show how we could use genaihub SDK to access embedding models[text-embedding-ada-002] and 
   ingest the embedded data into SAP HANA Cloud using langchain plugin. PLease refer
   https://python.langchain.com/docs/integrations/vectorstores/sap_hanavector  
   This would be the easier approach to embed and ingest the data as this is process is handled by the plugin 
   Data source is provided as part of the mission. 
   Please install the necessary packages 
    pip install   generative-ai-hub-sdk ||hdbcli || hana_ml || datetime || tiktoken || re || python-dotenv || shapely 
                  ||typing || langchain-community || langchain
"""
# Import the embeddings module from SAPs Generative AI Hub SDK
from gen_ai_hub.proxy.langchain import OpenAIEmbeddings
from langchain_community.vectorstores.hanavector import HanaDB
from langchain.docstore.document import Document
from typing import List
#In order to ingest the embedded data into SAP HANA Cloud(INSERT), we need to initiate the hdbcli module
from  hdbcli import dbapi
# In order to access the JSON documents from the sample schema we provided, we use the HANA_ML package
import hana_ml.dataframe as dataframe
# Import the os module to access the environment variables from env file where we maintain credentials for SAP HANA Cloud
import os
# Import the load_dotenv function from dotenv. To load the credentials from env file
from dotenv import load_dotenv
# Load environment variables from a .env file
load_dotenv()
# Get the HANA Cloud username from environment variables
HANA_USER_VDB = os.getenv('HANA_VECTOR_USER')
# Get the HANA Cloud password from environment variables
HANA_PASSWORD_VDB = os.getenv('HANA_VECTOR_PASS')
# Get the HANA Cloud host from environment variables
HANA_HOST  = os.getenv('HANA_HOST_VECTOR')
SCHEMA_NAME = "VECTOR_DEMO"  #Provide the schema name where you want the embedded data to be stored 
TABLE_NAME  = "CUSTOMER_REVIEWS_LCHAIN"#Provide the table name where you want the embedded data to be stored
# Establish a connection to the HANA Cloud database using HANA_ML package
conn = dataframe.ConnectionContext(
    address=HANA_HOST,  
    port=443,
    user=HANA_USER_VDB,
    password=HANA_PASSWORD_VDB,
    current_schema=SCHEMA_NAME,
    #schema = SCHEMA_NAME,
    encrypt='true'
)
print(conn.get_current_schema())
# Establish a second connection to the HANA Cloud database using dbapi.connect
conn1 = dbapi.connect(
    address=HANA_HOST, 
    port=443, 
    user=HANA_USER_VDB, 
    password=HANA_PASSWORD_VDB,
    currentSchema= SCHEMA_NAME
    
)
#Initiate the embedding model to be used from GenAI Hub and provide additional parameters as chunk size
embeddings = OpenAIEmbeddings(proxy_model_name='text-embedding-ada-002', chunk_size=100, max_retries=10)
#Select the columns from JSON document "REVIEWS_1K" that is provided as part of the test schema
#We make use of the multimodeling feature here to read content from JSON to SQL directly 
#We have limited it to 100 documents but could remove the limit if you want to process for all JSON documents  #
df2 = conn.sql('select "filename", "text" from "VECTOR_DEMO"."REVIEWS_1K" LIMIT 100 ')
df = df2.collect()
# List your actual text and sourcefiles from JSON document to the format required by our HANA Cloud langchain plugin
# the columns from df is mapped to page_content and metadata 
docs: List[Document] = [
    Document(
        page_content=row['text'],
        metadata={"doc_name": row['filename']}
    )
    for _, row in df.iterrows()
]
#initiating the HANADB instance with our custom table and columns
db = HanaDB(
    connection=conn1,
    embedding=embeddings,
   # schema = "VDEMO1",
    table_name="REVIEWS",
    content_column="TEXT",
    metadata_column="FILENAME",
    vector_column="VECTOR"
)
#finally appending the json documents using add_documents
db.add_documents(docs)
