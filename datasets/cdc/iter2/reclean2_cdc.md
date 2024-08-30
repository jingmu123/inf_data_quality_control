## reclean1_cdc问题
### 错误删除：
1.Related Pages导致的误删，
大部分Related Pages已被删除6删除，将此条正则```[r'(\n[  \t]*(Related Pages)[\w\W]*)', r'以下都删除2:<u>\1</u>']```删除。

2.括号内有四个数字的内容误删。

将正则删除4修改为：```[r'([\(（][^\(\)（）\n]*(Figure|Table|Appendix|[Nn]o\.)[^\(\)（）\n]*[\)）])', r'删除4:<u>\1</u>']```

0829补充：
3.人物介绍误删，补充一些规则。
```
[r'((\n[  \t]*(Drs?|M[sr][sr]?|Prof|Col\. G|Hanna Y)\.?[^,\.]* is )[^\n]+)', r'删除9:<u>\1</u>'], 
```

### 无关文本：
1.补充文章开头Figure的漏删。
```
[r'(^\**(Figure|Table|Appendix)[^\n]*)', r'删除5-2:<u>\1</u>'],
```

2.补充et al. 后面的 ( _2_ )页码数字。
```
[r'(et al\.)( *[\(（][\d\-,～~;–—、\s_]+[\)）])', r'\1删除1-1:<u>\2</u>'],
```

3.无关段落补充，Fast Facts、**icon、Bibliography、Appendix\n
```
[r'(\n[  \t\*#]*(Fast Facts\n\nFirearm|[a-z]+ icon\n|Bibliography|Appendix\n)[\w\W]*)', r'以下都删除2:<u>\1</u>'],
```

4.括号内补充see、Video、
```
[r'([\(（][^\(\)（）\n]*(Figure|Table|Appendix|[Nn]o\.|[Ss]ee|Video)[^\(\)（）\n]*[\)）])', r'删除4:<u>\1</u>'],
```

5.补充带#图注，脚注Footnotes、 Video、
```
[r'(\n[  \t\*#]*(Figure|Table|Appendix|Footnotes|Video)[^\n]*)', r'删除5:<u>\1</u>'],
```

6.Author(s):、Pages:、以上内容删除。
```
[r'([\w\W]*\n[  \t]*(Author\(s\):|Pages:)[^\n]+)', r'<u>\1</u>\n(以上都删除2)'],
```

7.无关文本特定删除，Back to top、
```
[r'(Back to top)', r'删除11:<u>\1</u>'],
```

8.成员删除，补充COVID-19 Registries Study Group members:、Sources:、
```
[r'(\n[  \t\*#]*(Author contributions:|Author Affiliations:|COVID-19 Registries Study Group members:|Sources:)[^\n]*)', r'删除7:<u>\1</u>'],
```

9.句中图表描述，补充删除句中带小数0.05等.
```
[r'([^\n\.]*?((\d\.\d)[^\n\.]*?)*((Figure|Table|Appendix)[\d\-～~–—\. _]+shows?| (in|from) (Figure|Table|Appendix) \d)[^\n]*?\.)([ \n])', r'删除5-1:<u>\1</u>\8'],
```


0830补充：
1.was supported in part by
```
[r'([^\n]*(was supported in part by)[^\n]*)', r'删除12:<u>\1</u>'],
```

2.人物介绍补充**Dr.及上一句的人名全称。
```
[r'([^\n]*(\n[  \t\*]*(Drs?|M[sr][sr]?|Prof|Col\. G|Hanna Y|Carmen C.H)\.?[^,\.]* is )[^\n]+)', r'删除9:<u>\1</u>'],
```

3.补充另一种形式的致谢Acknowledgments、引用References、作者信息Author Information等无关段落。
```
[r'(\n[  \t#]*(Acknowledgments|References?|Author Information)[  \t]*\n[\w\W]*)', r'以下都删除3:<u>\1</u>'],
```

4.补充_Suggested citation for this article:_以上内容删除
```
[r'([\w\W]*\n[  \t]*(Author\(s\):|Pages:|_Suggested citation for this article:_)[^\n]+)', r'<u>\1</u>\n(以上都删除2)'],
```

5.无关段落补充，ADDITIONAL RESOURCES、Safety & Health Outcomes
```
[r'(\n[  \t\*#]*(Fast Facts\n\nFirearm|[a-z]+ icon\n|Bibliography|Appendix\n|ADDITIONAL RESOURCES|Safety & Health Outcomes)[\w\W]*)', r'以下都删除2:<u>\1</u>'],
```

6.句中图表描述，补充复数形式Figures、Tables，补充in Technical Appendix Table 1.，补充Figure 2 reports。
```
[r'([^\n\.]*?((\d\.\d)[^\n\.]*?)*((Figures?|Tables?|Appendix)[\d\-～~–—\. _]+(shows?|reports?)| (in|from)[\w ]+(Figures?|Tables?|Appendix) \d)[^\n]*?\.)([ \n])', r'删除5-1:<u>\1</u>\9'],
```

7.一些特定无关段落修改补充，Dial、Image source:
```
[r'(\n[  \t\*#]*(Members of the CDC Brazil Investigation Team:|Top|Public Health and pharmacy:|Box\.|On This Page|Dial |Image source:)[^\n]*)', r'删除8:<u>\1</u>'],
```

8.删除12 补充are supported by情况。
```
[r'([^\n]*((was|are) supported (in part )?by )[^\n]*)', r'删除12:<u>\1</u>'],
```

9.删除\[A tabular version of this figure is also available.\]、[ Source: 2019 AR Threats Report ]。
```
[r'(\\?\[[^\[\]]*(Source:|[Ff]igure)[^\[\]]*\])', r'删除13:<u>\1</u>'],
```

10.It is almost worth buying the book for these 10 pages alone.
```
[r'(It is almost worth buying[^\n]*)',  r'删除14:<u>\1</u>'],
```

11.括号内补充(。。。。comm.)、(strain 92 Bardos)、(TOX A/B II ELISA; TechLab, Blacksburg, VA, USA)等形式。
```
[r'([\(（][^\(\)（）\n]*(strain|TOX|comm\.|Figure|Table|Appendix|[Nn]o\.|[Ss]ee|Video)[^\(\)（）\n]*[\)）])', r'删除4:<u>\1</u>'],
```

### 页码/数字：
1.句末括号无关数字，段末无关数字。
```
[r'([\(（][\d\-,～~;–—、\s_]+[\)）])([\.,;])', r'删除1-2:<u>\1</u>\2'],
[r'(\d[\d\-,～~;–—、_]*)(\n)', r'删除1-3:<u>\1</u>\2'],
```