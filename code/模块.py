'''
  1、模块的使用： import / from ... import ... / from ... import * / as
  2.主模块和非主模块(__name__ == '__main__')
  3.包(Package)
  4.作用域（Public / private）
'''

'''
  为什么要使用模块：
    1、提高可维护性 - 可以按功能拆分到不同的文件，不再是一个巨型脚本
    2、提高代码复用性 - 别人写好的模块可以直接拿来使用，不变再重复造轮子
    3、避免命名冲突 - 相同名字的函数和变量可以分别存在在不同的模块中
'''

'''
 模块大致分为两类
  1、标准库模块：Python自带，比如math、os、sys、math、random等
  2、自定义的模块：自己写的py文件
  3、第三方模块：别人写好的模块发布到PyPI上，使用pip install安装，比如requests、numpy、pandas等
'''

# import math # 导入的是整个模块

# from math import pi,sqrt # 导入模块中的指定函数或变量

from math import * # 导入模块中的所有函数和变量

import datetime as dt # 导入模块并起别名

# print(math.pi)  # 输出圆周率
print(sqrt(16))  # 输出16的平方根

print(dt.datetime.now())  # 输出当前时间

def main():
    print('我是主模块')

if __name__ == '__main__':
    main()  # 只有在当前模块是主模块时才会执行main函数


import json

data = {'name': 'Alice', 'age': 18}

print(data)

s = json.dumps(data)

print(s)

print(json.loads(s))