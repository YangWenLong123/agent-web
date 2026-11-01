# while循环,打印10遍hello,world

i = 0

while i<10:
    print(f'第{i + 1}遍，hello,world')
    i+= 1
else:
    print('循环结束')


# for循环

msg = 'hello world'

for i in msg:
    print(i)
else:
    print('循环结束了')

dic = { 'name': 'along', 'age': 18 }

print(dic)

for k,v in dic.items():
    print(k, v)


# msg1 = input('请输入要遍历的字符串')
#
# for s in msg1:
#     print(s)
# else:
#     print('遍历结束了')

# 计算1-100之间所有奇数之和

i = 1
count = 0

while i <= 100:
   if (i + 1) % 2 == 0:
       count += i
   i += 1

print('循环结束了', count)

count2 = 0

for i in range(1, 101):
    if i % 2 != 0:
        count2 += i
else:
    print('循环结束了', count2)

count3 = 0

for i in range(1, 101, 2):
    count3 += i
else:
    print('循环结束了', count3)

count4 = 0

for i in range(100, 500):
    if i % 3 == 0:
        count4 += i
else:
    print(f'100-500之间所有的数字和为:'+ str(count4))


# 嵌套循环

# 打印一个长度为m,宽度为n的长方形

# m = int(input('请输入长方形的长度'))
# n = int(input('请输入长方形的宽度'))
#
# for j in range(n):
#     for i in range(m):
#         print('*', end = ' ')
#     print()
#
#

for i in range(1, 10):
    for j in range(1, i + 1):
        print(str(j) + '*' + str(i) + '=' + f'{i*j}' , end=' ')
    print()


"""
    案例：根据输入的用户名和密码执行登录操作，具体要求如下：
        1.正确的用户名为admin/666，zhangsan/666
        2.输入用户名和密码进行登录，直到登录成功，程序结束运行；如果登录失败，则继续输入用户名和密码进行登录
        2.输入的用户名和密码不能为空
        3.登录成功：输出“登录成功”
        4.登录失败：输出“用户名或密码错误，请重新输入”
"""

# while True:
#     user_name = input('请输入用户名')
#     password = input('请输入密码')
#
#     if  user_name == '' or  password == '':
#         print('输入的用户名和密码不能为空')
#         continue
#
#     if user_name == 'admin' and password == '666':
#         print('登录成功')
#         break
#     elif user_name == 'zhangsan' and password == '666':
#         print('登录成功')
#         break
#     else:
#         print('用户名或密码错误，请重新输入')


"""
    案例：猜数字游戏
        1.系统随机生成一个随机数
        2.用户根据提示猜数字，并将所猜的数字输入系统
        3.如果猜错，系统给出提示是猜大了，还是猜小了，然后继续输入猜的数字
        4.如果猜对了，系统自动退出，游戏结束
"""
import random

random_num = random.randint(1, 100)

# print('系统生成的随机数是：', + random_num)

while True:
    num = int(input('请输入要猜的数字'))

    if num > random_num:
        print('数字猜大了')
    elif num < random_num:
        print('数字猜小了')
    elif num == random_num:
        print('恭喜你猜对了')
        break

