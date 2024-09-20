 reclean2_hindawi_case_label

reclean1结果分析

reclean1中还存在一些需要多段删除文章结尾，这次添加了几个特征词语

除多段删除的文章结尾外，还有一些固定格式的table描述，因为没有表的存在只有表的描述，所以这里选择删掉

预计已发现的无关文本基本都能解决，可提升到95分左右

删除文章结尾特征的补充

```
r'^[#\*\s]{0,}(Consent|Conflicts of Interest|Data Availability|Authors Contributions|Authors’? Contribution|Ethical Approval|Disclosure|Competing Interest|Additional Point|Disclosure)s?($|\n)'
↓
r'^[#\*\s]{0,}(Consent|Conflicts of Interest|Data Availability|Authors Contributions|Authors’? Contribution|Ethical Approval)s?($|\n)'
```

删除固定格式的table描述的补充

```
[r'(^[\*#]{0,4}([Ff]igs?(ure)?|F\s?IGS?(URE)?)[\*#]{0,4}\s?\d+.*)', r'通用删除16(英):<u>\1</u>'],
↓
[r'(^[\*#]{0,4}([Ff]igs?(ure)?|F\s?IGS?(URE)?|Table|TABLE)[\*#]{0,4}\s?\d+.*)', r'通用删除16(英):<u>\1</u>'],
```