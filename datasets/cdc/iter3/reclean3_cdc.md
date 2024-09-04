## reclean2_cdc问题
### 错误删除：
1.括号内有用内容误删，(reported in <5% of cases, most commonly dengue fever; Appendix Table 2)等。

将原正则：```[r'([\(（][^\(\)（）\n]*(strain|TOX|comm\.|Figure|Table|Appendix|[Nn]o\.|[Ss]ee|Video)[^\(\)（）\n]*[\)）])', r'删除4:<u>\1</u>']```,
修改为：```[r'([\(（][^\(\)（）\n]*(TOX|comm\.|[Nn]o\.|Video)[^\(\)（）\n]*[\)）])', r'删除4:<u>\1</u>'],
[r'([\(（][  \t]*(toll|[Ss]ee|[Ff]ig|[Tt]able|[Aa]ppendix|Technical)[^\(\)（）\n]*[\)）])', r'删除4-1:<u>\1</u>'],
[r'([\(（][^\(\)（）\n]*?)(([,;] *([Ss]ee|[Ff]ig|[Tt]able|[Aa]ppendix|Technical)[^\(\)（）\n,;]*)+)([^\(\)（）\n]*[\)）])', r'\1删除4-2:<u>\2</u>\5'],```
为了防止漏删，删除4-2:在去标签时复制一条运行两次。

2.文章中有图表说明的，it is not suitable for the SARS epidemic in Canada illustrated in Figure 1 .The estimates start to converge after June 4, in the last 2 rows of Table 3 in bold, yielding an estimate for _K_ of 248.96 (95% CI 246.67–251.25). 
经讨论保留，原正则删除。


### 无关文本：
1.人物介绍补充删除。
```
[r'([^\n]*(\n[  \t\*]*(Drs?|M[sr][sr]?|Prof|Col\. G|Hanna Y|Carmen C\.H|S\.C\.A\.C)\.?[^\.]* (is|received|[Rr]esearch(ers)?|works?) )[^\n]+)', r'删除9:<u>\1</u>'], 
```

2.文章开头无关段落补充。
```
[r'([\w\W]*)(\n[  \t#]*(Abstract|(LTAS )?Background)\n)', r'删除6:<u>\1</u>(以上都删除)\2'],
```

3.CHC 16, team leader、CHC 4, team leader等
```
[r'(CHC \d+, team leader)', r'删除15:<u>\1</u>'],
```

4.一些特定无关段落补充。
```
[r'(\n[  \t\*#]*(Of 107 manuscripts|Members of the CDC Brazil Investigation Team:|Top |Public Health and pharmacy:|On This Page|Dial |CAS#:|Image source:)[^\n]*)', r'删除8:<u>\1</u>'], 
```

**0904补充：**
### 错误删除：
1.一些文章后面的表格及表格说明需要保留，判断表格是否存在。
```
def step2_del_paragraph(self, context):
    patter1 = r'(\n[  \t#]*(Acknowledgments|References?|Author Information)[  \t]*\n[\w\W]*)(\n[  \t#]*Tables[  \t]*\n)'
    patter2 = r'(\n[  \t\*#]*(Fast Facts\n\nFirearm|[a-z]+ icon\n|Bibliography|Appendix\n|ADDITIONAL RESOURCES|Safety & Health Outcomes)[\w\W]*)(\n[  \t#]*Tables[  \t]*\n)'
    patter3 = r'(\n[  \t\*#]*(Figure|Appendix|Footnotes|Video)[^\n]*)'
    patter4 = r'(\n[  \t\*#]*(Figure|Table|Appendix|Footnotes|Video)[^\n]*)'
    if len(re.findall(r'\|', context)) >= 7 and re.search(r'(\n[  \t#]*Tables[  \t]*\n)', context):
        context = re.sub(patter1, r'(以下都删除1，到表格为止)<u>\1</u>\3', context)
        context = re.sub(patter2, r'(以下都删除2，到表格为止)<u>\1</u>\3', context)
        context = re.sub(patter3, r'删除5:<u>\1</u>', context)
    else:
        context = re.sub(patter4, r'删除5:<u>\1</u>', context)
    return context
```

2.was supported by会误删段落内容，修改为：
```
[r'([^\n\.]*((was|are) supported (in part )?by )[^\n\.]*)', r'删除12:<u>\1</u>'],
```
