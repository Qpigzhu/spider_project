# _*_ encoding:utf-8 _*_
__author__ = 'pig'
__data__ = '2019\1\19 0019 16:59$'
"""
随机获取一个IP代理
"""
import requests
from scrapy.selector import Selector
import MySQLdb
import time

#连接数据库
conn = MySQLdb.connect(host="127.0.0.1", user="root", passwd="root", db="article_spider", charset="utf8",port=3307)
cursor = conn.cursor()

def crawl_ips():
    #爬取西刺的免费ip代理
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0"}
    for i in range(1,30):
        url = "https://www.xicidaili.com/nn/{}".format(i)
        response = requests.get(url=url,headers=headers)
        selector = Selector(text=response.text)
        all_trs = selector.css("#ip_list tr")

        ip_list = []
        for tr in all_trs[1:]:
            speed_str = tr.css(".bar::attr(title)").extract()[0]
            if speed_str:
                speed = float(speed_str.split("秒")[0])

            all_text = tr.css("td::text").extract()

            ip = all_text[0]
            port = all_text[1]
            proxy_type = all_text[5]

            ip_list.append((ip, port, proxy_type, speed))

        #将数据插入数据库
        for ip_info in ip_list:
            cursor.execute(
                "insert proxy_ip(ip, port, speed, proxy_type) VALUES('{0}', '{1}', {2}, '{3}')".format(
                    ip_info[0], ip_info[1], ip_info[3],ip_info[2]
                )
            )

            conn.commit()


class GetIp(object):

    def delete_ip(self,ip):
        #删除无效的ip
        # 从数据库中删除无效的ip
        delete_sql = """
                    delete from proxy_ip where ip='{0}'
                """.format(ip)
        cursor.execute(delete_sql)
        conn.commit()
        return True

    def judge_ip(self, proxy_type,ip, port,):
        # 判断ip是否可用
        http_url = "http://www.baidu.com"
        proxy_url = "{0}://{1}:{2}".format(proxy_type,ip, port)
        try:
            proxy_dict = {
                proxy_type: proxy_url,
            }
            response = requests.get(http_url, proxies=proxy_dict)
        except Exception as e:
            print("invalid ip and port")
            self.delete_ip(ip)
            return False
        else:
            code = response.status_code
            if code == 200:
                print("effective ip")
                return True
            else:
                print("invalid ip and port")
                self.delete_ip(ip)
                return False



    def random_get_ip(self):
        # 从数据库中随机获取一个可用的ip
        random_id_sql = "SELECT ip, port,proxy_type FROM proxy_ip ORDER BY RAND()LIMIT 1"
        result = cursor.execute(random_id_sql)
        for ip_info in cursor.fetchall():
            ip = ip_info[0]
            port = ip_info[1]
            proxy_type = ip_info[2]

            judge_ip = self.judge_ip(proxy_type,ip,port)
            if judge_ip:
                print("{0}://{1}:{2}".format(proxy_type,ip, port))
                return "{0}://{1}:{2}".format(proxy_type,ip, port)
            else:
                return self.random_get_ip()


if __name__ == '__main__':
    get_ip = GetIp()
    get_ip.random_get_ip()