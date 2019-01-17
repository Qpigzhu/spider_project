# _*_ encoding:utf-8 _*_
__author__ = 'pig'
__data__ = '2019\1\16 0016 14:47$'

"""
处理Url地址，返回一个MD5的值
"""

import hashlib

def get_md5(url):
    # str就是unicode了
    if isinstance(url,str):
        url = url.encode("utf-8")

    m = hashlib.md5()
    m.update(url)
    return m.hexdigest()

if __name__ == '__main__':
    print(get_md5("http://jobbole.com".encode("utf-8")))
