#!/usr/bin/env python
# -*- coding: utf-8 -*-
from selenium import webdriver
from time import sleep
from lxml import etree
from datetime import datetime
from pymongo import MongoClient
from subprocess import call

#the connection to the MongoDB using pymongo library
db_client = MongoClient('localhost',27017)

#specify the data base name which one you would like to create
#if you choose to change the name of DB here then it should be changed in the node.js app file too.
db = db_client['scrape_data'] 

#specify the collection name to create and store your records
#if you choose to change the name of collection then it should be changed in the  node.js app file too.
collection = db['Data_Collection']

#you need to provide the chrome driver path to  bring up the chrome window
response = webdriver.Chrome() 

#start url for the website to be scraped
response.get("https://www.macys.com/?cm_sp=navigation-_-top_nav-_-macys_icon")

#maximizing the chrome window to properly geting the information available on the pagee
response.maximize_window()

# if there is a popup message then it needs to be closed inorder to  click the other elements
pop_up_close_button = response.find_elements_by_xpath('//div[@id="tinybox"]//a[@id="closeButton"]')
if pop_up_close_button:
	try:
		pop_up_close_button[0].click()
		sleep(1)
	except:
		pass

#selecting the  home department from the top navigation menu and clicking it
home_department_link = response.find_elements_by_xpath('//div[@id="mainNavigation"]/ul/li/a[contains(text(),"HOME")]')
if home_department_link:
	home_department_link[0].click()
	sleep(5)

#selecting and  clicking the home decor department from the sub department list in the left side
home_decor_link = response.find_elements_by_xpath('//div[@id="localNavigationContainer"]//ul[@id="firstNavSubCat"]/li//a[contains(text(),"Home Decor")]')
if home_decor_link:
	home_decor_link[0].click()
	sleep(5)

#going to each pages using the next page button and collecting all the data
next_page = response.find_elements_by_xpath('//div[@id="filters"]//a[@class="arrowRight arrowButton paginationSpacer"]')
while next_page:
	#converting the source code into an object for effectively parsing all the html content
	parser = etree.HTML(response.page_source)

	#collecting all the products into a list and going through each one to collect name and price
	all_products_listed =  parser.xpath('//div[@id="macysGlobalLayout"]//ul[@id="thumbnails"]/li[@class="productThumbnail borderless"]')
	for product in all_products_listed:
		name = product.xpath('.//div[@class="shortDescription"]//a[@class="productThumbnailLink "]/text()')
		price = product.xpath('.//div[@class="prices"]//span[@class="first-range "]/text()')
		name = ''.join(name).strip()
		price = ''.join(price).strip().replace('$','')
		scrapeDate = datetime.today().strftime('%Y-%m-%d')
		data = {"Product_Name":name,"Price":price,"ScrapeDate":scrapeDate}
		if name:
			#inserting data into the mongodb collections, one at a time
			insert_data = collection.insert_one(data).inserted_id
		else:
			print "data is not a valid one"
	#checking if there is a next page exist or not. if there  is one then going to that page by clicking the next button		
	next_page = response.find_elements_by_xpath('//div[@id="filters"]//a[@class="arrowRight arrowButton paginationSpacer"]')
	if next_page:
		next_page[0].click()
		sleep(5)
#closing the database connetion
db_client.close()
#clocing the browser window
response.close()

#calling the node.js app which listens to the port 3000 and returns all the data from mongodb database
#I used ubuntu and nodejs was the package name  in ubuntu, if you are on mac or windows it will be "node web_application.js"
call('nodejs web_application.js',shell = True)