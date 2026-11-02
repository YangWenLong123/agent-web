import main
# import utils.my_fun

print(main.count)
print(main.add_count())
print(main.add_count())
print(main.add_count())

# print(utils.__author__)
#
# utils.my_fun.log_separator1()
#
#
# from utils.my_fun import log_separator1,log_separator2
#
# log_separator1()
# log_separator2()


# 注意：通过这个种方式导入包下面所有模块，需要在__init__.py文件中添加__all__=[]
from utils.my_fun import *

log_separator1()

