# 字面量的写法

print(100)
print(3.14)
print(True)
print(False)
print('Hello Python')
print("------------------------")
print(None)

print(True + 1)
print(True - 1)
print(True * 1)

print(False + 1)
print(False - 1)


# 变量

num = 1114.1

print(num)

num = 1115

print(num)

num = 'ok'

print(num)

num = True

print(num)


# 完成如下需求，现在有两个变量，分别为：a=10,b=20,现需要将这两个变量的值交换，然后输入到控制台。

a = 10
b = 20
# a, b = b, a
# print(a)
# print(b)

c = a

a = b

b = c

print(a)
print(b)

# 查看数据类型

print(type(10))
print(type(3.14))
print(type('10'))
print(type(True))
print(type(None))
print(type(None).__name__)
print(type(None) is None)
print(type(10) is int)
print(type(10.6) is float)
print(type(True) is bool)
print(type('3.14') is str)


# 字符串

print("你好，我叫'python' ")
print(''' 你好，我叫'python' ''')
print('你好，我叫\'python\' ')
print("欢迎大家开始学习Python,\n大家一定要认真学习哦")


# f-string
name = 'along'
age = 20

print(f'我叫{name}')

print(f'name={name}, age={age}')
print(f'{name=}, {age=}')


# 输入与输出
name = input('请输入您的姓名:')
print(name)