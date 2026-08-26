'''
Author: along
Description: 常用的数据类型
Date: 2026-08-25 13:46:11
LastEditors: along
LastEditTime: 2026-08-26 09:35:07
FilePath: /Agent-web/code/常用的数据类型.py
'''

# 1.整数 int

age = 18
value = -5
zero = 0

print(
  age,
  value,
  zero,
  age + value,
  age - value, 
  age * value,
  age / value, 
  age // value, 
  age % value,
  age ** 2
)  

print(type(age).__name__)

# 18 -5 0 13 23 -90 -3.6 -4 -2 324


  # 2.浮点数 float

height = 180.5
price = 2.22

print(0.1 + 0.2, type(height))


# 3.复数 complex, 复数由实部和虚部组成，虚部使用j表示

complex_num = 3 + 4j

print(complex_num.real, complex_num.imag, type(complex_num)) # 3.0 4.0 <class 'complex'>


# 4.布尔值 bool, 布尔值只有两个取值 True 和 False

if(False or 0 or None or "" or [] or {} or set() or () or 0.0 or complex(0, 0) ):
  print("False")  
else:
  print("True")  # True


# 5.字符串 str, 字符串是由字符组成的序列，可以使用单引号、双引号或三引号表示
name = "Alice"
message = ' Hello, "World"! '
description = """This is a multi-line string."""

#AliceAliceAlice Alice A e Al lice Alic ecilA
print(name * 3, name, name[0], name[-1], name[0:2], name[1:], name[:-1], name[::-1])

print(message.strip(), message.upper(), message.lower(), message.replace("Hello", "Hi"), message.split(","))

print(f"我叫{name}，今年{age}岁。")  # 我叫Alice，今年18岁。


# 6.列表 list, 列表是有序的可变集合，可以包含不同类型的元素
numbers = [1,2,3,4,5]

# 1 5 [2,3] [1,2,3] [1,3,5] [5,4,3,2,1]
print(numbers[0], numbers[-1], numbers[1:3], numbers[:3], numbers[::2], numbers[::-1])

numbers[0] = 10

numbers.append(6)

print(numbers)  # [10, 2, 3, 4, 5, 6]

numbers.insert(1, 11)

print(numbers)  # [10, 11, 2, 3, 4, 5, 6]

numbers.remove(6)
print(numbers)  # [10, 11, 2, 3, 4, 5]

print(numbers.pop())  # 5
print(numbers)  # [10, 11, 2, 3, 4]


print(len(numbers), 2 in numbers)  # 5 True

# 7.元组 tuple, 元组是有序的不可变集合，可以包含不同类型的元素

points = (1, 2, 3, 4, 5)

print(points[0], points[-1], points[1:3], points[:3], points[::2], points[::-1])  # 1 5 (2, 3) (1, 2, 3) (1, 3, 5) (5, 4, 3, 2, 1)

# points[1] = 11  # 这会引发 TypeError，因为元组是不可变的

single = (1,)

print(single, type(single))  # 1 <class 'int'>

# 8.字典类型 dict, 字典是无序的可变集合，由键值对组成，键必须是唯一的

student = {
  "name": "Alice",
  "age": 18,
  "score": 100
}

print(student["name"], student.get("age"), student.get("gender") is None)  # Alice 18 True

student['gender'] = 'female'

print(student)  

student['gender'] = 'female2'

print(student)  

del student['gender']

print(student, student.items(), student.keys(), student.values())  # {'name': 'Alice', 'age': 18, 'score': 100} dict_items([('name', 'Alice'), ('age', 18), ('score', 100)]) dict_keys(['name', 'age', 'score']) dict_values(['Alice', 18, 100])


for key,value in student.items():
  print(key, value)  # name Alice age 18 score 100

# 9.集合类型set, 集合是无序的可变集合，元素是唯一的

numbers_set = {1,2,3,4,5,6}

print(numbers_set, 3 in numbers_set, 7 not in numbers_set)  # {1, 2, 3, 4, 5, 6} True True

a = {1,2,3}
b = {3,4,5}

print(a | b, a & b, a - b, a ^ b)  # {1, 2, 3, 4, 5} {3} {1, 2} {1, 2, 4, 5}

a.add(6)
a.remove(1)


# 10. None 类型, None 是一个特殊的类型，表示没有值或空值

if(None is None):
  print("None is None")  # None is None


a = 10
a = '123'

print(a, type(a))  # 123 <class 'str'>