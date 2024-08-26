reclean2_mayo_clinic_proceeding

无关文本

无关数字

```
[r'([^\dm]+\s?|^)(<sup>(<a>)?[\d\s\-—,]{1,20}(</a>)?</sup>)',r'\1删除19:<u>\2</u>'],
[r'(\\\[[^\[\]]*\d{4}[^\[\]]*\\\])',r'删除20:<u>\1</u>'],   #结尾是一个年份的句子
[r'(^\*   US Pharmacopeia.*)',r''],     # 固定的句子
[r'(.*[\s\.]\d{4}\.?$)',r'删除21:<u>\1</u>'],  # 删除末尾为年份的句子
[r'(\*   Kaiser Family Foundation Health Research and Educational Trust)',r''],   # 固定的句子
[r'(^\*{0,4}_?To the Edito.*)',r'删除22:<u>\1</u>'],   # 开头是To the Editor是一个致编辑的文本  这里的内容基本没用
[r'\(data from Siscovick et al',r''],  # 固定的句子
[r'The study by Khan et al',r''], # 固定的句子
```

整段的删除

在出现Trial Registration后面的内容都是一些注册信息等无关内容，直接对后面的内容进行删除

[#\*]{0,4}\s?Files in this Data Suppleme后面为补充文件相关信息

```
[#\*]{0,4}\s?Trial Registration|[#\*]{0,4}\s?Files in this Data Supplement
```

title中函数有(Highlights from the Current Issue|CORRECTIONS?|The History of Otorhinolaryngology at Mayo Clinic|Minimally Disruptive Medicine|Welcomes New Staff Members)，所有匹配到的情况中，正文内容中都是作者和一些书籍

```
if re.search(r'(Highlights from the Current Issue|CORRECTIONS?|The History of Otorhinolaryngology at Mayo Clinic|Minimally Disruptive Medicine|Welcomes New Staff Members)',title):
    continue
if re.search(r'^(_?To the Edito\s?r|CORRECTION)',context):   # 过滤掉To the Editor当页内容里面都是一些编辑信息
    continue
```

添加一个新方法，本组数据中出现大量的无关数字，发现这些无关数字后面都有一个固定格式，到某一种表述中间都是无关内容，对中间的内容进行删除

```
def step2_wuguanpage(self, context):
    print(context)
    new_context = []
    num = False
    for index,item in enumerate(context):
        if re.search(r'^<sup><a>\d+</a></sup>',item):   # 找到特殊的无关数字
            num = True
            num2Google = 0
            num2Google += 1
            num2Google_index = index
            num2Google_index_line = []
            num2Google_index_line.append(index)
        if num and re.search(r'\*\s+(Google|View Large Image|Download|et al\.|Open table in a new tab)',item):  # 找到作为段落删除条件停止的特征
            num2Google -= 1
            if index - num2Google_index <= 5 and num2Google == 0:
                new_context.append(item)
                num2Google_index_line.append(index)
                start_index = num2Google_index_line[0]
                end_index = num2Google_index_line[-1]
                # 循环遍历需要替换的片段
                for i in range(start_index, end_index+1):
                    # 将当前索引处的字符替换为你想要的字符，这里以空字符为例
                    # new_context[i] = "无关删除-3:<u>{}</u>".format(new_context[i])
                    new_context[i] = ""

                continue
        if re.search('^\*[^\n]*[\.\s][A-Z]\.(\n|$)',item) or re.search('[a-zA-Z]?\d+-[a-zA-Z]?\d+\.?$',item.strip()) or re.search(r'\*\s+(Google|View Large Image|Download|et al\.|Open table in a new tab)',item) or re.search(r'^\*\s+[^\n]*[A-Z](\n|$)',item):   # 匹配到无关行的特征打标签
            # wuguanline_num += 1
            # item = "无关删除-2:<u>{}</u>".format(item)
            item = ''
        new_context.append(item)
    # print(new_context)
    return new_context
```