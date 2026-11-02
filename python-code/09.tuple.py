t1 = (5, 7, 9, 1, 2, 3, 10, 6, 4, 8, 12, 7, 5)

print(t1[0], t1[-2])

list1=[123,456]
tuple1=('两点水','twowater','liangdianshui',list1)
print(tuple1)
list1[0]=789
list1[1]=100
print(tuple1)


tuple1=('两点水','twowter','liangdianshui',[123,456])
print(tuple1)
del tuple1


t2 = (1,3,5,7)
t3 = (2,4,6,8)

a,b,c,d = t2

print(a,b,c,d)

x, *y, z = t2
print(x,y,z)

x,*o = t2
print(x,o)