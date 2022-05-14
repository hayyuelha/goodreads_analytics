#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May  2 10:04:43 2022

@author: hayyu.hanifah
"""

from bs4 import BeautifulSoup
import requests
from lxml import etree


url = "https://www.goodreads.com/notes/38648728-hayyu-hanifah"
soup = BeautifulSoup(requests.get(url).content, "lxml")
dom = etree.HTML(str(soup))
# print(dom)
cek = dom.xpath('/html/body/div[1]/div[3]/div[1]/div[1]/div[2]/div/div/div/div[2]/div/div[2]')
print(cek)
# book_page_html = soup.find_all('a', class_="annotatedBookItem__knhLink") #class_="annotatedBookItem__knhLink"

# book_page_html = soup.select("a.annotatedBookItem__knhLink")

# annot = book_page_html.find('a', class_=True, recursive=True)
# annot_list = [x for x in annot if x.attrs['class'] == "annotatedBookItem__knhLink"]
# urls = [x['href'] for x in links]
# print(urls)
# print(links)

# classes = [value 
#             for element in annot 
#             for value in element["class"]]
# print(classes)

# print(book_page_html)
# annot[10].attrs['class']

# print(annot)