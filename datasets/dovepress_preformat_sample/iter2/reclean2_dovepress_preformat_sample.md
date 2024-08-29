reclean2_dovepress_preformat_sample

添加两条正则

```
[r'(Disclaimer.*)',r'删除3:<u>\1</u>'],
[r'(\d+\s([–,]\s\d+\s){1,20})',r'删除4:<u>\1</u>'],  # 删除内容中出现的无关数字 可能会造成误删
```

解决误删，修改删除2原因是出现有带括号且有Figure的内容，需要保留Figure之前的内容，只删除从Figure到右括号的内容，在删除2上加一个正则只针对左括号紧挨着单词Figure的情况对整个括号内容进行删除，并加入http，www特征到带有括号的删除

```
[r'(\(\s?([Ff]igs?(ure)?|F\s?IGS?(URE)?|Table|[sS]ee|For more|http|www|p\.)s?[\s\.][^\(\)]*\))', r''],
[r'(\(\s?[^\(\)]*)([\.,;]\s([Ff]igs?(ure)?|F\s?IGS?(URE)?|Table|[sS]ee|For more|http|www)s?[\s\.][^\(\)]*)(\))', r'\1删除2:<u>\2</u>)'],# 固定格式  带有（）的图片表格描述 附录描述 协议描述
[r'(\([^\(\)]*([Ff]igs?(ure)?|F\s?IGS?(URE)?|Table|[sS]ee|For more|http|www)s?[^\(\)]*\))',r'删除5:<u>\1</u>'],
```

解决误删，修改方法3，方法3是对段落进行删除，调整了匹配的规则，

```
def step3_Spaced_delete(self, context):
    new_context = []
    before_introduction = 0
    before_introduction_index = []
    for index,item in enumerate(context):
        if re.search('^\*\s+',item) and index <= 3:
            before_introduction_index.append(index)
            before_introduction += 1
        if re.search('^([\*#]{0,5}Introduction|[\*#]{0,5}Background)',item):
            before_introduction_index.append(index)
            before_introduction -= 1
        elif re.search(r'[\*#]{0,5}Background',item):
            before_introduction_index.append(index+1)
            before_introduction -= 1
            break
    if before_introduction <= 0 and len(before_introduction_index) >= 2:
        start_index = before_introduction_index[0]
        end_index = before_introduction_index[-1]
        print(start_index, end_index)
        # 循环遍历需要替换的片段
        for i in range(start_index, end_index-1):
            # 将当前索引处的字符替换为你想要的字符，这里以空字符为例
            # context[i] = "间距删除-1:<u>{}</u>".format(context[i])
            context[i] = ""
	    # 对于匹配到的最后一段有不同的情况，需要针对不同的情况进行去删除
        if re.search(r'\n\*\*',context[end_index - 1]):
            split_content = context[end_index - 1].split('\n**', 1)
            # context[end_index-1] = "间距删除-2:<u>{}</u>".format(split_content[0]) + '\n**' + split_content[1]
            context[end_index - 1] = '\n**' + split_content[1]
        else:
            # context[end_index-1] = "间距删除-3:<u>{}</u>".format(context[end_index-1])
            context[end_index-1] = ""
    return context
```

修改方法1，方法一是对某条件之后的段落进行全部删除，这里出现的情况很多，需要不断的去翻找新情况

```
if re.search(r'^(Ethics Statement|Ethics?|Ethics Approval|Statement of Ethics|Ethics Approval and Informed Consent)$', item.strip()):
    references_started = True

if re.search(r'Consent Statement',item.strip()):
    references_started = True
```





