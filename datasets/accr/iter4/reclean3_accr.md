## reclean3_accr问题
### 无关文本：
1.Video 1： Video of Case 1视频注释。
```
[r'(^Video \d+.*)', r'删除15:<u>\1</u>'],
```

2.| Figure 2： Sagittal proton density fast spin echo表格中无用的图片介绍。
```
[r'(^\| [Ff]igs?(ure)?[\w\W]*)', r'删除16:<u>\1</u>']
```

3.文末段落删除补充，Ethics Approval and Consent to Participate、Availability of Data and Materials等无关段落。
```
ending_starts = [
    [r'^[ #]*(Reference|Ethics Approval|Author[s\' ]*Contribution|Acknowledge?m ?ent|Funding|Funding Sources|Research Funding|Pseudomembranous Tracheobronchitis|Disclosure|Declaration|Permission|Institutional Review Board Statement|Consent( for Publication)?|Ethics Approval and Consent to Participate|Availability of Data and Materials)s?[ #]*($|\n)'],
]
```

4.无关字母或数字成段，(A) (B)。
```
[r'(^\(\w+\) ?\(\w+\)$)', r'删除17:<u>\1</u>']
```

### 多余换行：
1.句子开头为句号.，补充删除换行连接上一段。
```
context = re.sub(r'([a-z\-\d])(\n\n)( *\.)', r'\1删除3换行\3', context)
```

2.补充段落开头是）的情况，与上段连接。
```
context = re.sub(r'([a-z，\-\d])(\n\n)([a-z\)])',  r'\1删除1换行\3', context)
context = re.sub(r'([^|\n]{100,})(\n\n)( *[a-z\)])', r'\1删除2换行\3', context)
```

3.表格插入导致多余换行，补充上一段是大写字母结尾，下段是小写字母的情况。
```
context = re.sub(r'([a-zA-Z，\d])(\n\n((Supplementary )?Table|\|) [\W\w]*?)(\n\n)(([a-z\(]).*)', r'\1删除表格换行\6\2', context)
```

4.修改补充上一段是小写字母结尾，下一段是大写开头，但不是标题或者Table的多余换行。
```
[r'[^|]{100,}[a-z]#*$', r'^#*(?!Table)[A-Z][^|]{35,}\.[^|]*']
```

**0919补充：**

### 无关文本：
1.补充删除英文文本中出现的中文字。
```
context = re.sub(r'([\u4e00-\u9fff]+ | [\u4e00-\u9fff]+)', r'删除8:<u>\1</u>', context)
```

2.补充删除无关段落，Special thanks、References values、Department of、Arindam Sur、Robert Stenberg等。
```
[r'(^(We thank|Special thanks?|References values|Department of|Arindam Sur|Robert Stenberg).*)', r'删除12:<u>\1</u>'],
```

3.补充删除无关文本，1A 2B 3C、87-891-2182：等。
```
[r'(^(\(\w+\) ?\(\w+\)|\d\w( \d\w)+|[\d\-]+：)$)', r'删除17:<u>\1</u>']
```

4.句末无关数字删除，9，10|.、11-14、11|. 、7-11.、|15，16.、 11，25-32.、21，24等。
```
[r'( ?[，\-\|]*(\d+[，\-\|])+(\d+)?(\.|$))', r'删除18:<u>\1</u>\4'],
```





