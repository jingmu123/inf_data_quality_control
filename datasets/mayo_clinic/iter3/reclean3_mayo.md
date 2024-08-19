reclean2_mayo清洗报告

reclean2清洗率达到89.67%，93.89694分

存在错误删除和无关文本错误

解决错误删除和部分无关文本，并删除了标签，再标注一次，预计下一版可以清洗合格封板



reclean3_mayo

误删问题

误删问题集中在描述et al句子上

```
改进et al特征的删除 
[r'.*\s?et[\s\xa0]{1,3}al.*',r'删除7:<u>\1</u>'],
↓
[r'([\(\[][^\(\)\[\]]*\set[\s\xa0]{1,3}al[^\(\)\[\]]*[\)\]])',r'删除6:<u>\1</u>'],  et al加括号的情况
[r'.*,\s?et[\s\xa0]{1,3}al.*',r'删除6:<u>\1</u>'],   et前面有,出现，这样就不会误删一些句子中本该存在的et al
```

无关文本问题

```
添加一些固定描述的句子 大多时出版社相关
    [r'(Drug information provided by: Merative, Micromedex.*)',r''],   # 描述出版信息，与下一条规则一起用
    [r'(#{1,3} US Brand Name)',r''],
    [r'(^US Food & Drug Administration.*\n.*)',r''],
    [r'(Date:.*)',r''],
    [r'(^Warning letter to.*)',r''],
    [r'(^Public Health Service.*)',r''],
    [r'(^Cerebyx.*)',r''],
    [r'(.*(doi|DOI)\s?:)',r''],            # 存在有DOI描述的句子
```