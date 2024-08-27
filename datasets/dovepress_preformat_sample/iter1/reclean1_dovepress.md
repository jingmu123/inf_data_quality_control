reclean1_dovepress

dovepress这组数据出现有大量无关文本是段落级别，使用间距删除的方法找到开始删除的特征和结束删除的特征和结尾部分的参考

```
def step1_wuguantext_following(self, context):
    new_context = []
    references_started = False  # 定义一个删除reference的开关  只要出现固定格式的表述就对后面的内容进行删除
    for index, item in enumerate(context):
        if re.search(
                r'^(Ethics?\s)',
                item.strip()) :   # 付费下载...  拨打电话...  后面直接都删掉
            references_started = True
        if references_started:
            item = "无关删除-1:<u>{}</u>".format(item)
            # item = ''
        new_context.append(item)
    return new_context
def step3_Spaced_delete(self, context):
    new_context = []
    before_introduction = 0
    before_introduction_index = []
    for index,item in enumerate(context):
        if re.search('^\*\s+',item) and index <= 3:
            before_introduction_index.append(index)
            before_introduction += 1
        if re.search('^[\*#]{0,5}Introduction',item):
            before_introduction_index.append(index)
            before_introduction -= 1
        new_context.append(item)
    if before_introduction <= 0 and len(before_introduction_index) >= 2:
        start_index = before_introduction_index[0]
        end_index = before_introduction_index[-1]
        print(start_index, end_index)
        # 循环遍历需要替换的片段
        for i in range(start_index, end_index-1):
            # 将当前索引处的字符替换为你想要的字符，这里以空字符为例
            new_context[i] = "间距删除-1:<u>{}</u>".format(new_context[i])
            # new_context[i] = ""

        new_context[end_index-1] = re.sub(r'(^[^\*]*)(\n\*\*)', r'间距删除-2:<u>\1</u>\2',new_context[end_index-1])

    return new_context
```

正则删除

```
[r'([^\d]\s?[\.,]\s?)(\d+[\s–,\d+]{0,20})([A-Z]|$)',r'\1删除1:<u>\2</u>\3'],   # 无关数字
[r'(\(\s?[^\(\)]*([Ff]igs?(ure)?|F\s?IGS?(URE)?|Table|[sS]ee|For more)s?[\s\.][^\(\)]*\))', r'删除2:<u>\1</u>'],# 固定格式  带有（）的图片表格描述 附录描述 协议描述
[r'(Disclaimer.*)',r'删除3:<u>\1</u>'],
[r'(\d+\s([–,]\s\d+\s){1,20})',r'删除4:<u>\1</u>'],  # 删除内容中出现的无关数字 可能会造成误删
```

发现段落数少于一定数量的篇幅有用信息很少，可以选择删除

```
if len(context) <= 20:
    context.insert(0,"内容太短有用信息较少直接删除")
    context = split_token.join(context)
    return context
```