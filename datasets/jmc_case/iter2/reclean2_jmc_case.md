## reclean1_jmc_case问题
### 无关文本：
1.开头为Figure的图片描述段落删除。
```
[r'(^#*\s?([Ff]igs?(ure)?|F\s?IGS?(URE)?).*)', r'删除4:<u>\1</u>'],
```

2.文末段落删除补充，Disclaimer、Declaration of Competing Interests、Declaration、Disclaimers、Disclaimer、Declaration、Conflict of Interest Statement、Authors’ Contributions、Financial Disclosure、Funding Statement、Funding、Place of the Study、Funding Sources、Conflict of Interest and Funding Sources、Dedication、Acknowledgement and Funding等无关段落。
```
ending_starts = [
    [r'^[#\*]{0,4}\s?(Reference|Funding ?(and Disclosures|Statement|Sources)?|Polls on Public|Ethics Approval|Author[s\'’ ]*Contribution|Acknowledge?ment( and Funding)?|Financial Support|Conflicts? of Interest( Statement| and Funding Source)?|Source of Support|(\| )?Grant Support.*|Disclosure|Grant|Competing Interest|Source of Funding|Poster Presentation|Financial Disclosure( Statement)?|Financial Support and Disclosure|Declaration( of (Competing )?Interest)?|Disclaimer|Place of the Study|Dedication)s?[#\*]{0,4}\s{0,}($|\n)'],
]
```

3.Supplementary Material 1.、Supplementary Material 2.等。
```
[r'(^Supplementary Material \d.*)', r'删除2-1:<u>\1</u>'],
```

4.表格形式的图片、表格描述，|  Figure 1. Serial。。。、| Table 1. Cellular Immunological。。。
```
[r'(^\| *([Ff]igs?(ure)?|Table)[\w\W]*)', r'删除4-1:<u>\1</u>'],
```



