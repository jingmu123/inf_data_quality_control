reclean1_hindawi_case

reclean0中标注的问题基本全是无关文本的问题

无关文本的形式固定，比较好删除，预计本次清洗直接能达标

无关文本

```
[r'(\(([Ff]igs?(ure)?|F\s?IGS?(URE)?)[^\(\)]*(\([^\(\)]{0,5}\)[^\(\)]*){0,}\))',r'删除1:<u>\1</u>'],   # 删除带括号的(Figure ...(a)...(b)),括号里面可能嵌套其他的括号
[r'(^((\s){0,}(\([\da-z]\)|©)(\s){0,}){1,}($|\n))',r''],  # 删除类似于选项（a）出现在一个图片描述的下面应该是图片中（a）（b）...指对的某些地方
[r'',r''] , # 特殊符号
```

无关断尾的删除，利益冲突、数据可用性、作者的贡献...

```
r'^[#\*\s]{0,}(Consent|Conflicts of Interest|Data Availability|Authors Contributions|Authors’? Contribution|Ethical Approval)s?($|\n)'
```