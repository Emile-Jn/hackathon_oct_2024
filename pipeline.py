"""
date: 19/10/2024
author: Emile Johnston

A large part of the code was copy-pasted from sample_code.ipynb
"""

# import libraries
import os
import requests
import PyPDF2
import pandas as pd
from langchain_openai import ChatOpenAI
from langchain_core.documents import Document
from dotenv import load_dotenv

# load openai key
if not load_dotenv():
    raise Exception('Error loading .env file. Make sure to place a valid OPEN_AI_KEY in the .env file.')

# global variables
REPORTS_SAVE_PATH = 'data/sample_reports'

# See https://openai.com/api/pricing/
MODEL = "gpt-4o-mini"


def make_page_list(pdf_name: str):
    """
    Function to extract text from a pdf file
    :param pdf_name: name of the pdf file, as seen in the folder data/sample_reports
    :return: list of pages in the pdf
    """
    with open(os.path.join("data/sample_reports", pdf_name), 'rb') as f:
        reader = PyPDF2.PdfReader(f, strict=False)
        page_list = []
        for page in reader.pages:
            page_list.append(page.extract_text())
    return page_list


def yes_no_question(sentence: str):
    # Load the LLM
    llm = ChatOpenAI(model_name=MODEL, temperature=0, api_key=os.environ["OPENAI_API_KEY"])  # for deterministic outputs
    yes_no = "Only answer with 'yes' or 'no'."
    question1 = "Does this statement or figure say something about the aims, goals, or objectives of the company?"
    question2 = "Does this statement or figure say something about the values or beliefs of the company?"
    question3 = "Does this statement or figure state a hard fact about the company itself?"
    question4 = "Does this statement or figure state a quantified, concrete fact about the company?"

    answers = []
    for q in [question1, question2, question3, question4]:
        response = llm.invoke(sentence + q + yes_no)
        answers.append(response)
    sentence_length = len(sentence.split())
    return answers, sentence_length


def pipeline(pdf_name: str, page_number: int = None):
    """
    Pipeline function to run the entire pipeline
    :param pdf_name: name of the pdf file, as seen in the folder data/sample_reports
    :param page_number: number of the page to process, if None, process all pages
    :return:
    """
    page_list = make_page_list(pdf_name)
    # TODO: add "section" attribute to each page to add context for the model
    #   for example if pages 12-18 are about the company's environmental achievements,
    #   add "section": "environment" to each of those pages.
    all_answers = []
    sentence_lengths = []
    i = 1
    for page in page_list:
        if page_number is not None:
            if i != page_number:
                i += 1
                continue
        sentences = page.split(".")
        for sentence in sentences:
            answers, sentence_length = yes_no_question(sentence)
            all_answers.append(answers)
            sentence_lengths.append(sentence_length)
    df = pd.DataFrame(data=all_answers)
    df["sentence_length"] = sentence_lengths
    # TODO: do some wrangling, stats and visualizations on df
    return df

#%% testing the pipeline
df = pipeline("google-2023-environmental-report.pdf", page_number=37)