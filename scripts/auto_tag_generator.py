import os
import pandas as pd
from tika import parser
import re
from text_rank import TextRank4Keyword
from text_summary import summarize
from graph_database import update_tags, update_summary


def read_text(f):
    """converts pdf or txt file to string"""
    _, file_extension = os.path.splitext(f)
    if file_extension == '.txt':
        with open(f, encoding="utf8") as reader:
            text = reader.read()
        text = text.replace('\n', ' ')
    elif file_extension == '.pdf':
        raw = parser.from_file(f)
        text = raw['content']
        if text:
            text = text.replace('\n', '')
        else:
            print('No text found')
    else:
        print("Incorrect file extension")
    
    # drop punctuation except periods, apostrophes, and hyphens
    # (note some files use different characters than ASCII apostrophes)
    text = re.sub(r'[()/:"]', " ", text)
    
    return text[:1000000]  # spacy nlp character limit is 1000000


def save_summary_to_db(title, text):
    """summarizes and saves to sheet"""    
    summary = summarize(text)
    if len(summary)>0:
        update_summary(title, summary)
    else:
        print(f'No summary available for {title}')
        update_summary(title, 'No summary available')


def save_tags_to_db(title, text):
    """extracts tags and saves to database"""
    tr4w = TextRank4Keyword()
    tr4w.analyze(text, window_size=8, lower=False)
    keywords = tr4w.get_keywords(30)
    if len(keywords)>0:
        update_tags(title, keywords)
    else:
        print(f'No keywords identified in {title}')
        update_tags(title)
    

# open csv
df = pd.read_csv('data/reports.csv')

# read each file and process
files = df['Filename']

for f in files:  # .iloc[95:]:  # .sample(4):  
    if isinstance(f, str):
        if f in os.listdir('reports'):
            print(f'Processing: {f}')
            filename = os.path.join('reports', f)
            text = read_text(filename)
            save_tags_to_db(f, text)
            save_summary_to_db(f, text)
        else:
            print (f'{f} not found in reports/')
    else:
        print(f'{f} is not a recognized filename')
    