#coding:utf-8
# import re
# a="的包括: 1. 头部 : 颈动脉及其分支如颜浅"
# pattern = [r'([:：]\s?)(\d+[\.、]\s?[\u4e00-\u9fa5])',r'\1\n增加换行24:_\2_']
# # print(re.findall(pattern[0], a))
# print(re.sub(pattern[0],pattern[1],a))

import jieba
tests = "所有工作组成员填写得利益"
print(list(jieba.cut(tests, cut_all=False)))
