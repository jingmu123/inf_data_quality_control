reclean3_journal-pile

reclean2_journal-pile清洗合格率87.584%，质量分96.37555，已经很接近达标，目前又发现少量新的无关文本，和个别多于标点，无关数字等问题，但是由于文件数据量较大，本次解决完问题后会继续抽样

新增正则删除无关文本

```
[r'([\.;]\s([Ff]igs?(ure)?|F\s?IGS?(URE)?|Table|[sS]ee|For more|http|www)s?[\s\.:\d][^\(\)]*)(\))',r')'],    # （）内出现(dose---F~(4,\ 52)~ = 5.312, p = 0.001; group × dose \[F~(4,\ 52)~ = 2.539 p = 0.051\]; Fig. [2a])，删除;后面出现的Table、Fig...到后面的右括号
[r'(^The following are available online.*)',r'删除31:<u>\1</u>'],     # 一下内容可在...找到，一版后面接的是网址
[r'(.*These authors contributed equally to this work.*)',r'删除32:<u>\1</u>'],   # 固定表述
```

新增正则删除无关数字

```
[r'(\[\^\d+\])',r''],   # 无关数字
[r'(\(:\s?[①②③④⑤⑥⑦⑧\-⑨⑩\s,\.]{1,}\))',r''],
```

无关文章结尾内容删除

```
Additional Information|There is no funding|We are indebted to|The online version of this article|Under the direction of the authors|The work was supported|Thanks to all the|This article is distributed|We are grateful to|The work performed at
```