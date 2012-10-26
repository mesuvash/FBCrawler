from gevent import monkey, pool
monkey.patch_all()

from fetchUtils import get_fb_basic_info, get_fb_likes
import ConfigParser
import csv
import os
import sqlite3
import json

def retryOnError(tries=3):
    def funcwrapper(fn):
        def wrapper(self, *args, **kwargs):
            for i in range(tries):
                try:
                    return fn(self, *args, **kwargs)
                except Exception,e:
                    if i == tries - 1:
                        raise e
        return wrapper
    return funcwrapper

class Crawler(object):

    def __init__(self,configfile):
        self.configfile = configfile
        self.__configure()
        self.__configDB()
        self.__configFailedFile("ab")
        
    def __configure(self):
        self.config = ConfigParser.RawConfigParser(allow_no_value=True)
        self.config.read(self.configfile)
        self.source_path = self.config.get("CRAWLER_CONFIG", "source")
        self.pool_size = int(self.config.get("CRAWLER_CONFIG", "pool_size"))
        self.failed_path = self.config.get("CRAWLER_CONFIG", "failed")
        self.database_path = self.config.get("CRAWLER_CONFIG", "db_path")
        self.schema = self.config.get("CRAWLER_CONFIG", "db_schema")
        #self.log_path = self.config.get("CRAWLER_CONFIG", "log")
        # self.logger = getLogger(self.log_path)

    def __configDB(self):
        path_exists = os.path.exists(self.database_path)
        self.conn = sqlite3.connect(self.database_path)
        if not path_exists:
            with open(self.schema, 'r') as f:
                schema = f.read()
            self.conn.executescript(schema)
  
    def __configFailedFile(self,mode="wb"):
        self.failed = open(self.failed_path,mode)

    def __getUserTokenPair(self,source):
        reader = csv.reader(open(source,'rb'))
        for row  in reader:
            row = map(lambda x: x.strip(),row)
            yield row
    
    #retry 3 times on exception
    @retryOnError(3)
    def __scrape_data(self,uid,access_token):
        basic_info = get_fb_basic_info(uid, access_token)
        likes_info = get_fb_likes(uid, access_token,2)
        return basic_info,likes_info 
    
    def scrape(self,uid,access_token):
        try:
            basic_info,likes_info = self.__scrape_data(uid, access_token)
            return True,basic_info,likes_info
        except:
            return False,uid,access_token

    #callback function called after scraping data
    def updateDatabase(self,response):
        result = response.value
        fail = True if result[0] == False else False
        if fail:
            status,uid,access_token = result
            self.failed.write(uid+","+access_token+"\n")
        else:
            print result
            uid = result[1]["id"]
            result = map(lambda y: json.dumps(y),result)
            status,basic_info,likes_info = result
            cursor = self.conn.cursor()
            query = """insert or replace into raw_crawled_data 
                       (uid, basic_info, likes_info) 
                       values (?,?,?)"""
            cursor.execute(query,(uid,basic_info,likes_info))
            self.conn.commit()
        
    def __fetch(self,source):
        self.p = pool.Pool(self.pool_size)
        for uid,token in self.__getUserTokenPair(source):
            response = self.p.spawn(self.scrape,uid,token)
            response.link(self.updateDatabase)
        self.p.join()
        
    def crawl(self):
        self.__fetch(self.source_path)
       
        #attempt to recrawl the failed items
        
        temp_path = "temp_recovery"
        os.rename(self.failed_path, temp_path)
        self.__configFailedFile()
        self.__fetch(temp_path)  
        os.remove(temp_path)

if __name__ == "__main__":
    crawler = Crawler("crawler.cfg")
    crawler.crawl()
