# -*- coding: utf-8 -*-
import re
import datetime
import scrapy
from scrapy.http import Request
from scrapy.loader import ItemLoader
from urllib import parse

from ArticleSpider.items import JoBoleArticleItem,ArticleItemLoader,LogoArticleItemLoader
from ArticleSpider.utlis.common import get_md5



class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self, response):
        """
        1.获取文章列表页中的文章url交给scrapy下载后并解析
        2.获取下一页的url并交给scrapy进行下载,下载完成后交给parse
        """
        #取取出所有的详情页URL,attr是获取href的值
        post_nodes = response.css("#archive .floated-thumb .post-thumb a")
        #再把URL交给parse_detail函数去解析,parse.urljoin是连接详情Url地址
        for post_node in post_nodes:
            image_url = post_node.css("img::attr(src)").extract_first("")  #封面图
            post_url = post_node.css("a::attr(href)").extract_first("")

            #在下载网页时将这个封面url获取到，并通过meta将他发送出去。在callback的回调函数中接收该值
            yield Request(url=parse.urljoin(response.url,post_url),meta={"front_image_url":image_url},callback=self.parse_detail)


        #提取下一页Url,extract_first()取不到数据的的时候,不会报错
        nex_url = response.css(".next.page-numbers::attr(href)").extract_first("")
        if nex_url:
            yield Request(url=parse.urljoin(response.url,nex_url),callback=self.parse)


    def parse_detail(self,response):

        #extract()格式化文本,获取文本内容
        # title = response.xpath("//div[@class='entry-header']/h1/text()").extract()[0]
        # #发布日期 replace是替换字符
        # create_time = response.xpath("//p[@class='entry-meta-hide-on-mobile']/text()").extract()[0].strip().replace("·","").strip()
        #
        # #contains方法是获取class属性的其中一个值
        # praise_nums = int(response.xpath("//span[contains(@class,'vote-post-up')]/h10/text()").extract()[0])
        #
        # #收藏数
        # fav_nums =response.xpath("//span[contains(@class,'bookmark-btn')]/text()").extract()[0]
        # match_re = re.match(".*?(\d+).*?",fav_nums)
        # if match_re:
        #     fav_nums = int(match_re.group(1))
        # else:
        #     fav_nums = 0
        # #评论数
        # comment_nums = response.xpath("//a[@href='#article-comment']/text()").extract()[0].strip()
        # #使用正则表达式,把"评论"两个字去掉
        # match_re = re.match(".*?(\d+).*?",comment_nums)
        # if match_re:
        #     comment_nums = int(match_re.group(1))
        #
        # else:
        #     comment_nums = 0
        #
        #     #内容主体
        # cotent = response.xpath("//div[@class='entry']").extract()[0]
        #
        # #标签 = ['职场', ' 9 评论 ', '面试']
        # tag_list = response.xpath("//p[@class='entry-meta-hide-on-mobile']/a/text()").extract()
        # #去掉评论，使用去重方法.endswith()方法,以评论为结尾的
        # tag_list = [element for element in tag_list if not element.strip().endswith("评论")]
        # #列表链接
        # tags = ",".join(tag_list)


                #css选择器提取

        article_item = JoBoleArticleItem()  #创建Item实例
        front_image_url = response.meta.get("front_image_url","")  #封面图

        # #class值为entry-header下的h1标签,获取文本使用::text
        # title = response.css(".entry-header h1::text").extract()[0]
        # create_date = response.css(".entry-meta-hide-on-mobile::text").extract()[0].strip().replace("·","").strip()
        # #点赞数
        # praise_nums = response.css(".vote-post-up h10::text").extract()[0]
        #
        # #收藏数
        # fav_nums = response.css(".bookmark-btn::text").extract()[0]
        # match_re = re.match(".*?(\d+).*?",fav_nums)
        # if match_re:
        #     fav_nums = int(match_re.group(1))
        # else:
        #     fav_nums = 0
        #
        # #a标签herf值为article-comment下的span标签文本
        # comment_nums = response.css("a[href='#article-comment'] span::text").extract()[0]
        # match_re = re.match(".*?(\d+).*?",comment_nums)
        # if match_re:
        #     comment_nums = int(match_re.group(1))
        # else:
        #     comment_nums = 0
        #
        # #内容主体
        # content =  response.css("div.entry").extract()[0]
        #
        # tag_list = response.css("p.entry-meta-hide-on-mobile a::text").extract()
        # tag_list = [element for element in tag_list if not element.strip().endswith("评论")]
        # tags = ",".join(tag_list)
        #
        # # article_item将这个item传送到pipelines中
        # article_item["url_object_id"] = get_md5(response.url)
        # article_item["title"] = title
        # article_item["url"] = response.url
        # try:
        #     create_date = datetime.datetime.strptime(create_date,"%Y/%m/%d").date()  #转换为时间类型
        # except Exception as e:
        #     create_date = datetime.datetime.now().date()
        # article_item["create_date"] = create_date
        # article_item["front_image_url"] = [front_image_url]
        # article_item["praise_nums"] = praise_nums
        # article_item["comment_nums"] = comment_nums
        # article_item["fav_nums"] = fav_nums
        # article_item["tags"] = tags
        # article_item["content"] = content


        #通过item loader加载item
        item_loader = ArticleItemLoader(item=JoBoleArticleItem(),response=response)
        item_loader.add_css("title", ".entry-header h1::text")
        item_loader.add_value("url", response.url)
        item_loader.add_value("url_object_id", get_md5(response.url))
        item_loader.add_css("create_date", "p.entry-meta-hide-on-mobile::text")
        item_loader.add_value("front_image_url", [front_image_url])
        item_loader.add_css("praise_nums", ".vote-post-up h10::text")
        item_loader.add_css("comment_nums", "a[href='#article-comment'] span::text")
        item_loader.add_css("fav_nums", ".bookmark-btn::text")
        item_loader.add_css("tags", "p.entry-meta-hide-on-mobile a::text")
        item_loader.add_css("content", "div.entry")

        #调用这个方法来对规则进行解析生成item对象
        article_item = item_loader.load_item()

        # 在settings把ITEM_PIPELINES 开启才能进入pipelines
        yield article_item
