# _*_ encoding:utf-8 _*_
__author__ = 'pig'
__data__ = '2019\1\16 0016 14:47$'

"""
处理Url地址，返回一个MD5的值
"""

import hashlib
import re


def get_md5(url):
    # str就是unicode了
    if isinstance(url,str):
        url = url.encode("utf-8")

    m = hashlib.md5()
    m.update(url)
    return m.hexdigest()

def extract_num(text):
    """
    去除评论,点赞,收藏数的正则表达式,只取数字
    """
    match_re = re.match(".*?(\d+).*?",text)
    if match_re:
        nums = int(match_re.group(1))
    else:
        nums = 0

    return nums

def extract_num2(text):
    #处理13,167这类型的数字
    try:
        nums = text.split(",")
        nums = int("".join(nums))
        return nums
    except:
        return int(text)




if __name__ == '__main__':
    print(extract_num2("13,637"))
