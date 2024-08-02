reclean1_guidelines_ly_gptpdf的标注及总结及第二轮清洗

无关文本

正则改动

```
修改正则，避免识别m后面的小数字
[
    r'([^m])(<sup>[\d+\s,a-z]{1,}</sup>)',
    r'\1删除23:<u>\2</u>'
],
添加正则识别【aaaa 2016】
[
    r'([*]{0,3}\[[^\[\]]{0,50}\d{4}[^\[\]]{0,50}\][*]{0,3})',
    r'删除24:<u>\1</u>'
]
修改正则，删除9之前是将两种括号放在一起，但是有 （see ... []..）的情况出现所以要将两种括号分开，避免互相影响
[
    r'([\(]\s?([Tt]able|[sS]ee)[^\)]*?[\)])',
    r'删除9:<u>\1</u>'
],
[
    r'([\[]\s?([Tt]able|[sS]ee)[^\]]*?[\]])',
    r'删除9:<u>\1</u>'
],
删除19 [^\(\)]这里的字符数量不好把控直接换成*
[
    r'(\([^\(\)]*(\set[\s\xa0]{1,3}al|\d{4})[^\(\)]*\))',
    r'删除19:<u>\1</u>'
],
修改删除9添加中文见表的删除
[
    r'([\(]\s?([Tt]able|[sS]ee|见表)[^\)]*?[\)])',
    r'删除9:<u>\1</u>'
],
[
    r'([\[]\s?([Tt]able|[sS]ee|见表)[^\]]*?[\]])',
    r'删除9:<u>\1</u>'
],

```

step1改动对图片描述的句子做了补充

```
在这里我想匹配图片描述的内容在匹配到的字符后面加了[\s\d]避免匹配到Fig开头的其他单词，但是出现了例子Fig.
if re.search('^([#*]{0,5}).{0,5}\s?([Ff]igs?(ure)?s?|FIGS?(URE)?s?|图)[\s\d\.]',line.strip()) or re.search('\.(png|jpg|PNG|JPG)',line.strip()):

```



将clean_en中的参考删除stap5拿过来

修改正则主要是针对一些带有括号的[]，()之前没有包含进去的情况，做一下优化



多余标点，把之前多于标点解决的方案拿过来

```
context = re.sub(r'[。，\.](\s?[。，\.：；]){1,5}',r'。',context)
context = re.sub(r'[,\.](\s+[,\.]){1,5}',r'\.',context)
```

多余换行，因为换行错误较少，所以只添加这几个比较明显的换行错误修正

```
def is_merge_duannei(self, text, next_text):
   
    if re.search(r'^#{0,5}\s?(\d+[\.,\s]?){0,5}$', text) and re.search(r'^#{0,5}\s?[A-Z]',next_text):  # 匹配段落中只有序号且下一段是大写开头的情况 都可以带#
        return True
     # 定义一个介词列表
    preposition_list = ['of', 'in', 'and', 'or', 'not', 'the', 'a', 'any', 'for', 'is', 'The', 'A', 'with', '&',
                        'And', 'their', 'his', 'her','that']
    # 新增条件: 如果 stripped_item 结尾的单词在 preposition_list 中
    if any(text.rstrip().endswith(" " + prep) for prep in preposition_list) and not re.search("^#",next_text.strip()):
        return True
    if text and text[-1] in ['-', '"', ',']:
        return True
    if text.strip() and next_text.strip() and text.strip()[-1].islower() and next_text.strip()[0].islower():
        return True
    return False

def is_merge_duan(self, stripped_item, next_item):
   
    if re.search(r'^#{0,5}\s?(\d+[\.,\s]?){0,5}$', stripped_item) and re.search(r'^#{0,5}\s?[A-Z]',next_item):  # 匹配段落中只有序号且下一段是大写开头的情况 都可以带#
        return True
    # 定义一个介词列表
    preposition_list = ['of', 'in', 'and', 'or', 'not', 'the', 'a', 'any', 'for', 'is', 'The', 'A', 'with', '&',
                        'And', 'their', 'his', 'her','that']
    # 新增条件: 如果 stripped_item 结尾的单词在 preposition_list 中
    if any(stripped_item.rstrip().endswith(" " + prep) for prep in preposition_list) and not re.search("^#", next_item.strip()):
        return True
    if stripped_item and stripped_item[-1] in ['-', '"', ',']:
        return True
    return False
```

完整性（无法解决）

如果出现pdf左上角第一段是半段，需要与上一页衔接的，那一定会识别丢

准确性（无法解决）

ai改动文本的频次很高

序号格式不一致、栏目混乱、表格格式和一些无特殊特征的有用性未解决

