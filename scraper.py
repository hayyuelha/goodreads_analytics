#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May  5 20:12:04 2022

@author: hayyu.hanifah
"""

import time

from bs4 import BeautifulSoup
import requests

import pandas as pd
import json

page_source = requests.get("https://www.goodreads.com/notes/38648728-hayyu-hanifah")
time.sleep(15) # waiting the page to load completely
page_content = BeautifulSoup(page_source.content, "lxml")
book_list = page_content.find_all('a', attrs={"class":"annotatedBookItem__knhLink"})

print(len(book_list))
for bl in book_list:
    print(bl.text)

