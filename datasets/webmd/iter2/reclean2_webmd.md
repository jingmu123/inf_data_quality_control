reclean2_webmd

reclean1_webmd报告

各纬度问题频次F={'无关文本': 14, '语句/字词重复': 38, '错误删除': 1}
合格率=83.333%
质量分=96.15308

本次质量分已经较高，合格率一般，但是本次的清洗语句/字词重复是段落级的重复的较多，需要处理一下，解决重复预计能提升到98.5分左右，合格率预计能达到90%以上

加入一些正则对无关文本的处理，预计能提升0.5分，预计下一次能够合格



添加正则

```
[r'(\(\s?[Ss]ee[^\(\)]*(\)|$))',r'删除6:<u>\1</u>'],    # 带有括号的(See ...)
[r'(^Contact the health care professional for medical advice about side effects.*)',r'删除7:<u>\1</u>'],   # 请与医疗保健专业人员联系，致电...
[r'(^Call your doctor for medical advice about side effects.*)',r'删除8:<u>\1</u>'],
[r'(.*The National Abortion Federation.*)',r''],  # 只有一条特殊处理
[r'(You can find more information at.*)',r''],    # 只有一条特殊处理
[r'(^(NEWSLETTER|Get the Crohn|Tips from experts|Stay Up-to-Date|Sign up for the latest coronavirus news).*)',r''], 
```

解决段级重复，从Warnings到Warnings

```
def step1_repeat_delete(self,context):
    warnings1 = False
    warnings2 = False
    warnings_index = []
    for index,item in enumerate(context):
        if re.search(r'^(\*+)?Warnings:(\*)?',item) and index == 0:
            warnings1 = True
            warnings_index.append(index)
        if re.search(r'^(\*+)?Warnings:(\*)?',item) and index > 0:
            warnings2 = True
            warnings_index.append(index)

    if warnings1 and warnings2 and len(warnings_index) >= 2:
        start_index = warnings_index[0]
        end_index = warnings_index[-1]
        # 循环遍历需要替换的片段
        for i in range(start_index, end_index):
            context[i] = "删除重复:<u>{}</u>".format(context[i])
    return context
```