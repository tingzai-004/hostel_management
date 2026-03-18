1.  #把 lst = [1,2,3,4,5,6,7,8,9,10] 中所有偶数变成它的2倍
# 预期：[2, 4, 8, 12, 20]
lst = [1,2,3,4,5,6,7,8,9,10]

# lst=[2*x for x in lst if x%2==0 ]
# print(lst)

# s="hrllo,word"
# s=s.capitalize()
# print(s)





# 2.  把 每个单词变成大写并加感叹号
# # 预期：['HELLO!', 'WORLD!', 'PYTHON!', 'DJANGO!']
lst=['hello', 'world', 'python', 'django']
result=[word.title()+'!' for word in lst]
print(result)

a='hellp'
a=a.title()
print(a)


# 3.  把 中所有负数变成0，正数不变
# # 预期：[0, 0, 1, 2, 8, 0, 0]
lst = [-5,-3,1,2,8,-9,0] 

result=[x if x>0 else 0 for x in lst]
print(result)


# 4.  把  生成所有可能的二元组 (i,j) 其中 i < j
# # 预期：[(1,2),(1,3),(1,4),(1,5),(2,3),(2,4),(2,5),(3,4),(3,5)]

nums = [1,2,3,4,5]
result=[(i,j) for i in nums for j in nums if i<j ]
print(result)
# 5.  把 生成字典 {'a':'1','b':'2','c':'3'}
s = "abc"
t = "123"

print(result)
# 输出：{'a': '1', 'b': '2', 'c': '3'}


# 6.  把  生成新列表，只保留大于等于5的数，且全部加10
# # 预期：[15, 19, 16]
lst = [3,1,4,1,5,9,2,6]
result=[i+10 for i in lst if i>=5]
print(result)

# 7.  把矩阵  展平成一维列表
# # 预期：[1,2,3,4,5,6,7,8,9]
matrix = [[1,2,3],[4,5,6],[7,8,9]]
result=[j for i in matrix for j in i]
reult1=sum(matrix,[])
print(result,reult1)

# 8.  把 lst = ["alex","wusir","taibai","ritian"] 中名字包含'a'的变成"帅哥"
# # 预期：['帅哥', 'wusir', '帅哥', 'ritian']
lst = ["alex","wusir","taibai","ritian"]
result=['帅哥' if 'a'in name else name for name in lst ]



# 9.  把  生成 [1,9,25,49,81] （奇数的平方）
lst = [1,3,5,7,9]
result=[i**2 for i in lst if i%2!=0]
print(result)


# 10. 把  生成每个单词的长度列表
# # 预期：[5, 5, 6]
lst = ["hello","world","python"]
result=[len(i) for i in lst ]
print(result)
lst=['hello', 'world', 'python', 'django']
lst=str(lst)
print(lst)