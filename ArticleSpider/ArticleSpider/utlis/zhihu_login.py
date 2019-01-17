# _*_ encoding:utf-8 _*_
__author__ = 'pig'
__data__ = '2019\1\17 0017 11:59$'

import requests
try:
    import cookielib

except:
    import http.cookiejar as cookielib

import re

session = requests.session()
session.cookies = cookielib.LWPCookieJar(filename="cookies.txt") #加载cookies文件

try:
    session.cookies.load(ignore_discard=True)
except:
    print("cookie未能加载")

agent = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.104 Safari/537.36"
header = {
    "HOST":"www.zhihu.com",
    "Referer": "https://www.zhizhu.com",
    'User-Agent': agent
}


def get_index():
    response = session.get("https://www.zhihu.com", headers=header)
    with open("index_page.html", "wb") as f:
        f.write(response.text.encode("utf-8"))
    print ("ok")



def get_xsrf():
    #获取xsrf code
    response = session.get("https://www.zhihu.com", headers=header)
    response_text = response.text
    #reDOTAll 匹配全文
    match_obj = re.match('.*name="_xsrf" value="(.*?)"', response_text, re.DOTALL)
    xsrf = ''
    if match_obj:
        xsrf = match_obj.group(1)

    return xsrf



def zhihu_login(account,password):
    #知乎登录
    if re.match("^1\d{10}",account):
        print("手机登录")
        post_url = "https://www.zhihu.com/login/phone_num"
        post_data = {
            "_xsrf": get_xsrf(),
            "phone_num": account,
            "password": password,
        }

    response_text = session.post(post_url,data=post_data,headers=header)
    session.cookies.save()


# zhihu_login("13249981700","ZSH123123")
get_index()