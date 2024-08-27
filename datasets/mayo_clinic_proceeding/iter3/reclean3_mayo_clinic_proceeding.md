reclean3_mayo_clinic_proceeding

reclean2_mayo_clinic_proceeding分析报告

reclean2目前存在较多的误删问题原因

1.正则第21条# [r'(.*[\s\.]\d{4}\.?$)',r'删除21:<u>\1</u>'],  # 删除末尾为年份的句子,在这里我想删除那些具有末尾年份特征的无关的句子但是无关的句子明显不多但是造成的误删很多，需要删除

2.正则第19条，删除19是为了删除一些特殊形式的数字，但是需要避开次幂的表示，修改删除19

预计能解决80%的误删提升8分

无关文本通过添加正则预计解决60%，提升1.2分

预计能提升9.2分质量分达到95分以上达到封板标准

整段删除 

补充 Potential Competing Interests|Closing 后面为无关内容

行级删除

针对特殊的情况添加正则

```
[r'^(The authors report no competing interests|We thank Dr Padda for his interest in our article|Adapted by).*',r''],
[r'^[:;.,!]$',r''],   # 单行只有一个标点
[r'(<sup>[a-z\d\s–]{10,20}</sup>)',r'删除23:<u>\1</u>'], 
```