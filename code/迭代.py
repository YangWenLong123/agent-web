'''
Author: along
Description: 
Date: 2026-10-16 16:39:00
LastEditors: along
LastEditTime: 2026-10-17 09:27:01
FilePath: /Agent-web/code/迭代.py
'''

# 字符串循环迭代
for char in 'helloworld':
  print(char, end='/')

print('/n')

# for循环迭代list
for item in [1,2,3,4,5]:
  print(item, end=' ')

print('/n')

# for循环迭代dict字典

dict1 = {"name": 'along', "age": 18, "city": "beijing"}

# print(dict1.items())  # dict_items([('name', 'along'), ('age', 18), ('city', 'beijing')])

for key in dict1:
  print(key, dict1[key])

print('/n')

print(dict1.keys(), dict1.values())  # dict_keys(['name', 'age', 'city'])

print('/n')

for value in dict1.values():
  print(value)

for key,value in [('name', 'along'), ('age', 18), ('city', 'beijing')]:
  print(key, value)


for key in  iter('helloworld'):
  print(key, end=' ')


# while True:
#   try:
#     print(next(iter('helloworld')), end=' ')
#   except StopIteration:
#     break

print('/n')

gen = (x * x for x in range(5))

print(gen)

print(next(gen))  # 0
print(next(gen))  # 1 
print(next(gen))  # 1 

for num in gen:
  print(num, end=' ')


names = ['Alice', 'Bob', 'Cathy']
ages = [18, 19, 20]
# 用 zip 把两个 list 配成对，for 循环里拆包成 name、age 后逐对打印

dict1 = dict(zip(names, ages))

print(dict1, dict1.items())  # {'Alice': 18, 'Bob': 19, 'Cathy': 20} dict_items([('Alice', 18), ('Bob', 19), ('Cathy', 20)])

for name,age in dict1.items():
    print(name, age)


class Student:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def __iter__(self):
       print(f'{self.name} is iterable, age is {self.age}')

p = Student('小白学python', 18)

p.__iter__()

class MyIterable(Student):
  def __init__(self, name, age, city):
    super().__init__(name, age)
    self.city = city

  def __max__(self):
    print(f'{self.name} is max, age is {self.age}, city is {self.city}')

p1 = MyIterable('小白学python', 18, 'beijing')

p1.__max__()