# 使用 = 给变量赋值
# 变量命名规则与常见命名方式
# 修改变量的值
# 使用 print() 输出变量

# name = 'Along'
# age = 18
# weight = 60.5

# print(f"1. 我的名字叫做{name}, 今年{age}岁, 体重{weight}公斤")

# age = age + 2

# print(f"2. 我的名字叫做{name}, 后年{age}岁, 体重{weight}公斤")

# 变量命名规则
# 1.变量名只能包含字母，数字和下划线，不能以数字开头

# Age = 11  # 变量名可以以大写字母开头
# _age = 12  # 变量名可以以下划线开头
# user_name = 'Along'  # 变量名可以包含下划线
# MAX_SIZE = 100  # 变量名可以全部大写，通常用于常量

# 姓名 = '张三'  # 变量名可以使用中文，但不推荐
# π = 3.14  # 变量名可以使用希腊字母，但不推荐

# print(Age, _age, user_name, MAX_SIZE, 姓名, π)


# 非法标识符

# 0A = 12  # 变量名不能以数字开头，会报错
# -ddd = 13  # 变量名不能以减号开头，会报错
#user-name = 'Along'  # 变量名不能包含减号，会报错
#user.name = 'Along'  # 变量名不能包含点号，点号用于可访问性
# class = 'Along'  # 变量名不能使用关键字，会报错


# 关键字

# import keyword

# print("Python关键字:", keyword.kwlist)

# is_ok = True  # 变量名可以使用关键字的变体，但不推荐
# is_admin = False  # 变量名可以使用关键字的变体，但不推荐
# is_none = None  # 变量名可以使用关键字的变体，但不推荐

# print(is_ok, is_admin, is_none == None, None is None)  


## 关键字 条件和逻辑判断（if、elif、else）

# scope = 100

# if scope < 80 and scope >= 60:
#   print("成绩良好")
# elif scope >= 90 and scope <= 95:
#   print("成绩优秀")
# else:
#   print("满分100分")

## 关键字 and 逻辑与：所有条件都为真，结果才为真

# sex = '男'
# has_id_card = True

# result = sex == '男' and '有身份证' and False # result的值返回最右侧的值

# if sex == '男' and has_id_card:
  # print("可以入场", sex == '男' and has_id_card, result)


## 关键字 or 逻辑或：至少一个条件为真，结果就为真

# role = '管理员'

# if role == '管理员' or role == '超级管理员':
  # print("可以登录后台管理系统")


## 关键字 input 用户输入内容

# username = input("用户名：") 

# print(username)


## 关键字 in 判断元素是否在序列中

# if 'Python' in ['Python', 'Java', 'C++']:
#   print("Python在列表中")

# for item in ['Python', 'Java', 'C++']:
#   if 'Python' in item:
#     print("Python在列表中")

## 关键字 not 对布尔结果取反

# is_admin = False

# if not is_admin:
#   print("不是管理员")


## 关键字 is 判断两个对象是否是同一个对象，不是判断内容是否相等

# is_none = None

# if is_none is None:
#   print("is_none是None对象")

# a = [1, 2, 3]
# b = [1,2 ,3]

# print(a == b)  # True，判断内容是否相等
# print(a is b)  # False，判断是否是同一个对象

## 关键字 for 循环遍历序列

# for item in ['Python', 'Java', 'C++']:
#   print(item)


# for item in range(5):
#   print(item)


## 关键字 while 循环

# count = 0

# while count < 5:
#   print(count)

#   if(count == 1):

#     count += 1

#     continue  # 当count等于1时，跳过本次循环，继续下一次循环

#   # 当count等于3时，跳出循环
#   if count == 3:
#     break

#   count += 1


## 关键字 函数相关

# def add(a,b):
#   return a + b

# print(add(3,4))

# def get_name():
#   # return name
#   print()

# print(get_name() is None)


# lambda 参数: 表达式
# add2 = lambda a,b:  a + b

# print(add2(1,2))

# users = [
#     {"name": "Tom", "age": 20},
#     {"name": "Jack", "age": 18},
# ]

# # 每次取出一个用户，用用户的 age 作为排序依据 reverse默认值False正序、 True倒序
# # users.sort(key=lambda user: user["age"], reverse=False)

# users.sort(key = lambda user: user['age'])

# print(users)


## yield 把函数变成生成器。每次产生一个值，并暂停函数，下次继续执行。

# def next():
#     yield 1
#     yield 2
#     yield 3

# print(next())
# print(next())
# print(next())
# print(next())


# def all_numbers():
#     yield from [1, 2, 3]

# print(all_numbers())


## 关键字 global


# count = 0

# def add ():

#   # 声明全局global，可以在函数内部修改变量值
#   global count
#   count += 1
#   print(count)

# add()


# def outer():
#   count = 0

#   def inner():

#     nonlocal count

#     count += 1

#     return count


#   return inner ()

# print(outer())


## del 删除变量、列表元素、字典元素或对象属性

# name = 'Along'

# print(name)

# del name

# print(name)


# numbers = [1,2,3]

# del numbers[1]
# del numbers[1]
# del numbers[0]

# print(numbers)

# user = { "name": '张三', "age": 20 }

# print(user)

# del user['name']

# print(user)


## 类和面向对象

# class Person:
#   def __init__(self, name):
#     self.name = name

#   def say_hello(self):
#     print(f"你好，我叫{self.name}")

# person = Person('小明')

# person.say_hello()


# class Person:
#   def __init__(self, name):
#     self.name = name

#   def say_hello(self):
#     print(f"你好，我是 {self.name}")

# person = Person("小明")
# person.say_hello()


## 模块导入 ， 95个内置模块

# import math

# print(math.sqrt(16))

# print(dir(__builtins__))


# import sys

# print(sys.builtin_module_names)

# print(len(sys.builtin_module_names))

# 从模块中导入指定内容

# from math import sin

# print(sin(2))

# import math as mt

# print(mt.sin(2))

# from math import sin as s

# print(s(2))


# try:
#   number = int(input('请输入数字'))
# except ValueError:
#   print('请输入有效数字')
# else:
#   print('转换成功', number)
# finally:
#   print('处理结束')


# def set_age(age):
#   if age < 0:
#     raise ValueError('年龄不可以小于0')

#   return age

# set_age(1)

# try:
#   number = int('a')
# except ValueError as error:
#   raise RuntimeError('数据转换失败') from error


# age = 20

# assert age > 0, '年龄大于0'

# import asyncio

# async def download():
#     await asyncio.sleep(3)
#     return "下载完成"

# async def main():
#     result = await download()
#     print(result)

# asyncio.run(main())