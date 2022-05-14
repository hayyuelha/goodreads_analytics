# -*- coding: utf-8 -*-
"""
Goodreads Analytics

AUTHOR: Hayyu Hanifah

An interactive dashboard to display Goodreads data. Built using Streamlit.

Metrics:
    1. Number of books read (overall, breakdown by fiction/non-fiction, by genre)
    2. Number of page read (overall, breakdown by fiction/non-fiction, by genre)
    3. Number of books added to TBR (overall, breakdown by fiction/non-fiction, by genre)
    4. Reading velocity over the year (what month I read the most, what genre)
    5. Highlights -> cloud of words (to get the vibes of what interest me the most)
    6. My ratings (overall and per month); my rating vs overall rating of the book (is it usually similar, higher, or lower)
    
Features:
    1. Data visualization using plotly (+ filtering)
    2. Upload data (to enable others if they want to visualize their Goodreads data)
    3. Crawling Goodreads to get the book info (genre, highlights)
    4. Recommend books to read
    
TODO:
    1. Data transformation (make sure date type of date read, date added; numeric and string types)
    2. Get the highlights of read books (from kindle highlight, need to learn about selenium) -> should be separated from the main streamlit app, since it needs credentials 
    3. Visualisation (create scorecards, bar charts, line charts, pie charts, word cloud)
    
"""

import pandas as pd 
import numpy as np 
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
from datetime import datetime

### FUNCTIONS



### STREAMLIT
main_df = pd.read_csv('/Users/hayyu.hanifah/Documents/GitHub/goodreads_analytics/book_data_consolidated_fin.csv')

# Data Preparation
main_df['date_read'] = pd.to_datetime(main_df['date_read'])
main_df['date_added'] = pd.to_datetime(main_df['date_added'])
main_df['add_to_tbr_dt'] = pd.to_datetime(main_df['add_to_tbr_dt'])
main_df['start_reading_dt'] = pd.to_datetime(main_df['start_reading_dt'])
main_df['finish_reading_dt'] = pd.to_datetime(main_df['finish_reading_dt'])

main_df.dtypes

