reclean4_journal-pile

reclean3_journal-pile标注分析，合格率59.866%，质量分81.79469

在本次抽样中只针对较长的文本进行抽样发现标注出的问题明显增多，其中无关文本的数量较多

本次抽样无关文本问题解决90%，

多余标点、错误删除都已解决

还需要对长数据进行抽样发现更多问题

无关文本清洗

```
[r'\([^\(\)]{0,20}([,\.;\s]{0,}\[[^\[\]]{1,50}\]\([^\)\(]{1,50}\)\{[^\{\}]{1,50}\}){1,}[^\(\)]{0,20}\)', r''],   # 固定删除格式 [...](...){...} 外面可带圆括号或方括号，括号一定是同一种要带都带,要不就都不带
[r'\[[^\[\]]{0,20}([,\.;\s]{0,}\[[^\[\]]{1,50}\]\([^\)\(]{1,50}\)\{[^\{\}]{1,50}\}){1,}[^\[\]]{0,20}\]', r''],  # 固定删除格式 [...](...){...} 外面可带圆括号或方括号
[r'(\[[^\[\]]{1,50}\])?\([^\)\(]{1,50}\)\{[^\{\}]{1,50}\}', r''],

[r'((\\)?\([^\[]{,50}([,;\.\s]{0,}\[[^\[\]]*(@|#|Supplementary material|Reporting Summary|SUMMARY|data not shown)[^\[\]]*\]){1,}[^\]]{,50}(\\)?\))',r''],     # 带有圆括号 里面有一个特殊符号@、#
[r'((\\)?\[[^\[]{,50}([,;\.\s]{0,}\[[^\[\]]*(@|#|Supplementary material|Reporting Summary|SUMMARY|data not shown)[^\[\]]*\]){1,}[^\]]{,50}(\\)?\])',r''],                # 带有方括号 里面有一个特殊符号@、#
[r'((\\)?[\[\(])?([,;\.\s]{0,}\[[^\[\]]*(@|#|Supplementary material|Reporting Summary|SUMMARY|data not shown)[^\[\]]*\]){1,}((\\)?[\]\)])?',r''],                # 带有方括号 里面有一个特殊符号@、#

[r'\\\n',r''],

[r'([\.;]\s([Ff]igs?(ure)?|F\s?IGS?(URE)?|Table|[sS]ee|For more|http|www)s?[\s\.:\d][^\(\)]*)(\))', r')'],
# （）内出现(dose---F~(4,\ 52)~ = 5.312, p = 0.001; group × dose \[F~(4,\ 52)~ = 2.539 p = 0.051\]; Fig. [2a])，删除;后面出现的Table、Fig...到后面的右括号
[r'(^The following are available online.*)', r'删除31:<u>\1</u>'],  # 一下内容可在...找到，一版后面接的是网址
[r'(.*These authors contributed equally to this work.*)', r'删除32:<u>\1</u>'],  # 固定表述
[r'(\[\^\d+\])', r''],  # 无关数字
[r'(\(:\s?[①②③④⑤⑥⑦⑧\-⑨⑩\s,\.]{1,}\))', r''],

[r'([\(<][^\)>]*([hH]ttps?|www|WWW|HTTPS?|\.ua\.|\.edu)[^\(<]*[\)>])', r'删除33:<u>\1</u>'],  # 带有()\<>的非常规网址或网址路径
[r'(\(([^-\.,\s]{1,10}-){2,}[^-\.,\s]{1,10}\))',r'删除34:<u>\1</u>'],         # 删除类似于编号 (IJCCM-21-40-g003)
[r'([A-Z])(\[)([a-z][^\]]*)(\])',r'\1\3'],

[r'(!\[.*)', r''],  # 带有![ 这句是图片的描述!是因为图片加载不过来
[r'(^\[\^\d+\][^$]*)', r''],  # 句子开头为[^\d] 一般在句子结尾无关文本 必须放在处理带有[]特征的前面先删除掉
[r'(^\d.*\.pones?\..*)', r'删除35:<u>\1</u>'],  # 单行 10.1371/journal.pone.0035893.t001  类型的表述
[r'([^\d])(\s?(\$){1,}\s?)', r'\1删除36:<u>\2</u>'],  # 存在不是在数字后面的$符号  可匹配多个
[r'(.*(conflicts? of|competing) interest[^$]*)', r'删除37:<u>\1</u>'],  # ...利益冲突... 一般在句中只能针对这句去删除[r'(^(This|The)\s.* (was|is) supported[^$]*)', r'删除38:<u>\1</u>'],  # 这项研究得到了...的支持
[r'(^Paper extracted from[^$]*)', r'删除39:<u>\1</u>'],  # 论文摘自
[r'(^Assistance with the study[^$]*)',r''],  # 协助学习
```

增加文章结尾无关文本删除关键词

```
Funding Information|Online supplemental material|Not applicable|Ethical approval|Supplementary Material|Ethical aspects|Declared none
|Financial support and sponsorship|JX and SZ contributed equally to this article|SUPPLEMENTARY MATERIALS TABLE|SUPPLEMENTARY DATA|Supporting Information|The authors are grateful|Financial support and sponsorship|Statement of Ethics|Manuscript source|CONFLICT OF INTEREST|This article belongs to|Electronic supplementary material|Author.{0,5} contributions?|Thanks go to|This work was funded|Financial support|We would like to thank|CONFLICTS OF INTEREST|We gratefully acknowledge
[r'(No competing financial interests exist|statement:)']  # 匹配到就行
```

多余标点问题一般为之前的删除正则没有删干净遗留一些括号或特殊符号，已经补充到正则中

错误删除问题，错误删除的问题集中在通用删除问题里，由于本组数据里面比较复杂，而通用删除更多导致的是误删，所以对通用删除做了筛选，将用不到的或着是导致误删较多的正则进行了删除

