## reclean1_accr问题
### 无关文本：
1.文章中部分段落**OPEN ACCESS**开始到标题结束删除。
```
start_to_end = [
    # 样例
    [r'(^[\\\*#\_]+(OPEN ACCESS)[\\\*#\_]+$)', r'(^[\\\*#\_]+([A-Z][a-z]+( [A-Z][a-z]+)?)[\\\*#\_]+$)|(.{250,})', 0],
]
for middle in start_to_end:
    delete_line_index = []
    for index, item in enumerate(context):
        if re.search(middle[0], item):
            satrt = [index, 0]
            delete_line_index.append(satrt)
        if re.search(middle[1], item):
            end = [index, 1]
            delete_line_index.append(end)
    length = len(delete_line_index)
    if length >= 2:
        for i in range(1, length):
            if delete_line_index[i - 1][1] < delete_line_index[i][1]:
                start_index = delete_line_index[i - 1][0]
                end_index = delete_line_index[i][0]
                for i in range(start_index, end_index + middle[2]):
                    context[i] = "通用间距删除-1:<u>{}</u>".format(context[i])
                    # context[i] = ""
```

2.增加结尾没有标记直接序号开始的参考文献，并打上标签观察是否有误删情况。
```
ending_starts = [
    [r'^[#\*]{0,4}\s?(Reference|Funding and Disclosures|Polls on Public|Ethics Approval|Authors?\'? Contribution|Acknowledge?ment|Funding|Funding Sources)s?[#\*]{0,4}\s{0,}($|\n)'],
    [r'(^1\\\. )']
]
for ii, start in enumerate(ending_starts):
    references_started = False  # 定义一个删除reference的开关  只要出现固定格式的表述就对后面的内容进行删除
    for index, item in enumerate(context):
        if re.search(start[0], item.strip()):
            references_started = True
        if references_started:
            if ii > 0:
                context[index] = "通用结尾删除-1:<u>{}</u>".format(context[index])
            else:
                context[index] = ''
```

3.句子结尾.前面的无关数字，and longer onset21.**、antibiotic treatment 11-14.**等。
```
[r'(?<!of|in|to)( [\d,，\-\–—]+)(\.($| ))',  r'删除4:<u>\1</u>\2'],
[r'([a-z])([\d,，\-\–—]+)(\.($| ))',  r'\1删除4-1:<u>\2</u>\3'],
```

4.无关数字单独一段，**_2156._**
```
[r'^([\d,，\-\–— \.]+)$', r'删除5:<u>\1</u>']
```

**0911补充：**

1.结尾没有标记直接序号开始的参考文献误删严重，修改方法添加正则删除
```
[r'(^\d+\\?\..*\d{4}[;；]\d+(\(\d+\))?[:：]?[\w\-]+.*)', r'删除6:<u>\1</u>']
```

2.补充Acknowledgm ent致谢单词中带空格情况、补充Authors'Contribution中不带空格情况、补充Pseudomembranous Tracheobronchitis。
```
ending_starts = [
    [r'^[ #]*(Reference|Funding and Disclosures|Polls on Public|Ethics Approval|Authors?\'? ?Contribution|Acknowledge?m ?ent|Funding|Funding Sources|Research Funding|Pseudomembranous Tracheobronchitis)s?[ #]*($|\n)'],
]
```

3.Received Date： 30 Aug 2021、Accepted Date： 22 Sep 2021、Published Date： 27 Sep 2021等无关文本。
```
[r'(^(Received|Accepted|Published) Date：.*)', r'删除7:<u>\1</u>']
```

4.补充删除E-mail. wookoficu@kosinmed.or.kr 句子。
```
[r'(^[ \\]*(Correspondence：|OPEN ACCESS|E-mail|Copyright).*)', r'删除1:<u>\1</u>'],
```

5.补充Citation：文中无关段落。
```
start_to_end = [
    # 样例
    [r'(^[\\ #]*(OPEN ACCESS)[\\ #]*$)', r'(^[\\ #]*([A-Z][a-z]+( [A-Z][a-z]+)?)[\\ #]*$)|(.{250,})', 0],
    [r'(^[\\ #]*(Correspondence：|Citation：))', r'(^[\\ #]*([A-Z][a-z]+( [A-Z][a-z]+)?)[\\ #]*$)|(.{250,})', 0],
]
```
