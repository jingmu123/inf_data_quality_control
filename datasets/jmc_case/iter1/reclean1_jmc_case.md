## reclean0_jmc_case问题
### 无关文本：
1.| Click to view |。。。。。、| Click for large image |。。。。。等无关段落。
```
[r'(^\| ?Click.*\n.*)', r'删除1:<u>\1</u>'],
```

2.| **Discussion** | ▴Top |、| Case Report | ▴Top |、| Introduction | ▴Top |等形式标题，保留标题文本，去除 | ▴Top |。
```
[r'(^\| ([^|]*) \| ▴Top \|\n\| \-+ \| \-+ \|)', r'\2'],
```

3.文末段落删除补充，Financial Support、Conflict of Interest、Conflicts of Interest、Source of Support、Financial Support等无关段落。
```
ending_starts = [
    [r'^[#\*]{0,4}\s?(Reference|Funding and Disclosures|Polls on Public|Ethics Approval|Authors?\'? Contribution|Acknowledge?ment|Financial Support|Conflicts? of Interest|Source of Support|Financial Support)s?[#\*]{0,4}\s{0,}($|\n)'],
]
```

4.\[ 8 \- 10 \]、\[ 7 \- 10 \]、\[ 7 , 11 \- 13 \]等括号内带\的补充删除。
通用删除6补充：
```
[r'((\\)?\[[\d\s\\,，\–\-—]{1,}(\\)?\])', r'通用删除6(英):<u>\1</u>'],
```

5.Supplementary Material补充材料及例举Suppl 1. Clinical characteristics等删除。
```
[r'(^Supplementary Material *$)', r'删除2:<u>\1</u>'],
[r'(^Suppl ?\d+\..*)', r'删除3:<u>\1</u>'],
```

**0918补充：**

1.文末段落删除补充，| Grant Support | ▴Top |、Disclosure、Grant、Competing Interests、Source of Funding、Poster Presentation、Financial Disclosure Statement、Financial Support and Disclosure、Declaration of Interest等无关段落。
```
ending_starts = [
    [r'^[#\*]{0,4}\s?(Reference|Funding and Disclosures|Polls on Public|Ethics Approval|Author[s\' ]*Contribution|Acknowledge?ment|Financial Support|Conflicts? of Interest|Source of Support|(\| )?Grant Support.*|Disclosure|Grant|Competing Interest|Source of Funding|Poster Presentation|Financial Disclosure Statement|Financial Support and Disclosure|Declaration of Interest)s?[#\*]{0,4}\s{0,}($|\n)'],
```


