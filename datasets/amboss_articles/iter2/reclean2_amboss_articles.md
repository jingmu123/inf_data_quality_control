reclean2_amboss_articles

reclean1_amboss_articles清洗报告

reclean1标注结果有28条错误删除，能够解决25条，预计提升4.8分

语句字词重复是表格的第一列出现的字词重复，不好清洗且影像较小不去清洗

无关文本有一些固定格式的无关文本已被清洗，预计能提升1分

预计第二次清洗能达到96分

主要原因是

正则在匹配[sS]ee时应该在后面加一个空格，否则就会匹配到单词中含有see的句子导致误删

```
[r'([^\n]*\*[^\n]*[Ss]ee[^\n]*)',r'删除4:<u>\1</u>'],  # 不带括号的see 行级 前面有*
↓
[r'([^\n]*\*[^\n]*[Ss]ee\s[^\n]*)',r'删除4:<u>\1</u>'],  # 不带括号的see 行级 前面有*
```

另有一个原因

删除4和删除5的正则顺序需要调换，删除5是针对半句，删除4是针对整句，如果删除4先匹配到了某个句子就会对整句进行删除，实际上只需要删除半句

```
[r'([,;\:\.])(\s?[Ss]ee\s[^\:\n]*)', r'\1删除5:<u>\2</u>'],  # 半句see开头
[r'([^\n]*\*[^\n]*[Ss]ee\s[^\n]*)',r'删除4:<u>\1</u>'],  # 不带括号的see 行级 前面有*
```

语句字词重复是表格的第一列出现的字词重复，不好清洗且影像较小不去清洗

无关文本

句子中出现One-Minute Telegram都是没有价值的数据，直接过滤

一些固定格式的无关文本使用正则删除

```
[r'((\*\s+)?For more\s[^\n]*)',r'删除7:<u>\1</u>'],  # For more 更多消息请参考...
[r'((Subscribe to|To see |For answers to questions).*)',r''],
[r'(.*https\:.*)',r'删除8:<u>\1</u>'],    # https网址信息
```