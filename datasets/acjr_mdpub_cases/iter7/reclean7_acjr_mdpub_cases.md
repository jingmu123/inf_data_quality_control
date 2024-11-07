## reclean6_acjr_mdpub_cases问题
### 多余换行：
1.部分需要特殊处理的多余换行。

a. 上段小写字母结尾，下段7).开头，1 month (month(\n换行\n)7). A decrease in 。

b. 上段小写字母结尾，下段\-开头，at 3/10 (sphere(\n换行\n)\-1.25=cylinder-1.0 axis 180°) with。

c. 上段&结尾，下段数字开头，，patients (3.16±2.48 mg/dL &删除3换行1.33±0.1 mg/dL) with。
```
context = re.sub(r'([^|\n]{50,}[a-z\-\d，\=\&])(\n+\n *)(\.|\\\[|\d+\.\d+ ?(\%|\)|mg\/|±)|\d+\)\.|\\\-)', r'\1删除3换行\3', context)
```
2.单独成段的无关文本未删除导致的多余换行未删除，40×.直接删除。
```
[r'(^(40×\.)$)', r'删除17:<u>\1</u>'],
```

3.表格插入换行。

a. 补充上段%结尾的情况，failure and asystole may develop in 3%(\n表格插入\n)of the cases.

b. 补充下段44.2±开头的情况，with a mean age of(\n表格插入\n)44.2±20 years. The mean age at 。
```
context = re.sub(r'([a-zA-Z，\d\-\%])(\n+\n((Supplementary )?Table|\|) [\W\w]*?)(\n+\n)(([a-z\(][^ \--].*)|([A-Z][a-z]{2,10}\..{100,})|(\\\[|\d+\.\d+ ?(\%|\)|mg\/|±).*))', r'\1删除表格换行\6\2', context)
```

### 无关文本：
1.通用结尾删除遗漏，ending_starts里补充Conflict of interest statement、Declaration of Figures； Authenticity、Ethical Permission、CONSENT等。
```
[r'^[#\*]{0,4}\s?((Acknowledgements )?Cc?onflic?ts? of [Ii]nterest( and source of funding| statement)?|Declaration of (Figure[s\'’ ；]*|Tables )Authenticity|Ethical Permission|CONSENT)s?[：\.]?[#\*]{0,4}\s{0,}($|\n)'],
```

2.无关段落，We gratefully acknowledge the writing。。。、Abstract of this work。。。，删除12补充。
```
[r'(^((We|The authors) (would like to|gratefully) (acknowledge|thank)|Abstract of this work).*)', r'删除12:<u>\1</u>'],
```

3.括号内无关网址，(Boundless.“Boundless Microbiology." Lumen Learn-ing， Lumen Learning，courses.lumenlearning.com/boundless-microbiology/chapter/functions-of-antimicrobial-drugs/)。
```
[r'([（\(][^\)\(（）]*\.com\/[^\)\(（）]*[\)）])', r'删除24:<u>\1</u>'],
```

4.无关句子， A guide to drug safety can be found on the Porphyria Drug Safety Finder website at www.porphyr-、iadrugs.com.直接删除。
```
[r'(A guide to drug safety can be found.*)', r''],
```

5.通用结尾删除遗漏，ending_starts里补充Role of funding source、FUNDING、Department and Institution Where Work Was Performed。
```
[r'^[#\*]{0,4}\s?((Department and )?Institution [Ww]here [Ww]ork [Ww]as ([Dd]one|[Pp]erformed)|Role of funding source|FUNDING)s?[：\.]?[#\*]{0,4}\s{0,}($|\n)'],
```

6.结尾段落References：里有的正文内容，提取无关的参考出来拼接，造成无关文本。move_ref_confusion函数调整优化。

将引用里每个匹配开头的字母数量由```(\\?\-?[a-zA-Z\(]```改为```(\\?\-?[a-zA-Z\(]{2}```。

7.无关段落，iadrugs.com.、(b)、(a)、(C)。直接删除。
```
[r'(^(iadrugs\.com\.|\(\w\))$)', r'删除17:<u>\1</u>'],
```

8.结尾或者文中Ethical Consideration的段落，只有Conclusion结尾的段。
```
context = re.sub(r'(Ethical [Cc]onsiderations?\n\n.*(\n\n|$))', r'', context)
context = re.sub(r'(Conclusion\n*$)', r'', context)
```

9.段落结尾的图例，the parabasal part of the anterior wall - Fig. 2 and 3.
```
[r'( - Fig\. 2 and 3\.$)', r'删除26:<u>\1</u>.'],
```

10.致谢段落遗漏，We thank RCSI-Bahrain for。。。、The author is grateful to Takahiro Suzuki and。。。等
```
[r'(^(The author is grateful to|We thank ).*)', r''],
```












