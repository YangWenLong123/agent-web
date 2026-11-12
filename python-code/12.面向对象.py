# 定义类
# class Car:
#     def __init__(self, color, name, price, speed):
#         self.color = color
#         self.name = name
#         self.price = price
#         self.speed = speed
#
#     def car_speed(self):
#         print(f'汽车速度为{self.speed}')
#
#     def total_car(self, num, price):
#         print(f'汽车价格为{num * price}')
#         return num * price
#
# c1 = Car('红色', 'BMW', 20000, '100码')

# print(c1.__dict__)

# c1.car_speed()
# c1.total_car(2, 100)



# 魔法方法
# class Car:
#     def __init__(self, color, name, price, speed):
#         self.color = color
#         self.name = name
#         self.price = price
#         self.speed = speed
#
# c1 = Car('红色', 'BMW', 20000, '100码')
# print(c1)
#
# c2 = Car('红色', 'BMW', 20000, '100码')
# print(c2)
#
# print(c1 == c2)
# print(c1 > c2)


# 重写魔法方法
# class Car:
#     def __init__(self, color, name, price, speed):
#         self.color = color
#         self.name = name
#         self.price = price
#         self.speed = speed
#
#     def __str__(self):
#         return f'{self.color} {self.name} {self.price} {self.speed}'
#     def __eq__(self, other):
#         return self.price == other.price and self.speed == other.speed and self.color == other.color and self.name == other.name
#     def __lt__(self, other):
#         return self.price < other.price
#
# c1 = Car('红色', 'BMW', 20000, '100码')
# print(c1)
#
# c2 = Car('红色', 'BMW', 20000, '100码')
# print(c2)
#
# print(c1 == c2)
# print(c1 > c2)


# 实例属性和类属性
#
# class Car:
#
#     wheel = 4 # 轮胎数量
#     tat_rate = 0.1 # 购置税
#     name = '长城'
#
#     def __init__(self, name, price):
#         self.name = name
#         self.price = price
#
# c1 = Car('BMW', 20000)
# c2 = Car('BMW', 20000)
#
# print(c1.wheel, c1.name)
# print(c2.wheel, c2.name)
