"""In this scenario, we show how we could use "Azure Open AI" to retrieve embedded response from SAP HANA Cloud Vector.
   WE use two of the foundation models. Based on the use prompt, we use the "embedding model" to convert the user prompt
   to embedding. We use COSINE SIMILARITY to retrieve the closest embedding from HANA DB. Then the corresponding
   text is retrieved along with source file , actual text and Scoring.    
   Then we provide the retrieved text as input to "text-davinci-003" model to determine the sentiment of the text.
    Please install the necessary packages 
    pip install   generative-ai-hub-sdk ||hdbcli || hana_ml || python-dotenv || shapely  || openai
"""
#In this scenario we are using Azure OpenAI directly instead of GenAIHub
import openai 
from openai import AzureOpenAI
from  hdbcli import dbapi
import pandas as pd
import hana_ml.dataframe as dataframe
import os
from dotenv import load_dotenv
load_dotenv()
# provide the credentials to connect to HANA Cloud DB
HANA_USER_VDB = os.getenv('HANA_USER_VDB')
HANA_PASSWORD_VDB = os.getenv('HANA_PASSWORD_VDB')
HANA_HOST = os.getenv('HANA_HOST_VECTOR')
HANA_USER = os.getenv('HANA_VECTOR_USER') 
HANA_PASSWD = os.getenv('HANA_VECTOR_PASS') 
# Establish connections
conn = dataframe.ConnectionContext(
    address= HANA_HOST,             
    port=443,
    user=HANA_USER,
    password=HANA_PASSWD,
    encrypt='true'
)
conn1 = dbapi.connect( 
    address=HANA_HOST,
    port=443, 
    user=HANA_USER, 
    password=HANA_PASSWD   
)
#Set the Azure OpenAI keys 
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_DEPLOYMENT_ENDPOINT = os.getenv("OPENAI_EMBEDDING_ENDPOINT")
OPENAI_DEPLOYMENT_VERSION = os.getenv("OPENAI_DEPLOYMENT_VERSION")
openai.api_type = "azure"
openai.api_version = OPENAI_DEPLOYMENT_VERSION
openai.api_base = OPENAI_DEPLOYMENT_ENDPOINT
openai.api_key = OPENAI_API_KEY
#initiate the client to use AzureOpenAI for embedding and completion
client = AzureOpenAI(
  api_key = OPENAI_API_KEY ,  
  api_version = OPENAI_DEPLOYMENT_VERSION,
  azure_endpoint = OPENAI_DEPLOYMENT_ENDPOINT
)

#Here is the User Prompt. Change it  to query against the text that was ingested
prompt = "What are the reviews about Tacos?"
#Here we convert your input to vector using the Azure ada embedding model
res = client.embeddings.create(input=prompt, model="t4sap") #t4sap is the deployment name I setup in Azure portal for embedding model
query_vector = res.data[0].embedding
# we query the DB with the embedded response from user prompt
sql = '''SELECT TOP {k}  "FILENAME","TEXT" , TO_NVARCHAR("VECTOR") AS VECTOR_STR ,"{metric}"("VECTOR", TO_REAL_VECTOR('{qv}')) as SCORING
                  FROM "VECTOR_DEMO"."REVIEWS_TARGET"  
                  ORDER BY "{metric}"("VECTOR", TO_REAL_VECTOR('{qv}')) {sort}'''.format(k=10, metric="COSINE_SIMILARITY", qv=query_vector, sort="DESC")
hdf = conn.sql(sql)
res = hdf.head(10).collect() 
if not res.empty:
    db_results = [(row['FILENAME'],row['TEXT'], row['SCORING']) for _, row in res.iterrows()]
    new_results = []
    for i in range(len(db_results)):
        if i < len(db_results):
            filename, text,  scoring = db_results[i]
            #we are  getting the sentiment for every text using the below prompt
            sentiment_prompt = f"Provide sentiment in exactly one word for the: '{text}'"            
            #in order to get the prompt we call the falcon model from aicore config
            sentiment_output = client.completions.create(model="ai4sap", prompt=sentiment_prompt)#ai4sap is the model name for text-davinci-003
            sentiment = sentiment_output.choices[0].text.strip()
            new_tuple =  (filename,text, scoring, sentiment)
            new_results.append(new_tuple) 
#transform the results to DF and check the output                      
df_new_results = pd.DataFrame(new_results)
print(df_new_results)
