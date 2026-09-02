# 编写一个商品结算程序：

price = float(input('请输入商品的价格：'))
count = int(input('请输入商品的数量：'))
is_card = input("是否成为会员(是/否):") == '是'

total = price * count
discount = 0.8 if is_card else 1.0
final_price = total * discount

print(f'商品总价为: {total:.2f} 元')
print(f'是否为会员: {is_card}')
print(f'最终结算价格为: {final_price:.2f} 元')