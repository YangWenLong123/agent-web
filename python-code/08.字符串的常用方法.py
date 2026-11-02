# find()，在字符串中查找子串，返回第一次出现的索引位置，找不到返回-1

s = ' hello,python *'

s_index = s.find('py')
print(s_index)

# count(), 统计子串在字符串中出现的次数

s_count = s.count('l')

print(s_count)

# upper(), 将字符串中的所有字母都转换为大写

s_upper = s.upper()
print(s_upper)

# lower(), 将字符串中所有的字母转为小写
s_lower = s_upper.lower()
print(s_lower)

#split(), 将字符串按照指定分隔符分割为列表

s_list = s.split(',')
print(s_list)

#strip(),去除字符串两端的空白字符或指定字符
s_strip = s.strip('*')
print(s_strip)


#replace(),将指定的字符串替换为新的子串
print(s)
s1 = s.replace('*', '').replace(' ', '')
print(s1)

#startwith() 检查字符串是否以指定子串开头，返回布尔值。
s_with = s.startswith(' ')
print(s_with)

print(s)

# endwith()
s_end = s.endswith('*')
print(s_end)

"""
    案例：邮箱格式输出，至少包含一个@和至少一个.
"""

# email = input('请输入邮箱')
#
# if email.count('@') == 1 and email.find('.') != -1:
#     print('邮箱正确')
# else:
#     print('邮箱错误')


"""
    案例：输入一个字符串，判断该字符串是否是回文字符串
    1. 上海自来水来自海上
"""

text = input('请输入回文串')

text_reverse = text[::-1]
print(text_reverse == text)