"""In this scenario, we show how we could use genaihub SDK to access embedding models[text-embedding-ada-002] and 
   ingest the embedded data into SAP HANA Cloud using hdbcli. For embedding, we are using the method "embed_documents"
   as mentioned in https://python.langchain.com/docs/modules/data_connection/text_embedding/
    Data source is provided as part of the mission. 
   Please install the necessary packages 
    pip install   generative-ai-hub-sdk ||hdbcli || hana_ml || datetime || tiktoken || python-dotenv || shapely    
"""
# Import the embeddings module from SAPs Generative AI Hub SDK 
from gen_ai_hub.proxy.langchain.init_models import init_embedding_model
#In order to ingest the embedded data into SAP HANA Cloud(INSERT), we need to initiate the hdbcli module
from  hdbcli import dbapi
# In order to access the JSON documents or test data from the sample schema we provided, we use the HANA_ML package
import hana_ml.dataframe as dataframe
# Import the os module to access the environment variables from env file where we maintain credentials for SAP HANA Cloud
import os
# Import the datetime module to calculate time needed for embeddings the JSON documents and ingesting into SAP HANA Cloud
import datetime
# Import the tiktoken module. This helps us to split the text string and provide the tokens. 
# Embedding models have token limit and tiktoken helps us see the text in the form of tokens
import tiktoken
# Import the re module for regular expression operations
import re
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

# Establish a connection to the HANA Cloud database using HANA_ML package
conn = dataframe.ConnectionContext(
    address=HANA_HOST,  
    port=443,
    user=HANA_USER_VDB,
    password=HANA_PASSWORD_VDB,
    encrypt='true'
)
# Establish a second connection to the HANA Cloud database using dbapi.connect
conn1 = dbapi.connect(
    address=HANA_HOST, 
    port=443, 
    user=HANA_USER_VDB, 
    password=HANA_PASSWORD_VDB   
)
# Define helper functions to clean up the source text files
def normalize_text(s, sep_token = " \n "):
    s = re.sub(r'\s+',  ' ', s).strip()
    s = re.sub(r". ,","",s)
    s = s.replace("..",".")
    s = s.replace(". .",".")
    s = s.replace("\n", "")
    s = s.strip()    
    return s
SCHEMA_NAME = "VECTOR_DEMO"  #Provide the EXISTING schema name where you want the embedded data to be stored 
TABLE_NAME  = "CUSTOMER_REVIEWS_LC4"#Provide ANY new table name where you want the embedded data to be stored
#Create the table the first time you execute the script. And from the second iteration, it will directly select from the table
if not conn.has_table(table=TABLE_NAME, schema=SCHEMA_NAME):
    conn.create_table(table=TABLE_NAME, schema=SCHEMA_NAME, table_structure={'FILENAME':'NVARCHAR(100)','TEXT':'NCLOB','VECTOR':'REAL_VECTOR(1536)'})
#Select the columns from JSON document "REVIEWS_1K" that is provided as part of the test schema
#We make use of the multimodeling feature here to read content from JSON to SQL directly 
Free_Tier = 'X'  # If You are NOT using Free Tier, then set it to ''

if Free_Tier == 'X':
    df2 = conn.sql('select "filename", "text" from "VECTOR_DEMO"."REVIEWS_SOURCE" LIMIT 100') # Select from table
else:
    df2 = conn.sql('select "filename", "text" from "VECTOR_DEMO"."REVIEWS_1K" LIMIT 100') # select from JSON collection

df = df2.collect()
#We have limited it to 100 documents but could remove the limit if you want to process for all JSON documents

# Set up the list all_rows to collect the source file , text and embeeded text
all_rows = []
start_time_embeddings = datetime.datetime.now()  #Lets start calculating embedding time 
# Normalize the text in the 'text' column. We are calling the function normalize_text defined in line 44
df['text']= df["text"].apply(lambda x : normalize_text(x))
tokenizer = tiktoken.get_encoding("cl100k_base") #INitialize tiktoken to get the number of tokens for every row of text
# Count the number of tokens for every row 'text' column. This is to make sure token length doesnt exceed embedding model limit
df['n_tokens'] = df["text"].apply(lambda x: len(tokenizer.encode(x)))
embeddings = init_embedding_model('text-embedding-ada-002') # initialize the embedding model
#in this line we are initializing "embed_documents" provided by langchain to embed multiple texts 
#check https://python.langchain.com/docs/modules/data_connection/text_embedding/  
embedded_text_column = embeddings.embed_documents(df['text'].tolist())
# converting the embedded text as string. If we are using native langchain plugin for SAP HANA cloud, we dont have to do this :)
str_embedded_text_column = [str(list(embedding)) for embedding in embedded_text_column]
df['VECTOR'] = str_embedded_text_column #moving the embedded texts to dataframe
df['filename'] = df["filename"]  #moving the filename column  to dataframe
# Create a list of tuples containing the filename, text and its corresponding vector
rows = [(row['filename'],row['text'],str(row['VECTOR'])) for index, row in df.iterrows()]
all_rows.extend(rows)
# Calculate the time taken to generate embeddings
end_time_embeddings = datetime.datetime.now() 
time_taken_embeddings = (end_time_embeddings - start_time_embeddings).total_seconds() / 60
print(f"Time taken for generating embeddings: {time_taken_embeddings} minutes")
# Start the timer for the insert operation
start_time_insert = datetime.datetime.now()
# Set autocommit to False
conn1.setautocommit(False)
# Create a cursor
cursor2 = conn1.cursor()
# Prepare the SQL insert statement
sql = 'INSERT INTO "{0}"."{1}" ( "FILENAME","TEXT", "VECTOR") VALUES ( ?, ?, TO_REAL_VECTOR(?))'.format(SCHEMA_NAME, TABLE_NAME)
cursor2.prepare(sql)
# Execute the prepared statement with the data
cursor2.executemanyprepared(all_rows)
# Commit the transaction
conn1.commit()
# Calculate the time taken to insert rows
end_time_insert = datetime.datetime.now()
time_taken_insert = (end_time_insert - start_time_insert).total_seconds() / 60
print(f" Time taken for inserting rows: {time_taken_insert} minutes")
# Close the cursor
cursor2.close()
