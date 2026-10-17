'''
Author: along
Description: 
Date: 2026-08-31 09:14:25
LastEditors: along
LastEditTime: 2026-10-15 11:29:53
FilePath: /Agent-web/code/函数与作用域.py
'''


# 简单定义函数

def say_hello():
    print("Hello, World!")

# say_hello()


# 调用函数并将返回值赋给变量,函数没有写return，所以返回值是None
# result = say_hello()
# print(result) 

# 定义函数并传递参数

num = 2

def change_num(num):
    num = 1

# print("Before change_num:", num)

str = 'hello'

def change_str(str):
    str = 'world'

change_str(str)
# print("Before change_str:", str)

items = [1, 2, 3]

def change_items(items):

    new_items = items.copy()
    new_items.append(4)
    return new_items

change_items(items)

# print("Before change_items:", items)

# 返回多个值,按照顺序

def get_name_and_age():
    name = "Alice"
    age = 30
    return name, age

name, age  = get_name_and_age()
# print("Name:", name)
# print("Age:", age)

def sum_all(*args):
    print("Arguments:",args, type(args))
    total = 0
    for num in args:
        total += num
    return total

# print(sum_all(1, 2, 3, 4, 5))

# 任意数量的关键字参数

def show_info(**keywords):
    print("Keywords:", keywords, type(keywords))
    for key, value in keywords.items():
        print(f"{key}: {value}")

# show_info(name="Alice", age=30, city="New York")

# 仅限关键字参数
def display_info(host, *, port=80, timeout=1000):
    print(f"Host: {host}, Port: {port}, Timeout: {timeout}")

# display_info('www.baidu.com', port=8080, timeout=2000)

#解包传参

def rectangle_area(length, width):
    return length * width

dimensions = (5, 10)
area = rectangle_area(*dimensions)
# print("Area:", area)

options = { 'length': 5, "width": 20 }
# print("Area:", rectangle_area(**options))

# 函数内赋值会创建局部变量

counter = 0

def increment_counter():
    global counter  # 声明使用全局变量
    counter += 1    

increment_counter()
print("Counter:", counter)

def calculate_sum(price: float, rate: float = 0.1) -> float:
    if(price < 0 or not 0 < rate < 1):
        raise ValueError("Invalid input values")
    return price * (1 + rate)

print(list('123'))

def celsius_to_fahrenheit(celsius: float) -> float:
    return (celsius * 9/5) + 32

print(celsius_to_fahrenheit(0))

def score_summary(*scores):
    if not scores:
        raise ValueError("No scores provided.")
    return max(scores), min(scores), sum(scores) / len(scores)


print(score_summary(80, 90, 70))  # (90, 70, 80.0)



message = "外层"


def outer():
    message = "中层"

    def inner():
        print(message)

    inner()


outer()
print(message)


def report(name,score):
    print(f"学生 {name} 的成绩是 {score}", f"成绩是: { '及格' if score>=60 else '不及格' }")

report("小白", 75)

def division(a,b):
    return a,b

print(division(10,2))  # (10, 2)

print(min([10, 20, 30]))  # 10

def info(age, name, city):
    print(f"姓名: {name}, 年龄: {age}, 城市: {city}")


info(name='张三', city='北京', age=25)  # 姓名: 张三, 年龄: 25, 城市: 北京

def sum_all(*args):
    print("Arguments:", args, type(args))
sum_all(1, 2, 3, 4, 5)  # Arguments: (1, 2, 3, 4, 5) <class 'tuple'>

def show_info(**keywords):
    print("Keywords:", keywords, type(keywords))
    for key, value in keywords.items():
        print(f"{key}: {value}")

show_info(name="Alice", age=30, city="New York")