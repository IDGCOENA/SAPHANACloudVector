"""In this scenario, we show how we could use langchain  to access embedding models[text-embedding-ada-002] 
   from "Azure OpenAI/OpenAI" and ingest the embedded data into SAP HANA Cloud using langchain plugin. PLease refer
   https://python.langchain.com/docs/integrations/text_embedding/azureopenai
   https://python.langchain.com/docs/integrations/text_embedding/openai
   https://python.langchain.com/docs/integrations/vectorstores/sap_hanavector
   Data source is provided as part of the mission. 
   Please install the necessary packages 
    pip install   hdbcli || hana_ml || datetime || tiktoken || re || python-dotenv || shapely 
                  ||typing || langchain-community || langchain || openai
"""
#import the necessary linraries from langchain to use OpenAI/Azure Open AI
from langchain_openai import AzureOpenAIEmbeddings,OpenAIEmbeddings
#import the vector store modules to access "HanaDB"
from langchain_community.vectorstores.hanavector import HanaDB
#make sure you add azure_deployment(deployment name for embedding model),azure_endpoint(Endpoint from Azure portal) & api_key
embeddings = AzureOpenAIEmbeddings(azure_deployment="t4sap",azure_endpoint="https://sap-openai.openai.azure.com/",api_key="93c4ccc9eac54631afcf7b181cc48b0f",api_version="2023-03-15-preview")
#if you are using OpenAI Keys, the provide the parameters as below
#embeddings = OpenAIEmbeddings(model="text-embedding-ada-002",api_key="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")
import os
from dotenv import load_dotenv
import hana_ml.dataframe as dataframe
from  hdbcli import dbapi
from typing import List
from langchain.docstore.document import Document
#load the necessary variable to access your SAP HANA Cloud DB
load_dotenv()
# Get the HANA Cloud username from environment variables
HANA_USER_VDB = os.getenv('HANA_VECTOR_USER')
# Get the HANA Cloud password from environment variables
HANA_PASSWORD_VDB = os.getenv('HANA_VECTOR_PASS')
# Get the HANA Cloud host from environment variables
HANA_HOST  = os.getenv('HANA_HOST_VECTOR')
SCHEMA_NAME = "VECTOR_DEMO"  #Provide the schema name where you want the embedded data to be stored 
TABLE_NAME  = "CUSTOMER_REVIEWS_LCHAIN1"#Provide the table name where you want the embedded data to be stored
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
# Establish a second connection to the HANA Cloud database using dbapi.connect
conn1 = dbapi.connect(
    address=HANA_HOST, 
    port=443, 
    user=HANA_USER_VDB, 
    password=HANA_PASSWORD_VDB,
    currentSchema= SCHEMA_NAME #provide the schema where you want to store the embedding tables. Else it will use defaut user schema
    
)

#Select the columns from JSON document "REVIEWS_1K" that is provided as part of the test schema
#We make use of the multimodeling feature here to read content from JSON to SQL directly 
Free_Tier = ''  # If You are NOT using Free Tier, then set it to ''

if Free_Tier == 'X':
    df2 = conn.sql('select "filename", "text" from "VECTOR_DEMO"."REVIEWS_SOURCE" LIMIT 100') # Select from table
else:
    df2 = conn.sql('select "filename", "text" from "VECTOR_DEMO"."REVIEWS_1K" LIMIT 100') # select from JSON collection
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
#initiating the HANADB instance with our custom table and columns and our langchain plugin will automatically create the table
#This function abstracts the whole steps that we followed in Scenario1 to ingest the vectors into SAP HANA DB. Cool, isnt it?
db = HanaDB(
    connection=conn1,
    embedding=embeddings, 
    table_name="REVIEWS4",
    content_column="TEXT",
    metadata_column="FILENAME",
    vector_column="VECTOR"
)
#finally appending the json documents using add_documents which will create the new table REVIEWS
db.add_documents(docs)