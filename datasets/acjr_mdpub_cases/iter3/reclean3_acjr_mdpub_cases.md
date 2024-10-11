## reclean2_acjr_mdpub_cases问题
### 错误删除：
1.删除6删除段尾无关数字，9，10|、|1，21等误删小数，及表格内容。修改补充，取消删除在句子\.前。修改为：
```
[r'( ?[，\-\|]*(\d+[，\-\|])+(\d+)?)$', r'删除6:<u>\1</u>'],
```

2.删除7删除参考文献样式，误删正文内容，在年份\d{4}前补充非数字，后补充限制字符50。修改为：
```
[r'(^.{0,100}[^\d]\d{4}[;；：\.]\w+(\(\d+\))?[:：；]?[\w\-]+.{0,50})', r'删除7:<u>\1</u>'],
```

3.删除5删除类似￥口22284 盟- H02 目可23，误删较多，进行补充修改，限制必须出现中文，且字符数目有限。修改为：
```
[r'(^[\w\\\]\[ ￥\-]{0,20}[\u4e00-\u9fff][\u4e00-\u9fff\w\\\]\[ ￥\-]{0,}[^\.\n]{0,30}$)', r'删除5:<u>\1</u>'],
```

4.结尾段落References：里有的正文内容，没有提取出来拼接，造成误删。move_ref_confusion函数调整优化。

a. 补充拼接结尾是右括号)和]的情况。
```
r'([a-zA-Z，\d\.\)\]])(\n\n(Re[tf]erences?：?|REFERENCES?：?\n\n)[\W\w]*?\n\n)((\\?\-?[a-zA-Z\(].*|Conclusions?)\n\n)([\W\w]*?\n\n\d+\\?\.)'
```

b. 补充不符拼接的参考文献格式Eating Disorders， 7：573-579.
```
r'(\d{4}[;；： \.]+\d+(\(\d+\))?[:：； ]*[\d\-]+)|(https?[：:]\/\/)|(\d+(\(\w+\))?[:：； ]*\d+[\-]\d+)'
```

5.通用间距删除误删正文，继续补充结束判定条件，当下一段有两句话且每句字符长度大于60时不删除。排除Patients and Methods类似中间有and链接的标题。
```
start_to_end = [
        [r'(^[\\ #]*(Copyright @))', r'(^[\\ #]*([A-Z][A-Za-z]+( and)?( [A-Z][A-Za-z]+)?)[\\ #]*$)|(^.{250,})|(^[a-z]{1,3}.{75,}\.$)|(^([A-Z][\w ()]{50,}\. ?){2,})', 0],
        [r'(^[\\ #]*(DOI：))', r'(^[\\ #]*([A-Z][A-Za-z]+( and)?( [A-Z][A-Za-z]+)?)[\\ #]*$)|(^.{250,})|(^[a-z]{1,3}.{75,}\.$)|(^([A-Z][\w ()]{50,}\. ?){2,})', 0],
        [r'(^[\\ #]*(Full?-text ))', r'(^[\\ #]*([A-Z][A-Za-z]+( and)?( [A-Z][A-Za-z]+)?)[\\ #]*$)|(^.{250,})|(^[a-z]{1,3}.{75,}\.$)|(^([A-Z][\w ()]{50,}\. ?){2,})', 0],
        [r'(^[\\ #]*(Author[s\'’ ]*[Aa]ddress：|\d?Corresponding [Aa]uthors?：))', r'(^[\\ #]*([A-Z][A-Za-z]+( and)?( [A-Z][A-Za-z]+)?)[\\ #]*$)|(^.{250,})|(^[a-z]{1,3}.{75,}\.$)|(^([A-Z][\w ()]{50,}\. ?){2,})', 0],
        ]
```

### 无关文本：
1.删除2补充删除无关段落，开头为Internal Medicine、National Center of Cancer、Conflict of interest、Name of Department 。。。done、Faculty of Medicine，。。。等。
```
[r'(^(Full?-text |Copyright|DOI：|(Name of |[\dl]? ?)?Department |Dr\. |organizations， or those of the publisher|New York Chiropractic and|Publisher[\'s ]*note：|Corresponding author：|Internal Medicine (.*)?Department|Conflict of interest|National Center of Cancer|[A-Z][a-z]+ of Medicine，).*)', r'删除2:<u>\1</u>'],
```

2.无Reference标题的参考文献补充删除，类似1\.Schwingel PA 。。。。.Liver Int，2一元011；3：348-53的格式。delete_page_ending中ending_starts 规则修改\d{4}为\d{3,4}。
```
[r'(^(\d|l)\\?\..*\d{3,4}[;；：\.] ?\w+(\(\d+\))?[:：\.；]?[\w \-]+.*)']
```

**1010补充：**

1.补充通用结尾段落删除，Authors'contributions、Institution Where Work Was Done、CONFLICT OF INTEREST：、COMPETING INTERESTS、Department and Institution Where Work Was Done、Authors' Statements、TAKE HOME MESSAGE、AUTHORS'CONTRIBUTIONS、PATIENT CONSENT、Ethical approval：、Acknowledgements Conflicts of interest、Authors'Declaration等。ending_starts里补充：
```
ending_starts = [
            [r'^[#\*]{0,4}\s?(Re[tf]erences?：?|REFERENCES?：?|Funding( Sources| Statement| and Disclosure)?|Polls on Public|Ethics (committee )?[Aa]pproval|Author[s\'’ ]*([Cc]ontribution|[Ss]tatement|[Dd]eclaration)|Acknowledge?men[t1]：?|(Acknowledgements )?Conflicts? of [Ii]nterest|Source of (Support|Funding)|(Financial )?[Dd]isclosure|(Disclosure |Ethics )?Statement|Declaration of Figure[s\'’ ]*Authenticity|Competing [Ii]nterest|Declaration|Patient informed consent|(Department and )?Institution Where Work Was Done|CONFLICT OF INTEREST：|COMPETING INTERESTS|PATIENT CONSENT|TAKE HOME MESSAGES?|AUTHOR[S\'’ ]*CONTRIBUTIONS?|Ethical approval：?|Authorship)s?[#\*]{0,4}\s{0,}($|\n)'],
            [r'(^(\d|l)\\?\..*\d{3,4}[;；：\.] ?\w+(\(\d+\))?[:：\.；]?[\w \-]+.*)']
        ]
```

2.无Reference标题的参考文献补充删除，3\. Clin 。。。November 2010，95：E384-E391：、4\. Roessler E，。。。Genetics， 2005， Vol. 14， No. 15
```
[r'(\d+\\?\..*\d{3,4}[;；，：\.] ?\w+(\(\d+\))?[:：\.；]?[\d \-]+.*)', r'删除9:<u>\1</u>'],
```

3.无关括号内容(image 1)、(image2)、(Video 1)等。
```
[r'([\(（]([Ii]mage|[Vv]ideo) \d+[）\)])', r'删除10:<u>\1</u>'],
```

4.LAO 51CC、B LAO51 0030、a.、b.等字母数字点构成的无关段落。
```
[r'(^((\w+( ([A-Z]+\d+|\d+[A-Z]+))+( \w+)*)|(\w\.?))$)', r'删除11:<u>\1</u>'],
```

5.补充删除无关段落，开头为We would like to acknowledge、We would like to thank、Joana Vilaca*1， Sofia Miranda*，、*Servigo de Pediatria do Hospital de Braga、Video 1. Pulsation of、Clemenceau Medical Center 等。
```
[r'(^(We would like to (acknowledge|thank)|Joana Vilaca\\\*1，|\\\*Servigo de Pediatria|Video \d+\.|Clemenceau Medical Center).*)', r'删除12:<u>\1</u>'],
```

6.Author’s address： 的无关段落群，delete_page_middle通用间距删除里start_to_end补充：
```
[r'(^[\\ #]*(Author[s\'’ ]*[Aa]ddress：))', r'(^[\\ #]*([A-Z][A-Za-z]+( [A-Z][A-Za-z]+)?)[\\ #]*$)|(^.{250,})|(^[a-z]{1,3}.{75,}\.$)|(^([A-Z][\w ()]{50,}\. ?){2,})', 0],
```

7.image i、image 2、image 3无关段落。穿插在正文里，导致多余换行，直接删除。
```
[r'(^[Ii]mage (\d+|i)$)', r'']
```

**1011补充：**

1.·T、K.1A domen PeLCE、None、B./A、LEFT无关段落。直接删除。
```
[r'(^(Alreheili KM. et al：|[Ii]mage (\d+|i)|·T|K.1A domen PeLCE|PEL|None\.?|B\.\/A|LEFT)$)', r''],
```

2.删除12补充感谢段，The authors gratefully thank 。。。、There are no conflicts of interest.、No financial support of any kind was granted.、O Am J Case Rep， 2022； 23：e937052、1\\. van Riet EES， Hoes AW，、age size：、Abdomen venoes Axial、FUFFWO\\_、Series：等。
```
[r'(^(We would like to (acknowledge|thank)|Joana Vilaca\\\*1，|\\\*Servigo de Pediatria|Video \d+\.|Clemenceau Medical Center|The authors gratefully thank|There are no conflicts|No financial support of|O Am J Case Rep|1\\. van Riet EES， Hoes AW，|age size：|Abdomen venoes Axial|FUFFWO\\_|Series：).*)', r'删除12:<u>\1</u>'],
```

3.1Corresponding author： 的无关段落群，delete_page_middle通用间距删除里start_to_end补充：
```
[r'(^[\\ #]*(Author[s\'’ ]*[Aa]ddress：|\d?Corresponding [Aa]uthors?：))', r'(^[\\ #]*([A-Z][A-Za-z]+( and)?( [A-Z][A-Za-z]+)?)[\\ #]*$)|(^.{250,})|(^[a-z]{1,3}.{75,}\.$)|(^([A-Z][\w ()]{50,}\. ?){2,})', 0],
```

4.包含Department的标题，以及包含Department of或者Tel：或邮箱的小段落。Institution and Department Where Work Was Performer、satyendrapersaud@yahoo.com Tel： 447741051578等。
```
[r'((^(?=.{0,75}$).*Department.*)|(^(?=.{0,150}$).*(Department of|Tel：|@[a-z]{2,10}\.com).*))', r'删除14:<u>\1</u>'],
```

5.段落开头有字符中文的情况，删除中文字符。
```
[r'(^[\u4e00-\u9fff]+)', r'删除16:<u>\1</u>'],
```

6.删除零碎段落，B0ml i.v. KM、venos、ittleEndianExplicit、Images、1/102。
```
[r'(^([a-z][\w]{0,20}|[\d\/]{1,10}|Images|B0ml i.v. KM)$)', r'删除17:<u>\1</u>'],
```

### 多余换行：
1.表格插入导致的多余换行，补充下端开头是大写的特定情况，限制字符且有句号，防止误拼接。
```
context = re.sub(r'([a-zA-Z，\d\--])(\n+\n((Supplementary )?Table|\|) [\W\w]*?)(\n+\n)(([a-z\(][^ \--].*)|([A-Z][a-z]{2,10}\..{100,}))', r'\1删除表格换行\6\2', context)
```

2.上下颠倒的多余换行段落，就是上一段应该拼接到下一段的结尾。上一段是more小写开头，正常结尾。下一段是大写正常开头，连字符-结尾。
more， a prompt 。。。。patients.
This case 。。。。 changes. Further-
move_duan函数里添加正则，调整位置拼接：
```
context = re.sub(r'([^|\n]{80,}\.\n+\n)([a-z][^|\n]{50,}\n+\n)([A-Z][^|\n]{50,}[a-z\-])(\n+\n)([A-Z][^|\n]{50,}|\n\s*|$|[\u4e00-\u9fff]{2,})', r'\1\3|删除上下换行|\2\5', context)
```




