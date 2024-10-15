## reclean3_acjr_mdpub_cases问题
### 无关文本：
1.补充删除开头为Picture的图片介绍段落，Picture 1： The tumour was、Picture 2A et 2B： Radiography of等。
```
[r'(^#*\s?([Ff]igs?(ure)?|F\s?IGS?(URE)?|Picture \d).*)', r''],
```

2.无关图注，\[picture、\[picture 2A， 2B\]、\[picture 1J。
```
[r'((\\?[\[]picture[^\]\.\\]*\\?[\]J])|(\\\[picture))', r'删除18:<u>\1</u>'],
```

**1014补充：**

1.补充通用结尾段落删除，ACKNOWLEDGEMENTS、Funding program、Conflits of interest等。ending_starts里补充：
```
[r'^[#\*]{0,4}\s?((Acknowledgements )?Conflic?ts? of [Ii]nterest|ACKNOWLEDGEMENTS?|Funding program)s?[#\*]{0,4}\s{0,}($|\n)'],
```

2.ICorresponding author： Khalid 的无关段落群，delete_page_middle通用间距删除里start_to_end补充：
```
[r'(^[\\ #]*(Author[s\'’ ]*[Aa]ddress：|[\dIl]?Corresponding [Aa]uthors?：))', r'(^[\\ #]*([A-Z][A-Za-z]+( and)?( [A-Z][A-Za-z]+)?)[\\ #]*$)|(^.{250,})|(^[a-z]{1,3}.{75,}\.$)|(^([A-Z][\w ()]{50,}\. ?){2,})', 0],
```

3.包含 Center的无关短小段落，Denver Health Medical Center， Denver， CO， U.S.A.，删除14补充：
```
[r'((^(?=.{0,75}$).*(Department| Center).*)|(^(?=.{0,150}$).*(Department of|Tel：|@[a-z]{2,10}\.com).*))', r'删除14:<u>\1</u>'],
```

4.作者感谢，补充类型，The authors thank and acknowledge。
匹配开头补充为：```The authors?( gratefully)? thank```

5.提取引用里的正文内容包含图注，Figure 1. Hypocellular。。。，优化move_ref_confusion函数里else判断模块。

**1015补充：**

1.补充通用结尾段落删除，Ethical Committee Approval：、Main Institute for the Cases、Competing Interest Nil.、Declaration of Tables Authenticity、Institution where work was done、Statement of Ethics、Institutional review board statement、Ethics approval and informed consent、Refences：、Authors'contributions：等。ending_starts里补充：
```
[r'^[#\*]{0,4}\s?(Re[tf]e?r?ences?：?|REFERENCES?：?|Funding ?(Sources|Statement|and Disclosure|program)?|Polls on Public|Ethic(s|al) ([Cc]ommittee )?[Aa]pproval：?( and informed consent)?|Author[s\'’ ]*([Cc]ontributions?：?|[Ss]tatement|[Dd]eclaration)|Acknowledge?men[t1]：?|(Acknowledgements )?Conflic?ts? of [Ii]nterest|Source of (Support|Funding)|(Financial )?[Dd]isclosure|(Disclosure |Ethics )?Statement( of Ethics)?|Declaration of (Figure[s\'’ ]*|Tables )Authenticity|Competing [Ii]nterest( Nil\.)?|Declaration|Patient informed consent|(Department and )?Institution [Ww]here [Ww]ork [Ww]as [Dd]one|CONFLICT OF INTEREST：|COMPETING INTERESTS|PATIENT CONSENT|TAKE HOME MESSAGES?|AUTHOR[S\'’ ]*CONTRIBUTIONS?|Authorship|ACKNOWLEDGEMENTS?|Main Institute for the Case|Institutional review board statement)s?\.?[#\*]{0,4}\s{0,}($|\n)'],
```

2.结尾段落References：里有的正文内容，提取无关的参考出来拼接，造成无关文本。move_ref_confusion函数调整优化。

a. 补充不符拼接的参考文献格式Island， FL： Statpearls Publishing， 2018

无关正则补充：```([;；： ，\.]+(20|1[6-9])\d{2}$)```

b. 补充引用标题Refences：的情况。

c. 优化补充拼接结尾是-的情况。

3.包含 et al的无关短小段落，Mazen M. et al：、Gopal J.P. et al.：等，删除14补充：
```
[r'((^(?=.{0,75}$).*(Department| Center|et al).*)|(^(?=.{0,150}$).*(Department of|Tel：|@[a-z]{2,10}\.com).*))', r'删除14:<u>\1</u>'],
```
4.无关短小段落，PTima、lmage 2、lmage 6，补充删除：
```
[r'(^(Alreheili KM. et al：|[Iil]mage (\d+|i)|·T|K.1A domen PeLCE|PEL|None\.?|B\.\/A|LEFT|PTima)$)', r''],
```

5.不规则的括号内图注，[Figure 71、(Figure 7A-7F]。
```
[r'((\\?[\[\(]Figure[^\]\.\\]*\\?[\]1lJ])|(\\\[Figure))', r'删除19:<u>\1</u>'],
```

6.括号内人名出版时间，(Melo et al.， 2005)、(Kusmiyati， 2009)等。
```
[r'([（\(][^\)\(（）]*[， ,](20|1[6-9])\d{2}[\)）])', r'删除20:<u>\1</u>'],
```

### 错误删除：
1.删除7误删正文内容，\d前补充不是/和±符号，并添加结尾符。
```
[r'(^.{0,100}[^\d\/±] ?\d{4}[;；：\.]\w+(\(\d+\))?[:：；]?[\w\-]+.{0,50}$)', r'删除7:<u>\1</u>'],
```

2.通用间距删除误删正文内容，补充排除小写开头的长度大于72字符句号.结尾的段落。

补充结束特征：```(^[a-z]{1,3}.{72,}\.)```






