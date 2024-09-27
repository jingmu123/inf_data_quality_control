reclean1_journal-pile

reclean0_journal-pile清洗报告

主要存在无关文本的问题，无关文本的问题较为复杂，已解决90%以上的无关文本，但是本次的提升应该不会很大，或者可能质量分和通过率会下降，因为文件中有近14w条数据，300条数据太局限还会有很多的新错误没有发现。

添加无关文本删除

```
[r'(\([^\(\)]*(pone)s?[\d\s\.:][^\(\)]*\))', r'删除18:<u>\1</u>'],  # 带有圆括号 里面有特征pone
[r'(\{[^\{\}]*\})', r'删除19:<u>\1</u>'],  # 带有花括号 {}里面所有
[r'([!\.]{0,}(\\)?[\(\[\{][,\s;-]{0,}(\\)?[\)\]\}])', r'删除20:<u>\1</u>'],  # 前面可以有一个！带有各种括号的里面为空

[r'(\[[^\[\]]*(@|#|Supplementary material|Reporting Summary|SUMMARY|data not shown)[^\[\]]*\])',r''],                # 带有方括号 里面有一个特殊符号@、#、一些特殊的固定叙述补充材料等等
[r'(\([^\(\)]*(@|#|SUMMARY|data not shown)[^\(\)]*\))',r''],                # 带有圆括号 里面有一个特殊符号@、#、一些特殊的固定叙述数据未显示等等
[r'^(We|I) thank.*',r''],   # 一句固定格式的句子  感谢...
[r'(\(\s?([Ff]igs?(ure)?|F\s?IGS?(URE)?|Table|[Ss]ee|For more|panel|http|www|NCT\d+|NO\.|version|p\.)s?[\s\.:\d][^\(\)]*\))',r'删除21:<u>\1</u>'],  # 1. 这些固定的词语紧贴左括号
[r'^jcm-08-01366.*',r''],
[r'(^See\s.*)',r'删除22:<u>\1</u>'],        # See在句子开头  见...
[r'(\(ABSTRACT[^\(\)]*\))',r'删除23:<u>\1</u>'],   # 带有圆括号的ABSTRACT摘要
[r'(References:.*)',r'删除24:<u>\1</u>'],    #  句子结尾处出现References:...  从reference开始删除
[r'(.*no conflict of interests.*)',r'删除25:<u>\1</u>'],  # ...没有利益冲突，区别于文章尾的多段删除，这里只需要删除这一段
[r'(^The author is grateful.*)',r'删除26:<u>\1</u>'],    # 作者感谢...的支持之类的描述
[r'(^(Informed )?[cC]onsent:.*)',r'删除27:<u>\1</u>'],    # 知情同意、同意 ...
[r'^(\([A-Z]*\)|[#]{1,}|Click here for additional data file.)$',r'删除28:<u>\1</u>'],    # 单行只有(A-Z)、多个#、点击查看文件
[r'(.{20,}Supporting information.*)',r'删除29:<u>\1</u>'],    # ...支持信息... 如果Supporting information在段首则对下面的段落全部删除  否则只删除这一行
```

添加结尾无关删除

```
[r'^.{0,10}(Competing [Ii]nterest|Funding|Source of Support|Supporting information|Availability of data and materials|Financial support and sponsorship|conflict of interest|Acknowledgement|Reporting summary|Disclosure|Supplementary information|Disclosure statement|Author contribution|Conflict of interest statement|Ethics.{0,10}(\n|$))s?'],  # 利益冲突、赞助、致谢...断尾描述
[r'^The author has served']   # 这里是个特例能匹配到的数据不多
```

添加一个新方法，对连续出现多段的很短的段落（只有一个字符，最多不超多20个字符，通常出现有10段左右）进行删除

循环context段落，定义两个列表，一个存放index，一个存放length,循环存放length的列表，再定义两个列表存放真正需要删除的index，另一个存放发现短句的index，发现有5个及以上的短句就认为需要删除，再次发现长句时重置存放短句的列表，继续向后探索

```
def Continuous_phrase_clean(self, context):
    Continuous_phrase_index = []
    Continuous_phrase_len = []

    # 记录每个片段的index和长度
    for index, item in enumerate(context):
        Continuous_phrase_index.append(index)
        Continuous_phrase_len.append(len(item.split()))

    # 检查是否有连续5个及以上长度小于20的片段
    del_indices = []  # 记录需要删除的index
    temp_indices = []  # 临时存储符合条件的index

    for i, length in enumerate(Continuous_phrase_len):
        if length < 20:
            temp_indices.append(Continuous_phrase_index[i])
        else:
            # 如果temp_indices中有连续5个及以上的片段，记录这些index
            if len(temp_indices) >= 5:
                del_indices.extend(temp_indices)
            temp_indices = []  # 重置

    # 如果最后一段也是连续的，检查并添加到删除index
    if len(temp_indices) >= 5:
        del_indices.extend(temp_indices)

    # 根据del_indices删除context中对应的片段
    cleaned_context = [item for i, item in enumerate(context) if i not in del_indices]

    return cleaned_context
```