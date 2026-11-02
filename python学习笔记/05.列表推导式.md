## 列表推导式

列表推导式（List Comprehension）是一种通过遍历可迭代对象，按规则生成新列表的简洁写法。它可以在生成元素时进行计算、转换或筛选。

### 1.基本语法
```python
新列表 = [表达式 for 变量 in 可迭代对象]
```

| 部分 | 作用 | 示例 |
| --- | --- | --- |
| 表达式 | 决定放入新列表的值 | `x * 2` |
| 变量 | 接收每次遍历得到的元素 | `x` |
| 可迭代对象 | 提供要遍历的数据 | `nums`、`range(5)`、字符串等 |

- 例如，把列表的每个数字都乘以2:

```python
nums = [1, 2, 3, 4, 5]
result = [x * 2 for x in nums]
print(result) # [2, 4, 6, 8, 10]
```
注意：最前面的表达式决定最终列表中保存什么。

```python
nums = [1, 2, 3]

# 保存元素本身
a = [x for x in nums]
# [1, 2, 3]

# 保存元素的平方
b = [x ** 2 for x in nums]
# [1, 4, 9]

# 每遍历一次，都保存固定值 0
c = [0 for x in nums]
# [0, 0, 0]
```

### 2.使用if筛选元素

如果只想保留满足条件的元素，可以在末尾添加 if：

```python
[表达式 for 变量 in 可迭代对象 if 条件]
```
例如，筛选偶数：

```python
nums = [1, 2, 3, 4, 5, 6]
result = [x for x in nums if x % 2 == 0]
print(result) # [2, 4, 6]
```

也可以同时进行筛选和计算

```python
nums = [1, 2, 3, 4, 5, 6]
result = [x ** 2 for x in nums if x % 2 == 0] # 这里是先筛选偶数，再计算平方。
print(result) # [4, 16, 36]
```

多个条件可以用 `and`、`or` 组合：

```python
# 选出大于 3 且为偶数的数字
result = [x for x in range(1, 11) if x > 3 and x % 2 == 0]
print(result) # [4, 6, 8, 10]
```

### 3.使用 if...else 决定生成什么值
如果希望每个元素都得到处理，只是不同条件生成不同结果，可以使用条件表达式：

```python
[值1 if 条件 else 值2 for 变量 in 可迭代对象]
```
例如，把数字转换为“偶数”或“奇数”：

```python
nums = [1, 2, 3, 4, 5]
result = ["偶数" if x % 2 == 0 else "奇数" for x in nums]
print(result) # ['奇数', '偶数', '奇数', '偶数', '奇数']
```

对应的普通循环：
```python
result = []
nums = [1, 2, 3, 4, 5]

for x in nums:
    if x % 2 == 0:
        result.append("偶数")
    else:
        result.append("奇数")
```

这两种 if 的区别很重要：

| 写法 | 作用 | 对元素数量的影响 |
| --- | --- | --- |
| `[x for x in nums if 条件]` | 筛选元素 | 可能减少 |
| `[值1 if 条件 else 值2 for x in nums]` | 决定每个元素生成什么值 | 每个输入元素生成一个结果 |


记忆方式：
- 末尾的 if：决定要不要这个元素。
- 前面的 if...else：决定这个元素变成什么。

### 4.常见的使用场景

1. 字符串转换：
```python
words = ["python", "java", "go"]
result = [word.upper() for word in words]
print(result) # ['PYTHON', 'JAVA', 'GO']
```
2. 去除字符串两端的空白：
```python
names = [" Alice ", " Bob", "Charlie "]
result = [name.strip() for name in names]
print(result) # ['Alice', 'Bob', 'Charlie']
```

3. 把数字字符串转换为整数：
```python
users = [
    {"name": "小明", "age": 18},
    {"name": "小红", "age": 20},
    {"name": "小刚", "age": 16},
]
names = [user["name"] for user in users if user["age"] >= 18]
print(names) # ['小明', '小红']
```

4. 遍历字符串：
```python
letters = [char for char in "Python"]
print(letters) # ['P', 'y', 't', 'h', 'o', 'n']
```

### 5.多个 for：相当于嵌套循环
列表推导式中可以写多个 for：
```python
[表达式 for 变量1 in 对象1 for 变量2 in 对象2]
```
例如，生成所有组合：

```python
result = [(x, y) for x in [1, 2] for y in ["a", "b"]]

print(result)
# [(1, 'a'), (1, 'b'), (2, 'a'), (2, 'b')]
```
等价于：
```python
result = []

for x in [1, 2]:
    for y in ["a", "b"]:
        result.append((x, y))
```
> 多个 for 从左到右，对应普通循环从外到内。

一个常见应用是将二维列表展开成一维列表：

```python
matrix = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9],
]

result = [num for row in matrix for num in row]

print(result) # [1, 2, 3, 4, 5, 6, 7, 8, 9]
```

### 6.嵌套列表推导式：生成二维列表
如果希望结果仍然是二维列表，可以把一个推导式放进另一个推导式：
```python
matrix = [[0 for col in range(3)] for row in range(2)]

print(matrix) # [[0, 0, 0], [0, 0, 0]]
```
理解方式：
```python
# 内层：生成一行，包含 3 个 0
[0 for col in range(3)]

# 外层：执行 2 次，每次创建一行
[[0 for col in range(3)] for row in range(2)]
```
当循环变量用不到时，通常写成 `_`：
```python
matrix = [[0 for _ in range(3)] for _ in range(2)]
```

### 7.常见错误与注意事项
1. 筛选用的 if 后面不能直接接 else。
```python
# 错误写法
[x for x in nums if x > 0 else 0]
```
如果要把非正数变成 0，应该写成：
```python
[x if x > 0 else 0 for x in nums]
```
