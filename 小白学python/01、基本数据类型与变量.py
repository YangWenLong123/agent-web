# # 判断一个数据是否为整数

# a = 10

# if a > 0:
#   print("a是正整数")
# else:
#   print("a不是正整数")


# print('两点水')
# print("两点水")
# print('''两点水''')

# print(" 两'点'水 ")
# print(''' 两"点"水 ''')

# print('两\'点\'水')
# print("两\"点\"水")

# print('''
# 两
# 点
# 水
# ''')

# print('' \
# '两' \
# '点' \
# '水' \
# '')

# print(False == 0)

# num1 = 1 + 2
# num2 = 1 - 2
# num3 = 1 * 2
# num4 = 1 / 2

# print(num1, num2, num3, num4)
# print(type(num1), type(num2), type(num3), type(num4))
# print(type(num1).__name__, type(num2).__name__, type(num3).__name__, type(num4).__name__)

# print(None is None, None is not None, None == None, None != None, None is False, None is True, None == False, None == True, None == '', None == 0, None == [], None == {}, None == set(), None == (), None == object(), None == type(None), None == type(1), None == type(''), None == type([]), None == type({}), None == type(set()), None == type(()), None == type(object()), None == type(type(None)), None == type(type(1)), None == type(type('')), None == type(type([])), None == type(type({})), None == type(type(set())), None == type(type(())), None == type(type(object())))

# name = "小白学python"
# age = 18

# # 字符串格式化输出
# print(f"昵称:{name}", f'昵称:{name}', f'''昵称:{name}''')
# print(f"{name=}, {age=}")

# # 数字格式化输出
# a = 3
# b = 4

# print(f"{a+b=}, {a-b=}, {a*b=}, {a/b=}, {a//b=}, {a%b=}, {a**b=}")

# # 浮点数格式化输出
# pai = 3.14159

# print(f"{pai:.2f}, {pai=:.2f}, {pai:.3f}")


# # 右对齐、左对齐、居中占30个字符宽
# print(f"[{ name:>30}]", f'[{name:<30}]', f'''[{name:^30}]''')


# # 千分位分隔符
# money = 123456789
# print(f'订单金额:{money:,}元')

# # 百分号格式
# rate = 0.875
# print(f"完成率:{rate:.2%}", f"完成率:{rate:.1%}")

# data = {"name": "小白学python", "age": 18}

# print(f'昵称是：{data["name"]}, 年龄是：{data["age"]}')

# name = '水哥'
# age = 28
# # 用 f-string 拼成一句话，赋值给 intro 并打印
# print(f"我叫{name}，今年 {age} 岁。")

# str1 = '100'
# str2 = '200'
# print(str1 + str2)  # 字符串拼接
# print(int(str1) + int(str2))  # 转成整数后相加

# print(int(88.888))  # 浮点数转整数，取整

# a = b = c = 100

# a,b, c = 100, 200, 300

name = [1,2,3,4,5,6,7,8,9]

print(name[0:2])  # 切片，取索引0到索引2之间的元素，不包含索引2
print(name[:2])  # 切片，取索引0到索引2之间的元素，不包含索引2
print(name[:]) # 切片，取索引0到索引len(name)之间的元素，不包含索引len(name)
print(name[2:5])  # 切片，取索引2到索引5之间的元素，不包含索引5

# 更新列表
name[1] = 22
print(name)

# 添加数据
name.append(10)
print(name)

# 删除元素
del name[0]
print(name)

del name[1:3]  # 删除索引1到索引3之间的元素，不包含索引3
print(name)

# 获取列表长度
print(len(name))  # 获取列表长度
print([1,2,3] + [4,5,6])  # 列表拼接
print([1,2,3] * 2)  # 列表重复
print(1 in [1,2,3])  # 检查元素是否在列表中

print(enumerate([1,2,3]))

for key, x in enumerate([1,2,3]): print(key, x)  # 遍历列表

# List 列表函数方法

x = [1,2,3,4,5,6,7,8,9]

x.append(10)

print(len(x), max(x), min(x))

x.insert(2, 11)

print(x)

print(x.pop(), x.pop(2))  # 删除最后一个元素,返回删除的元素
print(x)

x.append(1)
print(x)

x.remove(1) # 删除列表中第一个出现的元素1

print(x)

print(x.index(2)) # 返回元素2在列表中的索引位置

print(x.count(2)) # 统计某个值在列表中出现的次数

print(x)

x.reverse()

print(x) # 反转列表

x.sort() # 排序列表

print(x) # 反转列表

x.sort(reverse=True)

print(x) # 反转列表

y = sorted(x)

print(y) 

y = sorted(x, reverse=True)

print(y) 


# 元组， 有序列表，不可修复

tuple1 = (1,2,3)
tuple2 = 4,5,6

print(tuple1, tuple2, type(tuple1), type(tuple2))

# 元组中只包含一个元素时，需要在元素后面加上一个逗号，否则会被认为是一个普通的括号表达式

tuple3 = (1,)

print(tuple3)

a = 1
b = '2'
c = [1,2,3]

tuple4 = (a, b, c)

print(tuple4)

# a = 11
# b = '22'
# c = [11,22,33]

c[0] = 11

print(tuple4)  # 元组中的元素是不可变的，但是元组中的可变对象是可以修改的

del tuple4

list1 = [1,2,3]

list2 = tuple(list1)

print(list2)

list3 = list(list2)

print(list3)

dict1 = {'name': '小白学python', 'age': 18}

print(len(dict1))
print(dict1.keys())
print(dict1.values())
print(dict1.items())

print(dict1.get('name1', 1))  # 如果键不存在，返回None

dict1.pop('age')  # 删除键值对

print(dict1)

dict1.clear()

print(dict1)