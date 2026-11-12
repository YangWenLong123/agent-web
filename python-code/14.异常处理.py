# print(10 / 0)
# print('程序执行完成')
# nums = [1, 2, 3]
# print(nums[10])

# try:
#     result = 10 / 0
#     print(result)
# except ZeroDivisionError:
#     print('哎呀，除数不能是零')
#
# print('程序继续运行')


def parse_age(s):
    try:
        age = int(s)
        return 100 / age
    except ZeroDivisionError:
        return '年龄不能是 0'
    except ValueError:
        return '输入的不是数字'


print(parse_age('25'))
print(parse_age('0'))
print(parse_age('abc'))