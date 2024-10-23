reclean7_journal-pile

reclean6_journal-pile结果分析

第六轮清洗在合格率上有了提升，但是本次的错误删除的数量增多，还有一些无关文本需要处理



无关文本删除新增

```
[r'10\.\d{4}/.*(Table|Fig|Figure)\.?\s?\d\.[A-Z].*',r''], # 必须添加到删除41和删除43的前面
[r'(.*the manuscript.*)',r'删除55:<u>\1</u>'],   # 。。。手稿 一般在末尾段落
↓
[r'(.*(the|a) manuscript.*)',r'删除55:<u>\1</u>'],   # 。。。手稿 一般在末尾段落

[r'(^(Presented at|Cite this article as|Sample Availability)\s?:.*$)',r'删除59:<u>\1</u>'],       #进宫朝见...？
[r'^(The Supplementary Information|Source code|Financing|To cite this article|None declared).*',r''],   #补充信息开头整句话
[r'.*([Aa]uthors have equally|Patient consent)[.\n]*',r''],        # 作者的贡献...
[r'(^We would like to (express special thanks|acknowledge).*$)',r''],   # 我们要感谢。。。
[r'(^.*(A|a) sincere thank you.*)',r''],
[r'^(The views expressed in this article|Special thanks are extended).*',r''],  # 本文表达的观点
[r'.*[cC]onceived and designed the experiments.*',r''],
[r'^(SUPPLEMENTARY FIGURES|Supplemental Material|Supplemental Information).*(\n.*)?',r''],
[r'^\s?Raw data\s?$',r''],
```

错误删除

```
[r'(.*10\.\d{4}[^\d].*$)',r'删除41:<u>\1</u>'],  # 固定表述  单独一行 10.7717...
↓
[r'(.*[^\d]10\.\d{4}[^\d].*$)',r'删除41:<u>\1</u>'],  # 固定表述  单独一行 10.7717...
另在删除41前添加
[r'(DOI:\()?10\.\d{4}/.*(Table|Fig|Figure|Video)\.?\s?\d\.[A-Z].*',r''],

有几条是因为删除38，这条正则删除的无关文本数量远大于误删的数量，先保存
[r'(^(This|The)\s.{0,50} (was|is) .{0,15}(supported|funded)[^$]*)', r'删除38:<u>\1</u>'],  # 这项研究得到了...的支持

```

