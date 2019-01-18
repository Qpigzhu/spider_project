# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import datetime
from w3lib.html import remove_tags #去掉网页标签
import re
import scrapy
from ArticleSpider.settings import SQL_DATETIME_FORMAT
from ArticleSpider.utlis.common import extract_num,extract_num2
from scrapy.loader.processors import MapCompose,TakeFirst,Join
from scrapy.loader import ItemLoader


class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class LogoArticleItemLoader(ItemLoader):
    # 自定义itemloader实现默认提取第一个
    default_output_processor = TakeFirst()


class ArticleItemLoader(ItemLoader):
    # 自定义itemloader实现默认提取第一个
    default_output_processor = TakeFirst()


#伯乐在线
def handle_create_data(value):
    #处理时间函数
    try:
        create_date = datetime.datetime.strptime(value, "%Y/%m/%d").date()  # 转换为时间类型
    except Exception as e:
        create_date = datetime.datetime.now().date()

    return create_date



def return_value(value):
    #返回列表值
    return value



def remove_comment_tags(value):
    """
    处理标签函数，去除评论两个字
    """
    if "评论" in value:
        return ""
    else:
        return value



class JoBoleArticleItem(scrapy.Item):  #伯乐Item
    title = scrapy.Field()
    create_date = scrapy.Field(
        input_processor=MapCompose(handle_create_data)  # 预先处理,自定义函数，从左到右顺序执行
    )
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    front_image_url = scrapy.Field(
        output_processor = MapCompose(return_value)  #output_processor取值的函数
    )
    front_image_path = scrapy.Field()
    praise_nums = scrapy.Field(
        input_processor = MapCompose(extract_num)
    )
    comment_nums = scrapy.Field(
        input_processor=MapCompose(extract_num)
    )
    fav_nums = scrapy.Field(
        input_processor=MapCompose(extract_num)
    )
    content = scrapy.Field()
    tags = scrapy.Field(
        input_processor = MapCompose(remove_comment_tags),
        output_processor = Join(",")  #连接符来连接列表
    )

    def get_insert_sql(self):
        insert_sql = """
            insert into jobbole_article(title,url,url_object_id,create_date,front_image_url,front_image_path,
            comment_nums,fav_nums,content,tags)values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE fav_nums=VALUES(fav_nums), content=VALUES(content)
        """
        params = (self["title"], self["url"], self["url_object_id"], self["create_date"],
                  self.get("front_image_url",""),self.get("front_image_path",""),self["comment_nums"],
                  self["fav_nums"],self["content"],self["tags"])

        return insert_sql,params


#拉钩网
def remove_splash(value):
    #去掉工作城市的斜线
    return value.replace("/","")

def handle_jobaddr(value):
    addr_list = value.split("\n")
    addr_list = [item.strip() for item in addr_list if item.strip()!="查看地图"]
    return "".join(addr_list)


class LgGouArticleItem(scrapy.Item):
    title = scrapy.Field()
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    salary = scrapy.Field()
    job_city = scrapy.Field(
        input_processor=MapCompose(remove_splash),
    )
    work_years = scrapy.Field(
        input_processor=MapCompose(remove_splash),
    )
    degree_need = scrapy.Field(
        input_processor=MapCompose(remove_splash),
    )
    job_type = scrapy.Field()
    publish_time = scrapy.Field()
    tags = scrapy.Field()
    job_advantage = scrapy.Field()
    job_desc = scrapy.Field()
    job_addr = scrapy.Field(
        input_processor=MapCompose(remove_tags,handle_jobaddr),
    )
    company_name = scrapy.Field()
    company_url = scrapy.Field()
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """
                insert into lagou_job(title, url, url_object_id, salary, job_city, work_years, degree_need,
                job_type, publish_time, job_advantage, job_desc, job_addr, company_name, company_url,
                tags, crawl_time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE salary=VALUES(salary), job_desc=VALUES(job_desc)
            """
        params = (
            self["title"], self["url"], self["url_object_id"], self["salary"], self["job_city"],
            self["work_years"], self["degree_need"], self["job_type"],
            self["publish_time"], self["job_advantage"], self["job_desc"],
            self["job_addr"], self["company_name"], self["company_url"],
            self["job_addr"], self["crawl_time"].strftime(SQL_DATETIME_FORMAT),
        )

        return insert_sql, params



#知乎问题item
class ZhihuQuestionItem(scrapy.Item):
    zhihu_id = scrapy.Field()
    topics = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    answer_num = scrapy.Field()
    comments_num = scrapy.Field()
    watch_user_num = scrapy.Field()
    click_num = scrapy.Field()
    crawl_time = scrapy.Field()


    def get_insert_sql(self):
        #插入知乎question表的sql语句
        insert_sql = """
            insert into zhihu_question(zhihu_id,topics,url,title,content,answer_num,
            comments_num,watch_user_num,click_num,crawl_time)values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """

        # 插入知乎question表的sql语句
        insert_sql = """
                    insert into zhihu_question(zhihu_id, topics, url, title, content, answer_num, comments_num,
                      watch_user_num, click_num, crawl_time
                      )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE content=VALUES(content), answer_num=VALUES(answer_num), comments_num=VALUES(comments_num),
                      watch_user_num=VALUES(watch_user_num), click_num=VALUES(click_num)
                """
        zhihu_id = int(self["zhihu_id"][0])
        topics = ",".join(self["topics"])
        url = self["url"][0]
        title = "".join(self["title"])
        content = "".join(self["content"])
        answer_num = extract_num("".join(self["answer_num"]))
        comments_num = extract_num("".join(self["comments_num"]))

        if len(self["watch_user_num"]) == 2:
            watch_user_num = extract_num2(self["watch_user_num"][0])
            click_num = extract_num2(self["watch_user_num"][1])
        else:
            watch_user_num = extract_num2(self["watch_user_num"][0])
            click_num = 0

        crawl_time = datetime.datetime.now().strftime(SQL_DATETIME_FORMAT)

        params = (zhihu_id, topics, url, title, content, answer_num, comments_num,
                  watch_user_num, click_num, crawl_time)

        return insert_sql, params

class ZhihuAnswerItem(scrapy.Item):
        zhihu_id = scrapy.Field()
        url = scrapy.Field()
        question_id = scrapy.Field()
        author_id = scrapy.Field()
        content = scrapy.Field()
        parise_num = scrapy.Field()
        comments_num = scrapy.Field()
        create_time = scrapy.Field()
        update_time = scrapy.Field()
        crawl_time = scrapy.Field()

        def get_insert_sql(self):
            insert_sql = """
                        insert into zhihu_answer(zhihu_id, url, question_id, author_id, content, parise_num, comments_num,
                          create_time, update_time, crawl_time
                          ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                          ON DUPLICATE KEY UPDATE content=VALUES(content), comments_num=VALUES(comments_num), parise_num=VALUES(parise_num),
                          update_time=VALUES(update_time)
                    """

            create_time = datetime.datetime.fromtimestamp(self["create_time"]).strftime(SQL_DATETIME_FORMAT)
            update_time = datetime.datetime.fromtimestamp(self["update_time"]).strftime(SQL_DATETIME_FORMAT)
            params = (
                self["zhihu_id"], self["url"], self["question_id"],
                self["author_id"], self["content"], self["parise_num"],
                self["comments_num"], create_time, update_time,
                self["crawl_time"].strftime(SQL_DATETIME_FORMAT),
            )

            return insert_sql, params



