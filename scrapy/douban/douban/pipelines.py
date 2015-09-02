# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


import json
from twisted.enterprise import adbapi
from scrapy import log
import MySQLdb
import MySQLdb.cursors


class DoubanPipeline(object):
    
    def __init__(self):
        self.file = open("./books.json", "wb")

    def process_item(self, item, spider):
		# 编码的转换
        for k in item:
            item[k] = item[k].encode("utf8")
        line = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.file.write(line)
        return item


class MySQLPipeline(object):

    def __init__(self):
        self.dbpool = adbapi.ConnectionPool("MySQLdb",
                                           db = "dbname",			# 数据库名
                                           user = "username",   	# 数据库用户名 
                                           passwd = "password", 	# 密码
                                           cursorclass = MySQLdb.cursors.DictCursor, 
                                           charset = "utf8",
                                           use_unicode = False 
                                           )
    def process_item(self, item, spider):
        query = self.dbpool.runInteraction(self._conditional_insert, item)
        query.addErrback(self.handle_error)
        return item

    def _conditional_insert(self, tb, item):

        tb.execute("insert into tabelname (name, author, press, date, page, price, score, ISBN, author_profile,\
                   content_description, link) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",\
                   (item["name"], item["author"], item["press"], item["date"],\
                   item["page"], item["price"], item["score"], item["ISBN"],\
                   item["author_profile"], item["content_description"], item["link"]))
        log.msg("Item data in db: %s" % item, level=log.DEBUG)

    def handle_error(self, e):
        log.err(e)
