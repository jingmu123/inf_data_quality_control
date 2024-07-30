reclean1_uptodate_new_zh

无关文本未删除干净，添加正则

```
1.添加删除[\d]的无关文本
[r'\\\[[\d\s\-,—\\]{0,20}\]',''],
2.添加删除带有括号且固定表述的句子
[r'\([^\(\)]{1,50}(流程图|figure|NCT|Grade|视频|计算器|波形|表|表格|图|图片|图表|影像)[^\(\)]{1,50}\)',''],
修改之前的一条正则，对参见表述的句子
[r'\(参见[^\(\)]*\)', '']
```

添加一个方法对[References|参考文献|见参考文献|致谢]和固定格式的介绍从Author到引言的删除

```
def step3_reference(self, context):
    new_context = []
    references_started = False   #定义一个删除reference的开关  只要出现固定格式的表述就对后面的内容进行删除
    introduce = 0
    introduce_index = []
    for index, item in enumerate(context):
        if re.search(r'^(References|参考文献|见参考文献|致谢)', item.strip()):
            references_started = True
		# 要删除从Author到引言 设定了两个条件在循环时同时出现Author和引言，记下index，对相应的index进行删除
        if re.search(r'^Author', item.strip()):
            introduce += 1
            introduce_index.append(index)
        if re.search(r'^引言', item.strip()):
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