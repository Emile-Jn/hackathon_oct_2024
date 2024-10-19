"""
This file is just a .py version of sample_code.ipynb.

# AIM Hackathon: Sample code
19.10.2024

Note: This is just some code to help you getting started, but in no way mandatory to use.
Feel free to use any other tools, libraries, approaches, etc.
"""

import os
import requests
import PyPDF2
import pandas as pd
from dotenv import load_dotenv
import psycopg

from langchain_openai import ChatOpenAI
from langchain_core.documents import Document

# load openai key
if not load_dotenv():
    raise Exception('Error loading .env file. Make sure to place a valid OPEN_AI_KEY in the .env file.')

#%%
# TODO set global variables
REPORTS_SAVE_PATH = 'data/sample_reports'
DB_PATH = "data/db/sample.db"

# See https://openai.com/api/pricing/
MODEL = "gpt-4o-mini"

#%%
df = pd.read_json('data/reports.json')
df

#%% Download some reports
# EXAMPLE: select Apple reports
df_sample = df[df['company_name'] == 'Apple']


#%%
# download Apple reports to save_dir
def download_files(df: pd.DataFrame, save_dir: str):
    os.makedirs(save_dir, exist_ok=True)
    for url in df['pdf_url']:
        pdf_filename = os.path.basename(url)
        response = requests.get(url)
        with open(os.path.join(save_dir, pdf_filename), 'wb') as file:
            file.write(response.content)
    print(f"Success.")


download_files(df_sample, REPORTS_SAVE_PATH)


#%% ## Load PDFs as documents
def get_documents_from_path(files_path: str) -> [Document]:
    documents = []

    for file in os.listdir(files_path):
        _, file_extension = os.path.splitext(file)
        text = ""

        if file_extension == ".pdf":
            with open(os.path.join(files_path, file), 'rb') as f:
                reader = PyPDF2.PdfReader(f, strict=False)
                for page in reader.pages:
                    text += page.extract_text() + "\n"

            if text:
                documents.append(Document(page_content=text, metadata={"source": file}))
            else:
                print(f"WARNING: No text extracted from {file}")
        else:
            # TODO: can add support for other file types here
            print(f" WARNING: Unsupported file extension: {file_extension}")

    return documents

documents = get_documents_from_path(REPORTS_SAVE_PATH)

#%% ## Create simple vector database


with psycopg.connect("host=localhost port=5432 dbname=vectordb user=postgres password=") as conn:
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE test (
                id serial PRIMARY KEY,
                num integer,
                data text)
            """)

#%%
# Load the LLM
llm = ChatOpenAI(model_name=MODEL, temperature=0)  # for deterministic outputs

# TODO Load retriever, question answer pipeline, etc.


#%%
def ask_question():
    pass


#%%
response = ask_question("When does Apple try to achieve carbon neutrality?")

