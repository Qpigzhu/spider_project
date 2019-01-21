# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import MySQLdb
import MySQLdb.cursors
from ArticleSpider.models.es_jobbole import ArticleType

from  scrapy.pipelines.images import  ImagesPipeline
from scrapy.exporters import JsonItemExporter
from twisted.enterprise import adbapi

class ArticlespiderPipeline(object):
    def process_item(self, item, spider):
        return item


class JsonExporterPipleline(object):
    # 调用scrapy提供的json export导出json文件
    def __init__(self):
        self.file = open('articleexport.json', 'wb')  #以二进制打开文件
        self.exporter = JsonItemExporter(self.file, encoding="utf-8", ensure_ascii=False)
        self.exporter.start_exporting()

    #爬虫停止时
    def close_spider(self, spider):
        self.exporter.finish_exporting() #停止写入
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item) #写入的Item
        return item


class MysqlPipeline(object):
    # 采用同步的机制写入mysql
    def __init__(self):
        self.conn = MySQLdb.connect("127.0.0.1","root","root",'article_spider', charset="utf8", use_unicode=True,port=3307)
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        insert_sql = """
            insert into jobbole_article(title,url,url_object_id,create_date)values (%s,%s,%s,%s)
        """
        self.cursor.execute(insert_sql,(item["title"],item["url"],item["url_object_id"],item["create_date"]))
        self.conn.commit()


class MysqlTwistedPipline(object):
    #采用异步来插入数据
    def __init__(self,dbpool):
        self.dbpool = dbpool

    #去设置里面拿MYSQL的配置值
    @classmethod
    def from_settings(cls, settings):
        dbparms = dict(
            host=settings["MYSQL_HOST"],
            db=settings["MYSQL_DBNAME"],
            user=settings["MYSQL_USER"],
            passwd=settings["MYSQL_PASSWORD"],
            charset='utf8',
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=True,
            port = 3307,
        )

        dbpool = adbapi.ConnectionPool("MySQLdb",**dbparms)

        return cls(dbpool)

    def process_item(self, item, spider):
        # 使用twisted将mysql插入变成异步执行
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error, item, spider)  # 处理异常

    def handle_error(self, failure, item, spider):
        # 处理异步插入的异常
        print(failure)

    def do_insert(self, cursor, item):
            # 执行具体的插入
            # 根据不同的item 构建不同的sql语句并插入到mysql中
        # insert_sql = """
        #     insert into jobbole_article(title,url,url_object_id,create_date,front_image_url,front_image_path,
        #     comment_nums,fav_nums,content,tags)values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        # """
        # cursor.execute(insert_sql, (item["title"], item["url"], item["url_object_id"], item["create_date"],
        #                             item.get("front_image_url",""),item.get("front_image_path",""),item["comment_nums"],
        #                             item["fav_nums"],item["content"],item["tags"]
        #                             ))

        # 根据不同的item 构建不同的sql语句并插入到mysql中
        insert_sql,params = item.get_insert_sql()
        cursor.execute(insert_sql, params)






class ArticleImagePipeline(ImagesPipeline):
    # 重写该方法可从result中获取到图片的实际下载路径,并填充到front_image_path字段里面
    def item_completed(self, results, item, info):
        if "front_image_url" in item:
            for ok,value in results:
                image_file_path = value["path"] #获取图片下载路径
            item["front_image_path"] = image_file_path
            return item


class elasticsearchPipeline(object):
    #将数据写入到es中

    def process_item(self, item, spider):
        #使得可以通用调用此方法,来存入es
        item.save_to_es()

        return item