reclean1_nejm

无关文本 添加4条正则

```
pattern_list = [
    [r'(\(pages?\s[^\(\)]*\))',r'删除1:<u>\1</u>'],   # 固定格式 （page ...）
    [r'(\(\s?([Ff]igs?(ure)?s?|F\s?IGS?(URE)?s?|Table|Details|Appendix)\s[^\(\)]*\))',r'删除2:<u>\1</u>'],   # 固定格式  带有（）的图片表格描述 附录描述 协议描述
    [r'(<sup>(<a>)?[\d\s\-—,]{1,10}(</a>)?</sup>)',r'删除3:<u>\1</u>'],   # 特殊格式的数字引用删除
    [r'(\([^\(\)]{,40}[\s,]\d{4}[^\(\)]{,40}\))',r'删除4:<u>\1</u>'],     # 带有括号的引用 例(N Engl J Med 300:9–13, 1979)
    [r'§',r'']    # 一个特殊符号
]
```

大片无关文本 多段的删除

基本都在文章的后面，使用开关的方式进行删除     基本都用共同的特征在第一段会出现

```
*   _18_ References
*   _558_ Citing Articles
```

的类似标记

```
def step1_reference(self, context):
    new_context = []
    first_paragraph = context[0]
    references_started1 = False  # 初始化 references_started 变量
    references_started2 = False
    CitingArticles_started1 = False  # 初始化 CitingArticles_started 变量
    CitingArticles_started2 = False
    if re.search(r'\*[^\n]*References?', first_paragraph):
        references_started1 = True  # 定义一个删除reference的开关  只要出现固定格式的表述就对后面的内容进行删除
        context[0] = "参考删除-0" + context[0]
    elif re.search(r'\*[^\n]*Citing Articles', first_paragraph):
        CitingArticles_started1 = True  # CitingArticles_started开关   定义CitingArticles_started是因为他和有References出现的页开始删除的地方有所不同
        context[0] = "参考删除-0" + context[0]
    for index, item in enumerate(context):
        if re.search(r'^(References?|Funding and Disclosures)\s', item.strip()):
            references_started2 = True
        if references_started1 and references_started2:
            item = "参考删除-1:<u>{}</u>".format(item)
        if re.search(r'\.D\.', item.strip()):
            CitingArticles_started2 = True
        if CitingArticles_started1 and CitingArticles_started2:
            item = "参考删除-2:<u>{}</u>".format(item)
        new_context.append(item)
    return new_context
```