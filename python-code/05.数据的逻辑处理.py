# 条件判断

# 1.提示用户输入账号和密码
# 2.判断账号和密码是否正确，如果账号和密码都正确，则登录成功，则进入首页
# 3.如果账号和密码有一个错误，则登录失败，提示错误信息

# account = '18888888888'
# password = '6666'
#
# account_ok = input('请输入你的账号')
# password_ok = input('请输入你的密码')
#
# if(account_ok == account and password_ok == password):
#     print('登录成功')
# else:
#     if(account_ok != account):
#         print('账号不正确')
#     elif(password_ok != password):
#         print('密码不正确')
#     else:
#         print('账号和密码都不正确')
#

# 模式匹配

day = input('请输入星期几(1-7)：')

match day:
    case '1':
        print('星期一')
    case '2':
        print('星期二')
    case '3':
        print('星期三')
    case '4':
        print('星期四')
    case '5':
        print('星期五')
    case '6' | '7':
        print('星期天')
    case _:
        print('输入错误：', day)


