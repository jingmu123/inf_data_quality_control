reclean1_icliniq_article

无关文本

主要为文章末尾处Article Resources对文章资源的描述和一些延伸内容相关主题的描述

关于延伸内容相关主题有三种情况

1.行级，在搜索到关键词Related Topics后可对此行后面的内容都删除

2.行级，在搜索到关键词Related Topics后对后面一定间距的行进行删除

3.段级，在搜索到关键词Related Topics后对后面一定间距的段进行删除

三种情况的检查规则为先3，2，1，3和2没有冲突，2和1可能有冲突但是2的规则更严格

使用一条正则和一个方法来解决

```
[r'(.*Related Topics[^$]*)',r'删除1:<u>\1</u>'],     # 相关话题...解决情况1
```

```
def step2_wuguanpage(self, context):
    new_context = []
    Related_Topics = False
    for item in context:
        if re.search('^Related Topics',item): 解决情况3
            Related_Topics = True
            item = "无关删除-2:<u>{}</u>".format(item)
            new_context.append(item)
            continue
            
        if re.search(r'\n\s{4}Related Topics',item):  # 解决情况2
            # print(item)
            # exit(0)
            Topic_in_item = False
            new_item = []
            splited_item = item.split('\n')
            for i in splited_item:
                if re.search(r'^\s{4}Related Topics',i):
                    Topic_in_item = True
                    i = "无关删除-4:<u>{}</u>".format(i)
                    new_item.append(i)
                    continue
                if Topic_in_item and (re.search(r'^\s{4}[^\s]',i) or re.search(r'^\s{1,5}$',i)):
                    i = "无关删除-4:<u>{}</u>".format(i)
                else:
                    Topic_in_item = False
                new_item.append(i)
            item = '\n'.join(new_item)

        if Related_Topics and (re.search(r'^[\*\s]{2,10}$',item) or re.search(r'\?$',item.strip())):
            item = "无关删除-3:<u>{}</u>".format(item)
        else:
            Related_Topics = False

        new_context.append(item)
    return new_context
```

关于文章资源的描述

使用之前的方法设置开关对匹配到的特征将后面的段落都删除

多余换行

出现问题的多于换行的格式单一，匹配到固定格式的序号就将下一句连上来

```
def step3_more_linefeed(self,context):
    index = 0
    while index < len(context):
        item = context[index]

        # 合并以小写字母或特定标点符号开头的段落
        stripped_item = item.strip()
        # print(stripped_item)
        if index >= 0:
            if index + 1 < len(context) and re.search(r'^#+\s?(\*+)?\d+\.(\*+)?$',stripped_item):
                context[index] = stripped_item +"删除换行"+re.sub("#+\s",r'',context[index+1])
                # 删除下一个 item
                del context[index + 1]
                index = index - 1
                continue
        index += 1
    return context
```