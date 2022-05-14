#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May  1 22:25:45 2022

@author: hayyu.hanifah
"""

# Import scrapy
import scrapy

# Import the CrawlerProcess
from scrapy.crawler import CrawlerProcess

# Create the Spider class
class YourSpider(scrapy.Spider):
  name = 'yourspider'
  # start_requests method
  def start_requests( self ):
    url_short = "https://www.goodreads.com/notes/38648728-hayyu-hanifah"
    yield scrapy.Request(url = url_short, callback=self.parse)
      
  def parse(self, response):
    # Get the link to the highlight items of each book
    book_link_list = response.xpath('//a[@class="annotatedBookItem__knhLink")]/@href/text()').extract()
    print(len(book_link_list))
    for bl in book_link_list:
      yield response.follow(url = bl, callback = self.parse_highlight)
  
  def parse_highlight(self, response):
    highlight_url = response.url
    print(highlight_url)
    highlight_list = response.xpath('//div[@class="noteHighlightTextContainer__highlightText"]/span/text()').extract()
    print(len(highlight_list))
    gr_dict[highlight_url] = highlight_list
    
# Initialize the dictionary **outside** of the Spider class
gr_dict = dict()

# Run the Spider
process = CrawlerProcess()
process.crawl(YourSpider)
process.start()

# Print a preview of courses
print(gr_dict)

test_response = scrapy.Request(url = "https://www.goodreads.com/notes/38648728-hayyu-hanifah")._get_body()
print(test_response.url)
book_link_list = test_response.xpath('//a[contains(@class,"annotatedBookItem__knhLink")]/@href/text()').extract()
print(len(book_link_list))
for bl in book_link_list:
  highlight_response = test_response.follow(url = bl)
  highlight_url = highlight_response.url
  print(highlight_url)
  highlight_list = highlight_response.xpath('//div[@class="noteHighlightTextContainer__highlightText"]/span/text()').extract()
  print(len(highlight_list))
  