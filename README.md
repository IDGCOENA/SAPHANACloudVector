# SAPHANACloudVector
THis code repository contains the python scripts for different scenarios discussed in Discovery Mission "Harnessing Generative AI Capabilities with SAP HANA Cloud Vector Engine"

# Vector_Discovery_Mission

**Pre-requisites:**

1. SAP Generative Hub subscription has been set up and have the AICORE tokens stored locally. If not, please follow these steps for:
   - [Initial setup](https://help.sap.com/docs/ai-launchpad/sap-ai-launchpad/initial-setup?q=generative%20ai%20hub) 
   - Setting up [roles](https://help.sap.com/docs/ai-launchpad/sap-ai-launchpad/activate-generative-ai-hub-for-sap-ai-launchpad?q=generative%20ai%20hub&locale=en-US)
   
   
2. If you are **NOT** using GenAI Hub, you can also use set up Azure Open AI service /Open AI and execute the scripts. Please refer the "SET UP" Tiles in the Discovery      Mission for additional information.
                     
3. SAP HANA CLoud Instance has been set up by following these [steps](https://developers.sap.com/tutorials/hana-cloud-deploying.html).

4. Local local python environment has been set up or use [Google Colabs](https://colab.research.google.com/) to execute the python scripts.
5. Install the Python Package for [Generative AI Hub - SDK](https://pypi.org/project/generative-ai-hub-sdk/). Additional Python packages include "hdbcli", "hana_ml",        "datetime", "tiktoken", "python-dotenv", "shapely".
6. If you are using GenAI hub, configure the ai-core-sdk using the ai-core instance keys. If you are using Microsoft Visual Studio, then you can execute "aicore            configure" from terminal. Incase you are using Google Colab, you can set up using 
* os.environ['AICORE_AUTH_URL'] = 'https://*************.authentication.eu10.hana.ondemand.com'
* os.environ['AICORE_CLIENT_ID'] = 'sb-************************'
* os.environ['AICORE_RESOURCE_GROUP'] = 'default'
* os.environ['AICORE_CLIENT_SECRET'] = 'df********************************GfCt1g='
* os.environ['AICORE_BASE_URL'] = 'https://******************entral-1.aws.ml.hana.ondemand.com/v2'
* os.environ['HANA_VECTOR_USER'] = 'XXXXXXXXXX'   --> Your SAP HANA Cloud User
* os.environ['HANA_VECTOR_PASS'] = 'XXXXXXXXXXXXXXX' --> Your SAP HANA Cloud password 
* os.environ['HANA_HOST_VECTOR'] = 'XXXXXXXXXXXXXXXXXXXXX-eu10.hanacloud.ondemand.com'   --> Your SAP HANA Cloud host          
8. Install the python packages as mentioned in the Python Scripts
9. Setting up the .env file so you dont have to harcode the credentials for accessing SAP HANA Cloud(Optional)


**Executing the Python Scripts**
           
1. There are 6 scenarios for python scripts provided as mentioned in the Implementation Review of the Discovery Mission. For executing scenarios [1,2,4,5], you need to setup up SAP HANA Cloud and SAP GenAI HuB
2. For executing scenarios 3 and 6, you need to setup up SAP HANA Cloud and Azure OpenAI/OpenAI
3. For Scenario 7 which is the CAP app for RAG based, the code is provided both for how to execute using GenAI Hub or Azure OpenAI.


| Scenarios | Description | GenAI Hub + SAP HANA Cloud  |  AzureOpenAI/Open AI +SAP HANA Cloud
| :---         |     :---:      |          ---: |           ---:
| Scenario1    | Using Python, extract the reviews from the Document Store or the table. Then, apply the embedding models from SAP Generative AI Hub to process these reviews. After processing, load the embeddings into  SAP HANA Cloud.|  X  | 
| Scenario2     | Utilizing Python, retrieve the reviews from either the Document Store or the table. Subsequently, employ the embedding models from SAP Generative AI Hub to embed these reviews. Finally, using the langchain plugin provided by SAP, ingest the embedded reviews into the SAP HANA Cloud. | X     |
| Scenario3    | Using Python, extract the reviews from the Document Store or the specified table. Apply the embedding models from Azure Open AI/Open AI to process these reviews. Once processed, use the langchain plugin provided by SAP to ingest the embeddings into the SAP HANA Cloud.|    |  X
| Scenario4    | Utilizing Python, retrieve the reviews from either the Document Store or the table. Subsequently, employ the embedding models from SAP Generative AI Hub to embed these reviews. Finally, using the standard langchain interface, ingest the embedded reviews into the SAP HANA Cloud.|  X  |  
| Scenario5   | Execute a Python script that performs a similarity search to verify the ingested data. This script uses the large language models from SAP Generative AI Hub and checks the user prompt in the SAP HANA Cloud.|   X |  
| Scenario6   | Execute a Python script that performs a similarity search to verify the ingested data. This script uses the large language models from Azure OpenAI/OpenAI and checks the user prompt in the SAP HANA Cloud.|    |  X
| Scenario7    | Retrieval augmented generation (RAG) Application based on SAP CAP to test ingested data from Scenarios 1-4|  X  |  X




4. Please make sure you have access to Large Language Models(LLM) either through 1.GenAI Hub or 2.Azure OpenAI or 3.OpenAI.
5. In order to set up the LLM access, please refer the SetUp section of the mission.
6. Please make sure you import the schema provided as part of the mission. It is available as part of SetUp section under the tile "Setup Data Access for Embedding"
7. Once the SAP HANA Cloud, access to LLM, and Schema, you can execute the scripts seamlessly. 

