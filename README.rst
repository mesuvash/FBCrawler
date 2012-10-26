Crawler for collecting information of Facebook App users

Dependencies
=============
	gevent 0.13.8

Description
============

	Crawler expects a file in CSV format containing userid and corresponding access_token infromation.
	Crawler fetches information of "n" users concurrently as specified by pool_size in crawler.cfg.


Configuration File (crawler.cfg)
=================================
	source => path of the csv file containing userid and access_token information

	pool_size => specifies the total number users to fetch concurrently

	db_path => path of database to store fetched data

	db_schema => schema of database

	failed => file path to store information of the failed crawl 

	log => log file for the program

Running Crawler
====================
	- Configure the crawler.cfg
	- run "python crawler.py"
	
