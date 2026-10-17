'''
Author: along
Description: 
Date: 2026-10-15 09:05:09
LastEditors: along
LastEditTime: 2026-10-15 09:55:34
FilePath: /Agent-web/code/条件与循环.py
'''
### 条件语句

age = 18

if age >= 18:
    print("你已经成年了")
else:
    print("你还未成年") 

# 真假判断隐规则

num = None

if num:
    print("num为真")  
else:
    print("num为假")

'''
  这些都是假值：

    数字0、字符串''、空列表[]、空元组()、空字典{}、空集合set()、None、False
  其他都是为真值
'''

result = 80

if result >= 90:
    print("优秀")
elif result >= 80:
    print("良好")
elif result >= 70:
    print("中等")
elif result >= 60:
    print("及格")
else:
    print("不及格")

java = 80
python = 90

if java >= 60 and python >= 60:
    print("及格")
elif java >= 60 or python >= 60:
    print("有一门及格")
else:
    print("不及格")


command = 'start'

match command:
    case 'start':
        print("启动")
    case 'stop':
        print("停止")
    case 'pause':
        print("暂停")
    case _:
        print("未知命令")


point = [10, 0]

match point:
    case [0, 0]:
        print('原点')
    case [x, 0]:
        print(f'在 x 轴上，x = {x}')
    case [0, y]:
        print(f'在 y 轴上，y = {y}')
    case [x, y]:
        print(f'普通点，x = {x}，y = {y}')
    case _:
        print('不是二维坐标')


response = {'status': 'ok', 'data': [1, 2, 3]}

match response:
    case {'status': 'ok', 'data': data}:
        print(f'成功，拿到数据 {data}')
    case {'status': 'error', 'message': msg}:
        print(f'失败：{msg}')
    case _:
        print('未知响应')


for str in set(["小白学python",2]):
    print(str)

print(range(0, 50, 10), list(range(0, 50, 10)))

for key in range(0, 5, 2):
    print(key)


count = 1
total = 0

while count <= 100:
    total+=count
    count+=1

print(total)