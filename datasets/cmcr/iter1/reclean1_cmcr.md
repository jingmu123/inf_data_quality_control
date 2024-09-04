reclean1_cmcr



语义不完整

1.语义不完整基本出现在内容很少只有一段的情况下，对于这种直接删除

2.文中可能出现空括号



无关文本

```
[r'(^[\*#]{0,4}图\s?\d+.*)',r'删除1:<u>\1</u>'],
[r'(（\s{0,}）)',r'删除2:<u>\1</u>'], # 空括号里面什么都没有
[r'(（详见[^（）]*）)',r'删除3:<u>\1</u>'],   # 详见...
[r'((视频))',r'删除4:<u>\1</u>'],  # 单行只有一个视频
[r'(（请扫描文章首页左下角二维码）)',r''],
[r'本病例选自.*',r''],
[r'([，。]见(图|表)\d+[^，。]*)',r'删除5:<u>\1</u>'],   # 见图/表1...
```



语句重复

文中出现有图表描述的段落重复，图重复已经删掉，step2方法判断两个相同的字符串删掉后面一个

```
def step2_repeated_paragraph(self,context):   # 删除掉重复的表叙述
    for index,item in enumerate(context):
        if re.search(r'^[\*#]{0,4}表\s?\d+',item.strip()):
            if item.strip() == context[index+1].strip():
                del context[index+1]
    return context
```