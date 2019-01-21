# _*_ encoding:utf-8 _*_
__author__ = 'pig'
__data__ = '2019\1\15 0015 20:35$'

"""
调试Spiders主函数
"""

from  scrapy.cmdline import execute

import sys
import os

#os.path.abspath(__file__)当前路径  os.path.dirname()获取路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

execute(["scrapy","crawl","jobbole"])
# execute(["scrapy","crawl","lagou"])
# execute(["scrapy","crawl","zhihu"])
