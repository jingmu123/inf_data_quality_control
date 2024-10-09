reclean2_journal-pile

reclean1_journal-pile清洗分析通过率82.943%，质量分95.17828

reclean1中存在{'错误删除': 10, '多余标点': 49, '无关文本': 42}

其中无关文本和多余标点通过添加正则已解决90%，质量分上提升空间已不大，只要是通过率的提升，本组数据的数据量较大，需要多抽几次数据

错误删除，修改规定删除

在通用删除2前加一条删除，删处带有括号的et al的情况

```
[r'(.*,\s?et[\s\xa0]{1,3}al.*)', r'通用删除2(英):<u>\1</u>'],  # , et al   et al一版在一些人名后面，一定要加逗号，如果没有逗号可能会造成一些误删
↓
[r'(\([^\(\)]*,\s?et[\s\xa0]{1,3}al[^\)\(]*\))', r''],    # 带有括号, et al   et al一版在一些人名后面，一定要加逗号，如果没有逗号可能会造成一些误删
[r'(.*,\s?et[\s\xa0]{1,3}al.*)', r'通用删除2(英):<u>\1</u>'],  # , et al   et al一版在一些人名后面，一定要加逗号，如果没有逗号可能会造成一些误删
```

修改通用删除7，这里又出现10(9)括号里面出现次幂的表述不能将(9)当作数字引用删除

```
[r'((\\)?\([\d\s,\\，\-\–—]{1,}(\\)?\))', r'通用删除7(英):<u>\1</u>'],  # 带有圆括号的数字引用

[r'([^\d](\\)?\([\d\s,\\，\-\–—]{1,}(\\)?\))', r'通用删除7(英):<u>\1</u>'],  # 带有圆括号的数字引用
```



无关文本的删除

添加正则

```
[r'(\([^\(\)]*\s?et[\s\xa0]{1,3}al[^\)\(]*\))', r''],    # 带有括号, et al   et al一版在一些人名后面，一定要加逗号，如果没有逗号可能会造成一些误删
[r'(\\)?\[[\s,\.]{0,5}(\\)?\]',r''],      # 空\[\]  或者中间有个空格或标点
[r'(\(\[[^\[\(\)\]]*\]\))',r'删除30:<u>\1</u>'],   # 删除前面删除剩余的一些([...])的表述
[r'(\([^\(\)]*([Ff]igs?(ure)?|F\s?IGS?(URE)?|Table|[sS]ee|Appendix)s?[\s\.:\d][^\(\)]*\))', r''],# 最广泛的形式从左括号匹配到右括号
[r'(\[[^\[\]]*([Ff]igs?(ure)?|F\s?IGS?(URE)?|Table|[sS]ee|Appendix)s?[\s\.:\d][^\[\]]*\])', r''],# 最广泛的形式从左方括号匹配到右方括号
[r'(\([\s,\.]{0,5}\))',r''],     # 空()
```

添加文章结尾删除，补充ending_starts列表

```
ending_starts = [
    [r'^[#\*]{0,4}\s?(References?：?|Funding( Sources| Statement| and Disclosure)?|Polls on Public|Ethics Approval|Author[s\' ]*Contribution|Acknowledge?ment|Conflicts? of [Ii]nterest|Source of (Support|Funding)|Supplementary (Material)?)s?[#\*]{0,4}\s{0,}($|\n)'],
    [r'^.{0,10}(Competing [Ii]nterest|Funding|Source of Support|Supporting information|Availability of data and materials|Financial support and sponsorship|conflict of interest|Acknowledgement|Reporting summary|Disclosure|Supplementary information|Disclosure statement|Author contribution|Conflict of interest statement|Ethics|Conflicts of Interest|Data Availability|Data sharing statement).{0,10}(\n|$)s?'],
    [r'^The author has served']

]
```

多余标点，多余标点是由于删除了一些方括号或圆括号里面的内容之后将括号留下，做一个，通过正则删除