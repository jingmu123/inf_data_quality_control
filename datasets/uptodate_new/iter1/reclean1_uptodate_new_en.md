reclean1_uptodate_new_en
无关文本的删除

```
1.添加删除[\d]的无关文本
[r'\\\[[\d\s\-,—\\]{0,20}\]',''],
2.固定格式的表述，这里原理和中文一样，词语有差距
[r'\([^\(\)]{1,50}([fF]igure|NCT|Grade|[pP]icture|FIGURE|PICTURE)[^\(\)]{1,50}\)',''],
3.固定格式括号里的参考内容
[r'\(\s+Ref\s+\)',''],
4.括号里的人名的删除，主要特征在于\d{4};
[r'\([^\)\(]{1,50}\d{4};[^\)\(]{1,200}\)','']
5.特殊符号的删除
['(👍|▶|●|©|®|†|¶|║|§|∧|™|■|❏|□|✓|✔|❍|😃|�|∑|✦|❤️|❤)', ''],
6.修改一条正则
[r'[\s•\\-]{0,5}\((See|see|ESMO|ESC|ASCO)[^\(\)]*(\([^\(\)]*\)[^\(\)]*){0,}\)', '']
```

继续改进方法对参考文献和固定格式的介绍的删除，本次加入英文的特征，思路没变

```
def step3_reference(self, context):
    new_context = []
    references_started = False   #定义一个删除reference的开关  只要出现固定格式的表述就对后面的内容进行删除
    introduce = 0
    introduce_index = []
    for index, item in enumerate(context):
        if re.search(r'^(References|参考文献|见参考文献|致谢|REFERENCES|ACKNOWLEDGMENT)', item.strip()):
            references_started = True
        # 要删除从Author到引言 设定了两个条件在循环时同时出现Author和引言，记下index，对相应的index进行删除
        if re.search(r'^Author', item.strip()):
            introduce += 1
            introduce_index.append(index)
        if re.search(r'^引言', item.strip()) or re.search(r'^INTRODUCTION', item.strip()):
            introduce -= 1
            introduce_index.append(index)
        if references_started:
            item = ""
        new_context.append(item)

    if introduce == 0 and len(introduce_index) == 2:
        start_index = introduce_index[0]
        end_index = introduce_index[1]
        new_context = new_context[:start_index] + new_context[end_index:]

    return new_context
```