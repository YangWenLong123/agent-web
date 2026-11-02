# 列表

list1 = [1, 'hello', 3.14, True, None]
print(list1, type(list1))


name = ['一点水', '两点水', '三点水', '四点水', '五点水']

del name[0]

print(name)


# 列表切片
s = ["A", "C", "E", "B", "D", "E", "G"]
num = [1,3,5,7,9, 2]
name = 'along'

print(s[0:5:2])

# 列表的方法

# 获取列表的长度
print(len(s))

# 获取列表的最大值和最小值
print(max(num))
print(min(num))

# 将可迭代的对象转化为列表
print(list(name))

# 在列表末尾添加数据
s.append('K')
print(s)

# 统计某个元素在列表中出现的次数
countA = s.count('A')
print(countA)

# 将可迭代对象的元素逐个添加在列表末尾
s.extend('LOVEK')

print(s)

# 返回第一个匹配到元素的索引
index = s.index('K')
print(index)

# 在指定索引位置插队对象
s.insert(1, 'Hello')

print(s)

# 移除并删除指定索引位置的元素，默认为最后一个
s.pop(1)

print(s)

# 移除第一个匹配到的元素
s.remove('K')
print(s)

# 反转列表元素
s.reverse()
print(s)

# 原地排序数组
num.sort()
print(num)

# 将用户输入的10个数字，存储到一个列表中，并将列表中的数字进行排序，输出其中的最小值、最大值和平均值。

# l = []
# sum1 = 0
#
# while len(l) < 10:
#     value = input(f'请输入第{len(l) + 1}个数字')
#     l.append(int(value))
# else:
#     print('恭喜你，10个数字已经输入完成，最终列表为：', l)
#     l.sort()
#     print('重新排序为：', l)
#     print(f'最大值是{max(l)}')
#     print(f'最小值是{min(l)}')
#     # for i in l:
#     #     sum1 += int(i)
#     print(f'平均值是: {sum(l) / len(l)}')


# 合并两个列表并去重

s1 = [1,2,3,4,5,6]
s2 = [4,5,6,7,8,9]

# s3 = s1 + s2
# s3 = set(s3)
# print(s3)

s3 = [*s1, *s2]
print(s3)


"""
    案例：
        1.生成1-20的平方列表。
        2.从如下数字列表中提起所有偶数，并计算其平方，组成一个新的列表
"""

num_list2 = [19,23,54,64,87,20,109,232,123,43,26,55,72]
num_list = [num ** 2 for num in range(1,21)]

for num2 in num_list2:
    if num2 % 2 == 0:
        num_list.append(num2 ** 2)

num_list.sort()

print(num_list)


"""
    案例：
        从一个数字列表中提取所有偶数，并计算平方，组成一个新的列表
"""

num_list3 = [12,32,45,77,80,92,33,57,97,98]

new_list = [ x**2 for x in num_list3 if x % 2 == 0 ]

print(new_list)