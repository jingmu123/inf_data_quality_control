## reclean1_acjr_mdpub_cases问题
### 错误删除：
1.结尾段落References：里有的正文内容，没有提取出来拼接，造成误删。move_ref_confusion函数调整优化。

a. 补充拼接开头，增加大写字母开头。增加\-开头。

b. 补充References上段结尾是句号，但References里还是有正文内容。

c. 将不符拼接段落的字符长度由原来的100改为判断后面段落是否包含文献数字特征，并加上标签。

d. 补充References里有Conclusions标题的正文内容。

e. 补充标题为Reterences：，不符拼接段落补充包含网址的(https?[：:]\/\/)。
```
def move_ref_confusion(self, context):
    match = re.search(r'([a-zA-Z，\d\.])(\n\n(Re[tf]erences?：?|REFERENCES?：?\n\n)[\W\w]*?\n\n)((\\?\-?[a-zA-Z\(].*|Conclusions?)\n\n)([\W\w]*?\n\n\d+\\?\.)', context)
    if match:
        wei = match.group(1)
        n_text = match.group(5)
        l_text = match.group(6)
        if n_text in "Conclusions":
            context = re.sub(
                r'([a-zA-Z，\d\.])(\n\n(Re[tf]erences?：?|REFERENCES?：?\n\n)[\W\w]*?)(\n\n)((\\?\-?[a-zA-Z\(])[\W\w]*?)(\n\n\d+\\?\.)',
                r'\1\n\n拼接引用里的正文:\5\2\7', context)
            return context
        elif re.search(r'(\d{4}[;；： \.]+\d+(\(\d+\))?[:：； ]*[\d\-]+)|(https?[：:]\/\/)', l_text) or re.search(r'(\d{4}[;；： \.]+\d+(\(\d+\))?[:：； ]*[\d\-]+)|(https?[：:]\/\/)', n_text):
            context = re.sub(r'([a-zA-Z，\d\.])(\n\n(Re[tf]erences?：?|REFERENCES?：?\n\n)[\W\w]*?\n\n)(\\?\-?[a-zA-Z\(].*\n\n)([\W\w]*?\n\n\d+\\?\.)', r'\1\2删除不符拼接:<u>\4</u>\n\n\5', context)  #去标签去掉删除不符拼接:<u>\4</u>\n\n
            context = self.move_ref_confusion(context)
        else:
            if wei == '.':
                context = re.sub(
                    r'([a-zA-Z，\d\.])(\n\n(Re[tf]erences?：?|REFERENCES?：?\n\n)[\W\w]*?)(\n\n)((\\?\-?[a-zA-Z\(])[\W\w]*?)(\n\n\d+\\?\.)',
                    r'\1\n\n拼接引用里的正文:\5\2\7', context)
            else:
                context = re.sub(r'([a-zA-Z，\d\.])(\n\n(Re[tf]erences?：?|REFERENCES?：?\n\n)[\W\w]*?)(\n\n)((\\?\-?[a-zA-Z\(])[\W\w]*?)(\n\n\d+\\?\.)', r'\1删除引用换行\5\2\7', context)
    return context
```

2.删除5:Patient 3、删除5:CASE 2误删标题，修改：
```
[r'(^\w{0,2}[\u4e00-\u9fff\d\\\]\[ ]{2,}$)', r'删除5:<u>\1</u>'],
```

3.因为删除开头、中间、结尾段落顺序问题造成的误删。调整顺序，由于结尾段落References：里有正文内容，在结尾段落删除之前加入move_ref_confusion函数调整拼接正文。
```
context = context.split(split_token)
context = cp.delete_page_start(context)
context = cp.delete_page_middle(context)
context = split_token.join(context)
context = sp.move_ref_confusion(context)
context = context.split(split_token)
context = cp.delete_page_ending(context)
```

4.delete_page_middle通用间距删除补充结束特征正则，防止误删，导致意义不完整。
```
start_to_end = [
    [r'(^[\\ #]*(Copyright @))', r'(^[\\ #]*([A-Z][A-Za-z]+( [A-Z][A-Za-z]+)?)[\\ #]*$)|(^.{250,})|(^[a-z]{1,3}.{75,}\.$)', 0],
    [r'(^[\\ #]*(DOI：))', r'(^[\\ #]*([A-Z][A-Za-z]+( [A-Z][A-Za-z]+)?)[\\ #]*$)|(^.{250,})|(^[a-z]{1,3}.{75,}\.$)', 0],
    [r'(^[\\ #]*(Full?-text ))', r'(^[\\ #]*([A-Z][A-Za-z]+( [A-Z][A-Za-z]+)?)[\\ #]*$)|(^.{250,})|(^[a-z]{1,3}.{75,}\.$)', 0],
]
```

### 无关文本：
1. O Am J Case Rep， 2022；23：e937961.
```
[r'(.{0,100}\d{4}[;；：\.]\w+(\(\d+\))?[:：；]?[\w\-]+.*)', r'删除7:<u>\1</u>'],
```

2.补充通用结尾段落删除，Acknowledgmen1、Declaration of Figures Authenticity。
```
ending_starts = [
    [r'^[#\*]{0,4}\s?(References?：?|REFERENCES?：?|Funding( Sources| Statement| and Disclosure)?|Polls on Public|Ethics (committee )?[Aa]pproval|Author[s\' ]*Contribution|Acknowledge?men[t1]|Conflicts? of [Ii]nterest|Source of (Support|Funding)|(Financial )?[Dd]isclosure|Statement|Declaration of Figure[s\' ]*Authenticity)s?[#\*]{0,4}\s{0,}($|\n)'],
]
```

3.删除4补充删除，AP等两个字母或数字单独一段。
```
[r'(^(\(\w+\) ?\(\w+\)|\d\w( \d\w)*|[\d\-]+：|[A-Z]( \w)*|\w\w)$)', r'删除4:<u>\1</u>'],
```

4.删除2补充删除，Publisher's note：一段的换行后多余的organizations， or those of the publisher the editors。
```
[r'(^(Full?-text |Copyright|DOI：|[\dl]? ?Department |Dr\. |organizations， or those of the publisher).*)', r'删除2:<u>\1</u>'],
```

**0927补充：**
### 多余换行：
1.删除表格插入换行，补充上段是-结尾，补充删除Figure后换行符多余\n+\n。
```
context = re.sub(r'([a-zA-Z，\d\--])(\n+\n((Supplementary )?Table|\|) [\W\w]*?)(\n+\n)(([a-z\(][^ \--]).*)', r'\1删除表格换行\6\2', context)
context = re.sub(r'([a-z\d])(\n+\n((Supplementary )?Table|\|) [\W\w]*?)(\n+\n)((±|\d).*)', r'\1删除表格换行\6\2', context)
```

2.相邻两段之间，补充删除（开头的段落多余换行。调整前段字符限定，防止标题连接。
```
context = re.sub(r'([^|\n]{50,}[a-z，\-\d])(\n+\n)([a-z\(][^\)]|\d+[^\.\\\)])',  r'\1删除1换行\3', context)
context = re.sub(r'([^|\n]{80,}[^\.])(\n+\n)( *[a-z][^\)])', r'\1删除2换行\3', context)
context = re.sub(r'([a-z\-\d])(\n+\n)( *\.)', r'\1删除3换行\3', context)
context = re.sub(r'([^|\n]{80,}[,，a-z])(\n+\n)( *(?!Table)[A-Z][^|\n]{35,}\.[^|\n]{200,})', r'\1删除4换行\3', context)
```

### 无关文本：
1.删除2补充删除无关段落，New York Chiropractic and Physiotherapy Centre， EC Healthcare， Kowloon， Hong Kong.、Publisher's note：、Corresponding author：、Internal Medicine Department。
```
[r'(^(Full?-text |Copyright|DOI：|[\dl]? ?Department |Dr\. |organizations， or those of the publisher|New York Chiropractic and|Publisher[\'s ]*note：|Corresponding author：|Internal Medicine Department).*)', r'删除2:<u>\1</u>'],
```

3.补充通用结尾段落删除，Disclosure Statement、Acknowledgement：、Ethics Statement、Competing Interests、Patient informed consent以及文末没有标题的参考文献。
```
ending_starts = [
    [r'^[#\*]{0,4}\s?(Re[tf]erences?：?|REFERENCES?：?|Funding( Sources| Statement| and Disclosure)?|Polls on Public|Ethics (committee )?[Aa]pproval|Author[s\'’ ]*Contribution|Acknowledge?men[t1]：?|Conflicts? of [Ii]nterest|Source of (Support|Funding)|(Financial )?[Dd]isclosure|(Disclosure |Ethics )?Statement|Declaration of Figure[s\'’ ]*Authenticity|Competing [Ii]nterest|Declaration|Patient informed consent)s?[#\*]{0,4}\s{0,}($|\n)'],
    [r'(^(\d|l)\\?\..*\d{4}[;；：\.] ?\w+(\(\d+\))?[:：\.；]?[\w \-]+.*)']
]
```

4.无关段落，￥口22284 盟- H02 目可23，补充修改删除5。
```
[r'(^\w{0,2}[\u4e00-\u9fff\d\\\]\[ ￥\-]{2,}.{0,80}$)', r'删除5:<u>\1</u>'],
```

5.含有网址的段落，加入段落长度限定，https：//www.amjcaserep.com/abstract/index。
```
[r'(^.{0,150}(https?[：:]\/\/[^ ]*).{0,100})', r'删除8:<u>\1</u>'],
```

