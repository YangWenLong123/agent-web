# 集合set

s1 = {1, 3, 4, 2, 6, 7, 1}

print(s1, type(s1))

# 字典

d1 = { '王林': 100, '李木婉': 200, '徐立国': 105, (1,2): 1 }

# del d1[(1,2)]
#
# print(d1)
#
# d1.clear()
#
# print(d1)

# 字典的方法

print(len(d1))
print(str(d1), type(str(d1)))

print(d1.values())

print(d1.popitem())

print(d1.items(), list(d1.items()))

print(d1.keys(), list(d1.keys()))

print(d1.values(), list(d1.values()))