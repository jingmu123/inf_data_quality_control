## reclean0_accr问题
### 无关文本：
1.Fig.3： Postoperative.等图片注释。
```
[r'(^#*\s?([Ff]igs?(ure)?|F\s?IGS?(URE)?).*)', r''], 
```

2.Full-text PDF https、Copyright @ 2021 by、DOI：10.5455/IJMRCR、1Department of Internal、l Department of Cardiology、Department and Institution
```
[r'(^(Full-text |Copyright|DOI：|[\dl]? ?Department ).*)', r'删除2:<u>\1</u>'],
```

3.文末段落删除补充，REFERENCES：、References：、Financial disclosure、Conflict of interest、Funding、Disclosures
```
ending_starts = [
    [r'^[#\*]{0,4}\s?(References?：?|REFERENCES?：?|Funding( Sources| Statement| and Disclosure)?|Polls on Public|Ethics Approval|Author[s\' ]*Contribution|Acknowledge?ment|Conflicts? of [Ii]nterest|Source of (Support|Funding)|(Financial )?[Dd]isclosure)s?[#\*]{0,4}\s{0,}($|\n)'],
]
```

4. Adress： Centro Hospital、 E-mail：marta isa pinheiro@hotmail.com、Phone number： +351225501111、Received：、Accepted：、 Editor：
```
[r'(.*(Adress|E-mail|Phone number|Received|Accepted|Editor)[：:].*)', r'删除3:<u>\1</u>'],
```

5.文章开头段落删除补充，ABSTRACT：、 Introduction： Orofacial clefts 、Background：、ABSTRACT Riga Fede等。
```
end_pattern = [
    [r'(^[#\s]*(Abstract|ABSTRACT)：?\s*)', 0],
    [r'(^[#\s]*(Background|Introduction)：?\s*)', 0],
]
```

6.无关文本，A B、1A 2B 3C、87-891-2182：等。
```
[r'(^(\(\w+\) ?\(\w+\)|\d\w( \d\w)+|[\d\-]+：|\w( \w)*)$)', r'删除4:<u>\1</u>'],
```

7.无关中文，口 十1281 十十 07、口2188 \]2 山白 12、
```
[r'(^[\u4e00-\u9fff\d\\\]\[ ]+$)', r'删除5:<u>\1</u>'],
```

### 多余换行：
1.引用References：插入导致的文本错乱，多余换行，
```
context = re.sub(r'([a-zA-Z，\d])(\n\n(References：)[\W\w]*?)(\n\n)(([a-z\(])[\W\w]*?)(\n\n\d+\\?\.)', r'\1删除引用换行\5\2\7', context)
```

**0924补充：**

### 多余换行：
1.文末References：里有正文内容，栏目混乱导致多余换行，利用move_ref_confusion调整References里正文段落位置并删除多余换行。
```
def move_ref_confusion(self, context):
    match = re.search(r'([^|\n]{100,}[a-zA-Z，\d])(\n\n(References?：?|REFERENCES?：?\n\n)[\W\w]*?\n\n)([a-z\(].*\n\n)([\W\w]*?\n\n\d+\\?\.)', context)
    if match:
        n_text = match.group(4)
        if len(n_text)<100 or re.search(r'(\d{4}[;；： \.]+\d+(\(\d+\))?[:：； ]*[\d\-]+)', n_text):
            context = re.sub(r'([a-zA-Z，\d])(\n\n(References?：?|REFERENCES?：?\n\n)[\W\w]*?\n\n)([a-z\(].*\n\n)([\W\w]*?\n\n\d+\\?\.)', r'\1\2\5', context)
            context = self.move_ref_confusion(context)
        else:
            context = re.sub(r'([a-zA-Z，\d])(\n\n(References?：?|REFERENCES?：?\n\n)[\W\w]*?)(\n\n)(([a-z\(])[\W\w]*?)(\n\n\d+\\?\.)', r'\1删除引用换行\5\2\7', context)
    return context
```

2.多余换行补充上段小写字母结尾，下段数字开头但非序号。补充排除a)、b)、c)等序号，补充逗号结尾，下段大写开头。补充上段小写结尾非标题，下段大写开头且带有句号段落长度大于200。
```
def move_duan(self, context):
    context = re.sub(r'([a-z，\-\d])(\n+\n)([a-z][^\)]|\d+[^\.\\])',  r'\1删除1换行\3', context)
    context = re.sub(r'([^|\n]{100,}[^\.])(\n+\n)( *[a-z][^\)])', r'\1删除2换行\3', context)
    context = re.sub(r'([a-z\-\d])(\n+\n)( *\.)', r'\1删除3换行\3', context)
    context = re.sub(r'([^|\n]{100,}[,，a-z])(\n+\n)( *(?!Table)[A-Z][^|\n]{35,}\.[^|\n]{200,})', r'\1删除4换行\3', context)
    context = re.sub(r'([a-zA-Z，\d])(\n\n((Supplementary )?Table|\|) [\W\w]*?)(\n\n)(([a-z\(]).*)', r'\1删除表格换行\6\2', context)
    context = re.sub(r'([a-z\d])(\n\n((Supplementary )?Table|\|) [\W\w]*?)(\n\n)((±|\d).*)', r'\1删除表格换行\6\2', context)
    return context
```

### 无关文本：
1.H品\]11295大写开头的无关文本，以及排除单个数字的一段。
```
[r'(^\w*[\u4e00-\u9fff\d\\\]\[ ]{2,}$)', r'删除5:<u>\1</u>'],
```

2.文章中间连着的无关段落群使用函数delete_page_middle删除。
```
start_to_end = [
    [r'(^[\\ #]*(Copyright @))', r'(^[\\ #]*([A-Z][a-z]+( [A-Z][a-z]+)?)[\\ #]*$)|(.{250,})', 0],
    [r'(^[\\ #]*(DOI：))', r'(^[\\ #]*([A-Z][a-z]+( [A-Z][a-z]+)?)[\\ #]*$)|(.{250,})', 0],
    [r'(^[\\ #]*(Full-text ))', r'(^[\\ #]*([A-Z][a-z]+( [A-Z][a-z]+)?)[\\ #]*$)|(.{250,})', 0],
]
```

3.无关数字只带一半括号的[13，14、[4，11，12、10-13，26，27]等，更改补充通用删除6。
```
[r'(((\\)?\[[\d\s,，\.\–\-—]{1,}(\\)?\]?)|((\\)?\[?[\d\s,，\.\–\-—]{1,}(\\)?\]))', r'通用删除6(英):<u>\1</u>'], 
```
4.段尾无关数字，|1，21、9，10|等。
```
[r'( ?[，\-\|]*(\d+[，\-\|])+(\d+)?(\.|$))', r'删除6:<u>\1</u>\4'],
```
