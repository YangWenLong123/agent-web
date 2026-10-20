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

print(int('123'))
print(float('123'))
print(complex('123'))
print(type({"a": 1}), type(str({"a": 1})), str({"a": 1}))

value = [1, 2, 3]

print(value)       # 看值
print(type(value)) # 看类型
print(id(value))   # 看对象身份；具体数字每次运行可能不同
# print(dir(value)) # 看对象的属性和方法
# print(dir('123')) # 看对象的属性和方法

items = [1, 2]
items += [3]
print(items)  # [1, 2, 3]

big_number = 10 ** 100
print(big_number)

population = 1_400_000_000
print(population, population == 1400000000)

print(-7 // 2)

print(False + 1)

text = "Python is fun"

print(text.lower())
print(text.upper())
print(text.replace("fun", "powerful"))
print(text.startswith("Python"))
print(text.endswith("fun"))
print(text.find("is"))       # 找不到时返回 -1
print("a,b,c".split(","))
print("-".join(["2026", "10", "17"]))


list1 = [1, 2, 3]

list1.append(4)
print(list1)  # [1, 2, 3, 4]

list1.extend([5, 6])
print(list1)  # [1, 2, 3, 4, 5, 6]

list1.insert(1,1.5)
print(list1)  # [1, 1.5, 2, 3, 4, 5, 6]


list1.remove(1.5)
print(list1)  # [1, 2, 3, 4, 5, 6]

list2 = list1.pop()
print(list2)  # 6


inventory = {
    "keyboard": {"name": "机械键盘", "stock": 3, "minimum": 5},
    "mouse": {"name": "鼠标", "stock": 12, "minimum": 5},
    "monitor": {"name": "显示器", "stock": 0, "minimum": 2},
}

low_stock = []
total_stock = 0

for product_id, product in inventory.items():
    stock = product["stock"]
    minimum = product["minimum"]
    total_stock += stock

    if stock < minimum:
        low_stock.append(product["name"])
        status = "需要补货"
    else:
        status = "库存正常"

    print(f"{product_id}: {product['name']}，库存 {stock}，{status}")

print(f"库存总件数：{total_stock}")
print(f"需要补货：{', '.join(low_stock) if low_stock else '无'}")



from decimal import Decimal, ROUND_HALF_UP

cart = [
    {"name": "机械键盘", "price": Decimal("299.90"), "quantity": 1},
    {"name": "鼠标", "price": Decimal("89.50"), "quantity": 2},
    {"name": "鼠标垫", "price": Decimal("29.90"), "quantity": 1},
]

subtotal = Decimal("0")

print("=== 购物清单 ===")
for item in cart:
    line_total = item["price"] * item["quantity"]
    subtotal += line_total
    print(
        f"{item['name']}: "
        f"{item['price']:.2f} x {item['quantity']} = {line_total:.2f}"
    )

if subtotal >= Decimal("200"):
    discount_rate = Decimal("0.90")
else:
    discount_rate = Decimal("1")

total = (subtotal * discount_rate).quantize(
    Decimal("0.01"), rounding=ROUND_HALF_UP
)

discount = subtotal - total
print("----------------")
print(f"商品合计：{subtotal:.2f} 元")
print(f"优惠金额：{discount:.2f} 元")
print(f"应付金额：{total:.2f} 元")


def greet(self):
    print('hi')

Greeter = type('Greeter', (object),{ 'greet': greet })

g = Greeter()

g.greet()

print(type(Greeter))