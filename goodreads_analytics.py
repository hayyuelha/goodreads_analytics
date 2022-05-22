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
# import scipy
import plotly.graph_objects as go
import plotly.express as px
import plotly.figure_factory as ff
from plotly.subplots import make_subplots
import streamlit as st
from datetime import datetime
import json
import os
import warnings
warnings.filterwarnings('ignore') ## to avoid error with keyerror 'warnings'

### FUNCTIONS
def get_dict_from_file(filepath):
    with open(filepath, 'r') as file:
        json_str = file.read()

    json_dict = json.loads(json_str)
    return json_dict

def plot_ratings_vis(df):
    avg_myrating = df['My Rating'].mean()
    hist_average_rating = [df['Average Rating'].tolist()]
    group_labels = ['Overall Average Rating']
    fig = make_subplots(rows=2, cols=1, row_heights=[0.2,0.8],
                                    specs=[[{'type':'domain'}], [{}]],
                                    subplot_titles=("My Average Rating","Average Rating Distribution")
                                    )
    fig.add_trace(go.Indicator(
        mode = "number",
        value = avg_myrating,
        domain = {'row': 0, 'column': 0}), 1, 1)

    dist_rating = ff.create_distplot(hist_average_rating, group_labels, bin_size=[.1], show_rug=False)
    fig.add_trace(
            go.Histogram(dist_rating.data[0]),
            2, 1
        )
    fig.add_trace(
            go.Scatter(dist_rating.data[1]),
            2, 1
        )
    
    return fig


### STREAMLIT
working_dir_path = os.environ['CONDA_PREFIX']
param = get_dict_from_file(os.path.join(working_dir_path,'parameters.json'))

@st.cache
def load_data(param):
    """ Loads in 4 dataframes and does light feature engineering"""
    df = pd.read_csv(param['consolidated_data_filepath'])
    
    # Data Preparation
    date_cols = ['date_read','date_added','add_to_tbr_dt','start_reading_dt','finish_reading_dt']
    for c in date_cols:
        df[c] = pd.to_datetime(df[c])
    
    df['add_to_tbr_dt'] = df.apply(lambda x: x['date_added'] if pd.isna(x['add_to_tbr_dt']) else x['add_to_tbr_dt'], axis=1)
    df['wtr_to_start_read'] = (df['start_reading_dt'] - df['add_to_tbr_dt']).dt.days
    df['start_to_finish_read'] = (df['date_read'] - df['start_reading_dt']).dt.days
    return df

# Data Aggregation
main_df = load_data(param)

## Conditions
null_date_read = main_df['date_read'].isna()
null_date_start = main_df['start_reading_dt'].isna()
fiction = (main_df['is_fiction'] == 1)
nonfiction = (main_df['is_nonfiction'] == 1)
unknown_category = (main_df['is_fiction'] == 0) & (main_df['is_nonfiction'] == 0)
# read = (main_df['Exclusive Shelf'] == 'read') | (main_df['Read Count'] > 0)
read = (main_df['Exclusive Shelf'] == 'read')
have_rating = main_df['My Rating'] != 0

## Overall
total_books = main_df['Book Id'].nunique()
total_books_read = main_df[~null_date_read | read]['Book Id'].nunique()
total_books_inprogress = main_df[(~null_date_start) & (null_date_read)]['Book Id'].nunique()

### Fiction
total_books_fic = main_df[fiction]['Book Id'].nunique()
total_books_read_fic = main_df[(~null_date_read | read) & fiction]['Book Id'].nunique()
total_books_inprogress_fic = main_df[(~null_date_start) & (null_date_read) & fiction]['Book Id'].nunique()

### Non Fiction
total_books_nonfic = main_df[nonfiction]['Book Id'].nunique()
total_books_read_nonfic = main_df[(~null_date_read) & nonfiction]['Book Id'].nunique()
total_books_inprogress_nonfic = main_df[(~null_date_start) & (null_date_read) & nonfiction]['Book Id'].nunique()

### Unknown Category
total_books_unknown = main_df[unknown_category]['Book Id'].nunique()
total_books_read_unknown = main_df[(~null_date_read) & unknown_category]['Book Id'].nunique()
total_books_inprogress_unknown = main_df[(~null_date_start) & (null_date_read) & unknown_category]['Book Id'].nunique()

overall_by_category = pd.DataFrame(
                        data={
                                "category": ['fiction','non-fiction','unknown'],
                                "total_books": [total_books_fic, total_books_nonfic, total_books_unknown],
                                "total_books_read": [total_books_read_fic, total_books_read_nonfic, total_books_read_unknown],
                                "total_books_inprogress": [total_books_inprogress_fic, total_books_inprogress_nonfic, total_books_inprogress_unknown]
                            }
    )


## Yearly


## Monthly


# Visualization
st.title("Goodreads Analytics")
st.markdown("""
            ## Overview
            Total number of books on my shelves as per 1 May 2022, how many have been read,
            and how many still not finish reading.
            """)
labels = overall_by_category['category']
colors = px.colors.qualitative.Pastel
fig_total_books = make_subplots(rows=1, cols=3, 
                                subplot_titles=("Total Books","Read","In Progress"),
                                specs=[[{'type':'domain'}, {'type':'domain'}, {'type':'domain'}]],
                                
                                )
fig_total_books.add_trace(go.Pie(labels=labels, values=overall_by_category['total_books'], 
                                 name="Total Books",
                                 insidetextorientation='horizontal'
                                 ), 
                          1, 1)
fig_total_books.add_trace(go.Pie(labels=labels, values=overall_by_category['total_books_read'], 
                                 name="Books Read",
                                 insidetextorientation='horizontal'
                                 ), 
                          1, 2)
fig_total_books.add_trace(go.Pie(labels=labels, values=overall_by_category['total_books_inprogress'], 
                                 name="Books In Progress",
                                 insidetextorientation='horizontal'
                                 ), 
                          1, 3)
fig_total_books.update_traces(hole=.52, 
                              hoverinfo="label+percent+value",
                              marker=dict(colors=colors[2:5])
                              )

## Tricks to find the coordinate for center annotations
# coord_annot = []
# for p in list(np.arange(start=0, stop=1.1, step=0.1)):
#     current_step = "{:.1f}".format(p)
#     coord_annot.append(dict(text=current_step, x=p, y=0, font_size=15, showarrow=False))
#     coord_annot.append(dict(text=current_step, x=0, y=p, font_size=15, showarrow=False))
    
# donut_existing_annot += coord_annot

donut_center_annot = [
        dict(text=str(total_books), x=0.103, y=0.53, font_size=27, showarrow=False),
        dict(text="books", x=0.103, y=0.43, font_size=15, showarrow=False),
        dict(text=str(total_books_read), x=0.5, y=0.53, font_size=27, showarrow=False),
        dict(text="books", x=0.5, y=0.43, font_size=15, showarrow=False),
        dict(text=str(total_books_inprogress), x=0.885, y=0.53, font_size=27, showarrow=False),
        dict(text="books", x=0.895, y=0.43, font_size=15, showarrow=False)
    ]

donut_existing_annot = [a.to_plotly_json() for a in fig_total_books["layout"]["annotations"]]
donut_existing_annot += donut_center_annot # so the center annot and subplot title not override each other

fig_total_books.update_layout(
        annotations=donut_existing_annot,
        legend=dict(yanchor="middle",y=0.5),
        margin=dict(l=3, r=3, t=0, b=3),
        autosize=False,
        height=250
    )
st.plotly_chart(fig_total_books)

## Overview of My Rating vs Average Rating per books
## TODO: improve the readability, change height / implement filter; change color
st.markdown("""
            ## Ratings
            Usually I only pick books with minimum rating 3.5 
            """)

rating_df = main_df[(~null_date_read | read) & (have_rating)] 
rating_df['abs_diff_rating'] = rating_df.apply(lambda x: abs(x['My Rating'] - x['Average Rating']), axis=1)
rating_df.sort_values(by=['My Rating','abs_diff_rating'],ascending=[False,False],inplace=True,ignore_index=True)            

fig_rating = px.scatter(rating_df, x=['Average Rating','My Rating'], y='Title', labels={'variable':'Rating'})
for i in range(len(rating_df)):
    fig_rating.add_shape(
            type='line',
            x0=rating_df['My Rating'].iloc[i], y0=rating_df['Title'].iloc[i],
            x1=rating_df['Average Rating'].iloc[i], y1=rating_df['Title'].iloc[i],
            line_color="#cccccc"
        )
fig_rating.update_xaxes(showgrid=True, gridwidth=0.3)
fig_rating.update_yaxes(showgrid=False)
st.plotly_chart(fig_rating)


radio_col, vis_rating_col = st.columns([1, 3])

with radio_col:
    category = st.radio(
         "Category filter",
         ('All', 'Fiction', 'Non-Fiction'))
with vis_rating_col:
    if category == 'All':
        fig_rating_dist = plot_ratings_vis(rating_df)
    elif category == 'Fiction':
        fig_rating_dist = plot_ratings_vis(rating_df[fiction])
    elif category == 'Non-Fiction':
        fig_rating_dist = plot_ratings_vis(rating_df[nonfiction])
    
    st.plotly_chart(fig_rating_dist)

