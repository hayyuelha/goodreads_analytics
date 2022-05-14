#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May  1 19:50:17 2022

@author: hayyu.hanifah
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

from bs4 import BeautifulSoup
import requests

import pandas as pd
import json
import os

def selenium_find_elements(driver, url, by_id, by_value):
    driver.get(url)
    time.sleep(10)
    if by_id == 'class':
        e_list = driver.find_elements(by=By.CLASS_NAME, value=by_value)
    # TODO: implement find elements by other identifiers
    return e_list

def bs_find_all(url, tag_string, attrs, headers=''):
    if headers == '':
        page_source = requests.get(url).content
    else:
        page_source = requests.get(url, headers=headers).content
    page_soup = BeautifulSoup(page_source, "lxml")
    elements = page_soup.find_all(tag_string, attrs=attrs)
    return elements

def get_dict_from_file(filepath):
    with open(filepath, 'r') as file:
        json_str = file.read()

    json_dict = json.loads(json_str)
    return json_dict

def convert_str_list(row_df,str_col):
    clean_str = row_df[str_col].replace('[','').replace(']','').replace("'","")
    str_list = clean_str.split(", ")
    return str_list

def get_timeline_date(row_df,str_col,substr_timeline):
    current_timelines = row_df[str_col]
    dt_list = []
    for t in current_timelines:
        if substr_timeline in t:
            dt = t.replace(substr_timeline,'').strip()
            dt_list.append(dt)
    return dt_list

def check_is_genre(row_df,str_col,genre_str):
    current_genre_list = row_df[str_col]
    if genre_str in current_genre_list:
        return 1
    else:
        return 0
    
def exclude_genre(row_df,str_col,genre_str):
    current_genre_list = row_df[str_col]
    genre = [x for x in current_genre_list if x != genre_str]
    return genre

# LOAD PARAMETERS FILE
working_dir_path = os.environ['CONDA_PREFIX']
param = get_dict_from_file(os.path.join(working_dir_path,'parameters.json'))

# Setup Selenium
s = Service(param['chromedriver_path'])
driver = webdriver.Chrome(service=s)

# Get the list of books with public highlights
highlight_lp_url = param['highlight_lp_url']
book_list = selenium_find_elements(driver, highlight_lp_url, 'class', 'annotatedBookItem__knhLink')
print(len(book_list))

highlight_dict = dict()

for l in book_list:
    # For each book, get the list of hightlighted sentences
    current_h_link = l.get_attribute("href")
    print(current_h_link)
    highlight_list = bs_find_all(current_h_link, 'div', attrs={"class":"noteHighlightTextContainer__highlightText"})
    hl_text_list = []
    
    for hl in highlight_list:
        print(hl.find('span').text)
        hl_text_list.append(hl.find('span').text)
    
    # highlight_dict[current_h_link] = hl_text_list
    highlight_dict[l] = hl_text_list
    
print(highlight_dict)
with open(param['highlight_filepath'], 'w') as convert_file:
      convert_file.write(json.dumps(highlight_dict))

# Get the top shelves of each book from Genre section
options = Options()
options.headless = True
book_driver = webdriver.Chrome(service=s,options=options)
executor_url = book_driver.command_executor._url
session_id = book_driver.session_id

print(session_id)
print(executor_url)

book_df = pd.read_csv(param['gr_library_export_filepath'])
book_id_list = book_df['Book Id'].tolist()
url_prefix = 'https://www.goodreads.com/book/show/'

books_dict = dict()
for bid in book_id_list[100:312]:  ## crawl the genre in batches
    print(bid)
    current_href = url_prefix + str(bid)
    book_driver.get(current_href)
    time.sleep(7)
    parent = book_driver.current_window_handle
    uselessWindows = book_driver.window_handles
    for winId in uselessWindows:
        if winId != parent: 
            book_driver.switch_to.window(winId)
            book_driver.close()
            
    book_soup = BeautifulSoup(book_driver.page_source, "html.parser")
    genre_list = book_soup.find_all('div',attrs={'class':'elementList'})
    print([x.find('a').text for x in genre_list])
    books_dict[str(bid)] = [x.find('a').text for x in genre_list]

with open(param['genre_filepath_3'], 'w') as convert_file:
      convert_file.write(json.dumps(books_dict))

# Concat book genre files
genre_1 = get_dict_from_file(param['genre_filepath_1'])
genre_2 = get_dict_from_file(param['genre_filepath_2'])
genre_3 = get_dict_from_file(param['genre_filepath_3'])

genre_1.update(genre_2) # it is safe since there are no overlap keys between 2 dicts
genre_1.update(genre_3)

print(len(genre_1))
print(genre_1)

book_id_list = [k for k,v in genre_1.items()]
book_genre_list = [v for k,v in genre_1.items()]

genre_df = pd.DataFrame.from_dict({'book_id': book_id_list, 'book_genre': book_genre_list})

def clean_genre_list(row_df, genre_col):
    raw_list = [x for x in row_df[genre_col] if x != '']
    return sorted(set(raw_list), key=raw_list.index)

genre_df['clean_genre_list'] = genre_df.apply(lambda r: clean_genre_list(r, 'book_genre'), axis=1)
    
genre_df.to_csv(param['clean_genre_filepath'],index=False)

# Get book timeline details 
## Get review list, to get the link to review detail pages
review_driver = webdriver.Chrome(service=s)
review_driver.get(param['review_lp_url'])
time.sleep(7)
parent = book_driver.current_window_handle
uselessWindows = book_driver.window_handles
for winId in uselessWindows:
    if winId != parent: 
        book_driver.switch_to.window(winId)
        book_driver.close()
for i in range(15): # simulate scroll, to load all the review items
    review_driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(4)

review_soup = BeautifulSoup(review_driver.page_source, "html.parser")
review_list = review_soup.find_all('td',attrs={'class':'field actions'})
review_link_list = [x.find('a').attrs['href'] for x in review_list]

print(review_link_list)

review_url_prefix = 'https://www.goodreads.com'
timeline_dict = dict()
for r in review_link_list:
    book_driver.get(review_url_prefix+r)
    time.sleep(7)
    parent = book_driver.current_window_handle
    uselessWindows = book_driver.window_handles
    for winId in uselessWindows:
        if winId != parent: 
            book_driver.switch_to.window(winId)
            book_driver.close()
    
    book_soup = BeautifulSoup(book_driver.page_source, "html.parser")
    book_title = book_soup.find('h1').text.replace("Hayyu Hanifah's Reviews > ","")
    book_timeline = book_soup.find_all('div', attrs={'class':'readingTimeline__text'})
    book_timeline_list = [x.text.strip().replace('\n',' ') for x in book_timeline]
    timeline_dict[book_title] = book_timeline_list
    
print(timeline_dict)
with open(param['timeline_filepath'], 'w') as convert_file:
      convert_file.write(json.dumps(timeline_dict))

### CONSOLIDATE ALL DATASET
goodreads_lib_export = pd.read_csv(param['gr_library_export_filepath'])
book_genre_df = pd.read_csv(param['clean_genre_filepath'])
timeline = get_dict_from_file(param['timeline_filepath'])

consolidate_df = goodreads_lib_export.merge(book_genre_df, how='left', left_on='Book Id', right_on='book_id')
consolidate_df.drop(columns=['book_id', 'book_genre'],inplace=True)

consolidate_df['date_read'] = pd.to_datetime(consolidate_df['Date Read'])
consolidate_df['date_added'] = pd.to_datetime(consolidate_df['Date Added'])
consolidate_df['Title_shorten'] = consolidate_df.apply(lambda x: x['Title'].split(" (")[0].strip() if x['Title'].endswith(")") else x['Title'].strip(), axis=1)

book_title = [k for k,v in timeline.items()]
timelines = [v for k,v in timeline.items()]
book_timeline_df = pd.DataFrame(data={'book_title': book_title, 'timelines': timelines})
book_timeline_df['add_to_tbr'] = book_timeline_df.apply(lambda x: get_timeline_date(x,'timelines','– Shelved as: to-read'), axis=1)
book_timeline_df['start_reading'] = book_timeline_df.apply(lambda x: get_timeline_date(x,'timelines','–  Started Reading'), axis=1)
book_timeline_df['finish_reading'] = book_timeline_df.apply(lambda x: get_timeline_date(x,'timelines','–  Finished Reading'), axis=1)

book_timeline_df['add_to_tbr_dt_len'] = book_timeline_df.apply(lambda x: len(x['add_to_tbr']),axis=1)
book_timeline_df['start_reading_dt_len'] = book_timeline_df.apply(lambda x: len(x['start_reading']),axis=1)
book_timeline_df['finish_reading_dt_len'] = book_timeline_df.apply(lambda x: len(x['finish_reading']),axis=1)

book_timeline_df[book_timeline_df['finish_reading_dt_len'] > 1]

# df.A.map(lambda x: x[0])
book_timeline_df['add_to_tbr_dt'] = book_timeline_df.add_to_tbr.map(lambda x: x[0] if len(x) == 1 else '')
book_timeline_df['start_reading_dt'] = book_timeline_df.start_reading.map(lambda x: x[0] if len(x) == 1 else '')
book_timeline_df['finish_reading_dt'] = book_timeline_df.finish_reading.map(lambda x: x[0] if len(x) == 1 else '')

book_timeline_df.drop(columns=['add_to_tbr','start_reading','finish_reading','add_to_tbr_dt_len','start_reading_dt_len','finish_reading_dt_len'],inplace=True)

consolidate_df = consolidate_df.merge(book_timeline_df, how='left', left_on='Title_shorten', right_on='book_title')

consolidate_df['add_to_tbr_dt'] = pd.to_datetime(consolidate_df['add_to_tbr_dt'], infer_datetime_format=True)
consolidate_df['start_reading_dt'] = pd.to_datetime(consolidate_df['start_reading_dt'], infer_datetime_format=True)
consolidate_df['finish_reading_dt'] = pd.to_datetime(consolidate_df['finish_reading_dt'], infer_datetime_format=True)

consolidate_df.dropna(axis=1, how='all', inplace=True) # drop all columns which only consist of NaN value

consolidate_df['genre_list'] = consolidate_df.apply(lambda x: convert_str_list(x,'clean_genre_list'), axis=1)

consolidate_df['is_nonfiction'] = consolidate_df.apply(lambda x: check_is_genre(x,'genre_list','Nonfiction'), axis=1)
consolidate_df['is_fiction'] = consolidate_df.apply(lambda x: check_is_genre(x,'genre_list','Fiction'), axis=1)

consolidate_df['genre_list_trf'] = consolidate_df.apply(lambda x: exclude_genre(x,'genre_list','Nonfiction'), axis=1)
consolidate_df['genre_list_trf'] = consolidate_df.apply(lambda x: exclude_genre(x,'genre_list_trf','Fiction'), axis=1)

consolidate_df['year_read'], consolidate_df['month_read'] = consolidate_df['date_read'].dt.year, consolidate_df['date_read'].dt.month
consolidate_df['year_added'], consolidate_df['month_added'] = consolidate_df['date_added'].dt.year, consolidate_df['date_added'].dt.month

consolidate_df.to_csv(param['consolidated_data_filepath'], index=False)

