Crawler for collecting information of Facebook App users

Dependencies:
	gevent 0.13.8

Description
	Crawler expects the userid and corresponding access_token in CSV format. Crawler crawls information of "n" users concurrently as specified by pool_size in crawler.cfg.


Configuration File (crawler.cfg)
	source => path of the csv file containing userid, access_token information
	pool_size => specifies the total number of concurrent user fetch at a time
	db_path => path to database to store fetched data
	db_schema => schema of database
	failed => path of file to store the information of user whose information couldnt be collected by crawler

	