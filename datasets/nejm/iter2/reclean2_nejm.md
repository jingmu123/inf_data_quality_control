reclean2_nejm

本次抽样125条，无关文本和语句字词重复基本都能解决，预计能到提升到95分，并解决一些误删

正则

```
1.正则2新添加带有括号且开头是Panels|[sS]ee|for example, see的描述
[r'(\(\s?([Ff]igs?(ure)?|F\s?IGS?(URE)?|Table|Details|Appendix|Funded|Section|epoch|Panels|[sS]ee|for example, see)s?[\s\.][^\(\)]*\))',r'删除2:<u>\1</u>'],   # 固定格式  带有（）的图片表格描述 附录描述 协议描述
2.正则3在处理特殊格式的数字引用这里新添加避免删除\d和m后面的特殊数字，避免删除次幂的描述
[r'([^\d\sm]+\s?)(<sup>(<a>)?[\d\s\-—,]{1,20}(</a>)?</sup>)',r'\1删除3:<u>\2</u>'],   # 特殊格式的数字引用删除
3.新添加固定形式  删除（... NCT112233 ...） 描述什么机构 拨打电话
[r'(\([^\(\)]*\s(NCT|ISRCTN)\d[^\(\)]*\))',r'删除5:<u>\1</u>'],    #固定形式  删除（... NCT112233 ...） 描述什么机构 拨打电话
4.新添加# 匹配带括号且有网址特征的句子
[r'(\([^\(\)]*(www\.|NEJM\.org|https?:|versions?\s?\d|opens? in new tab)[^\(\)]*\))',r'删除7:<u>\1</u>'],    # 匹配带括号且有网址特征的句子
5.新添加删除时间或下载时间
[r'(\(\d+:\d+\) Download)',r'删除9:<u>\1</u>'],    # 一个时间 一个下载
[r'([\(_]{0,}\d+:\d+[\)_]{0,})',r'删除10:<u>\1</u>'],  # 时间
6.新添加重复Table或Figure问题
[r'^((Table|Figure) \d\.)(\s+(Table|Figure) \d\.)',r'\1删除11:<u>\3</u>'],  # Table 1.  Table 1. 重复问题
```

step1方法解决大块的删除设置了不同的开关，又添加了step2，补充step1方法满足不了的情况，之前想把两个方法融合但是会出错

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
        elif re.search(r'\*[^\n]*Citing Articles?', first_paragraph):
            CitingArticles_started1 = True  # CitingArticles_started开关   定义CitingArticles_started是因为他和有References出现的页开始删除的地方有所不同
            context[0] = "参考删除-0" + context[0]
        for index, item in enumerate(context):
            if re.search(r'^(References?|Funding and Disclosures|Polls on Public)\s', item.strip()):
                references_started2 = True
            if re.search(r'\.[A-Z]\.\s+\n', item.strip()):
                CitingArticles_started2 = True
                references_started2 = True

            if references_started1 and references_started2:
                item = "参考删除-1:{}".format(item)
            if CitingArticles_started1 and CitingArticles_started2:
                item = "参考删除-2:{}".format(item)
            # if (not references_started1 and references_started2) or (not CitingArticles_started1 and CitingArticles_started2):
            #     item = "无关删除-1:<u>{}</u>".format(item)
            if re.search('^参考删除-\d:<u>Table \d\.',item):
                item = re.sub(r'参考删除-\d:(.*)',r'\1',item)
                references_started1 = False
                CitingArticles_started1 = False
            # if not references_started1 and references_started2:
            #     item = "无关删除-1" + item

            new_context.append(item)
        return new_context

    def step2_wuguantext_following(self, context):
        new_context = []
        references_started = False  # 定义一个删除reference的开关  只要出现固定格式的表述就对后面的内容进行删除
        for index, item in enumerate(context):
            if re.search(
                    r'^(Funding and Disclosures|Polls on Public|Author Affiliations)',
                    item.strip()) :
                references_started = True
            if references_started:
                item = "无关删除-1" + item
            new_context.append(item)
        return new_context

```

