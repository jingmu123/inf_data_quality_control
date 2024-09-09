reclean2_oxford

reclean1_oxford报告

reclean1中77.333%，91.60426主要为无关文本的问题，主要为文章末尾的一些句子

预计本次的清洗能解决90%以上的无关文本，能提升8分左右，主要是通过率的提升，预计能提升到90以上

无关文本，主要为文章结尾一些内容需要删掉，特征主要是一些大写的词语，这里之前没有删掉是因为这里的单词好像有拼写错误，已经全为大写的情况导致我们之前没有包含到

```
# sudo 添加文章末尾删除主要为大写
r'^ACKNOWLEDGMENT(S)?',   #感谢
r'^ACKNOWLEDGEMENT(S)?(\n|$)',  # 单行只有一个ACKNOWLEDGEMENTS以下的需要删除
r'^AVAILABILITY OF DATA AND MATERIAL(\n|$)',  # 单行AVAILABILITY OF DATA AND MATERIAL全为大写
r'^(CONFLICTS? OF INTEREST STATEMENT|CONFLICTS?(ING)? OF INTEREST|Confict of Interest statement)',# 单行利益冲突CONFLICT OF INTEREST STATEMENT 全为大写
r'^(FINANCIAL DISCLOSURES/)?FUNDING(\n|$)',  # 拨款
r'^(ETHICAL|ETHICS) APPROVAL',  # 伦理...
r'^DATA AVAILABILITY',  # 数据可用性
r'^SUPPLEMENTARY MATERIAL',  # 补充材料
r'^ACKNOWLEGE?MENTS?',  # 感谢
r'^AUTHORS’ CONTRIBUTIONS?',  # 作者补充
```

带有视频的无关带括号

```
[r'([\.,;][^\.,;]*\s([Vv]ideo|VIDEO|Fig)s?[\s\.:][^\(\)]*\))', r')'],    # Vidio   ...视频带括号只需删除后半句
[r'(\([^\(\)]*\s([Vv]ideo|VIDEO)s?[\s\.:][^\(\)]*\))', r'删除1:<u>\1</u>'],  # Vidio   ...视频带括号
```



ccri多余换行的解决，首先需要对开头为Figure的描述进行删除，因为这些内容将正常的句子阶段，调用类中封装好的more_line_feed方法解决换行

```
pattern_list = [
    [r'^[#\*]{0,4}\s?([Ff]igs?(ure)?|F\s?IGS?(URE)?).*',r''],   # 删除开头为Figure的描述
]

pattern_more_line_feed = [
    [r'\s?[^\.,!?|]\s?[#\*]{0,4}$',r'^[#\*]{0,4}[a-z]'],        # 上一段非标点结尾，下一段小写开头
    [r'(The|A)\s?[#\*]{0,4}$'],   #  上一段结尾是A或者The 下一段一定要连上
]
```