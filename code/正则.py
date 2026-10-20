'''
Author: along
Description: 
Date: 2026-10-20 16:01:34
LastEditors: along
LastEditTime: 2026-10-20 16:47:51
FilePath: /Agent-web/code/正则.py
'''


import re

str1 = '两点水|abc|vv1|程序员'

result = re.findall('[a-z]+',str1) # 找出连续的小写字母，知道规则

print(result)  

import re

s = 'abc123def456'
print(re.match('\d+', s))    # None（开头不是数字）
print(re.search('\d+', s))   # <Match '123'>
print(re.findall('\d+', s))  # ['123', '456']

def is_phone(s):
    return re.match('^1[3-9]\d{9}$', s) is not None

print(is_phone('13812345678'))
print(is_phone('12345'))
print(is_phone('1381234567a'))