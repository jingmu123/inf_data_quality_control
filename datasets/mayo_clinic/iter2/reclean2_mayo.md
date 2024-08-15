reclean2_mayo

多余标点   都能解决

1.两种情况句子开头是标点

```
[r'(^\s?[;,])',r'删除7:<u>\1</u>'], # 多余标点开头是;
```

2.句子末尾出现？.的情况

```
([,\.?])(\s+[?,\.]){1,5}
```

无关文本 能解决百分之80左右   预计能够提升18.9分

新增加正则

```
[r'(\([^\(\)]*(https?:|www\.|WWW\.)[^\)\(]*\))',r''],  # 无关链接网址带括号
[r'(.*(https?:|www\.|WWW\.).*)',r'删除3:<u>\1</u>'],   # 无关链接网址的整句删除
[r'(.*\s((1|2)\d{3};|Vol \d\.?)(\s.*|$))',r'删除3:<u>\1</u>'],  # 带有年份特征的句子  ( 2000; )
[r'(\(\s?[^\(\)]*([Ff]igs?(ure)?|F\s?IGS?(URE)?|Table|[sS]ee|For more)s?[\s\.][^\(\)]*\))',r'删除4:<u>\1</u>'],  # 固定格式  带有（）的图片表格描述 附录描述 协议描述
[r'(\\\[[^\[\]]*:\d+-\d+\\\])',r'删除5:<u>\1</u>'],  # 带有方括号的引用
[r'.*\set[ \s]al.*',r''], # et al
[r'(^(FDA |Date accessed:).*)',r'删除6:<u>\1</u>'], # 固定格式描述开头FDA或Date accessed:
```

新加入匹配无关行的特征    大量存在   

【54】*   Fleming NS

Ogola G
Ballard DJ

```
re.search(r'^\*\s+[^\n]*[A-Z](\n|$)',item)   #Fleming NS人名特征
re.search(r'\*\s+(Google|View Large Image|Download|et al\.|Open table in a new tab)',item)   #et al\.特征 in a new tab特征
```

新加入整块无关删除

```
### Identification|### Footnotes|Article info|Acknowledgments?   # 脚注，鉴别 后面几乎都是没用的介绍期刊的 文章的介绍 致谢
```

加入之前些的方法对某个间距内的内容进行删除，从In their editorial and administrative roles关于作者的介绍到\*\*Question的描述

```
    def step3_Spaced_delete(self, context):
        new_context = []
        question = 0
        question_index = []
        for index,item in enumerate(context):
            if re.search('\.\s?In their editorial and administrative roles',item):
                question_index.append(index)
                question += 1
            if re.search(r'^In their editorial and administrative roles',item):
                question_index.append(index)
                question += 1
            if re.search(r'^\*\*Question',item):
                question_index.append(index)
                question -= 1
            new_context.append(item)
        print(question_index)
        if question <= 0 and len(question_index) >= 2:
            start_index = question_index[0]
            end_index = question_index[-1]
            print(start_index, end_index)
            # 循环遍历需要替换的片段
            for i in range(start_index, end_index + 1):
                if re.search('\.\s?In their editorial and administrative roles',new_context[start_index]):
                    new_context[start_index] = re.sub('(\.\s?)(In their editorial and administrative roles.*)',r'\1间距删除-1:<u>\2</u>',new_context[start_index])
                    continue
                # 将当前索引处的字符替换为你想要的字符，这里以空字符为例
                new_context[i] = "间距删除-1:<u>{}</u>".format(new_context[i])
        return new_context
```

title是CORRECTIONS或CORRECTION直接跳过

```
if re.search(r'CORRECTIONS?',context):
    continue
```

错误删除是有一个地方的误标后续后续再次标注和标注同学指明，错误删除都能解决 预计提升10.5分

总预计能提升29分，达到90分以上