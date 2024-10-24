reclean8_journal-pile

reclean7_journal-pile标注分析

从本次的标注结果上看，较上次基本没什么提升，主要问题还是在无关文本上

本次无关文本清洗可解决90%左右的问题，

错误删除全部纠正，在错误删除上纠正完之后可能会造成新的错误删除

本次将会重新加入短的文本，预计合格率上可能有5%的提升



无关文本清洗，本次的删除尽量不添加新正则，正则的数量已经较多，需要删除的形式基本都已出现，只在原来的正则上添加关键词



```
[r'^(The views expressed in this article).*',r''],  # 本文表达的观点
↓
[r'^(The views expressed in this article|Special thanks are extended|Supplementary Data online at|This work was part of the|A comment to this article is available online at).*',r''],  # 句子开头为某些关键词，整句shan'chu

[r'(^(E-mail):[.\n]*)',r'删除44:<u>\1</u>'],   # E-mail:开头的句子
↓
[r'(^(E-mail|Twitter|Published|iThenticate screening|Financial source|Clinical Trial number \(ReBEC\)|Acknowledgments|Citation):[.\n]*)',r'删除44:<u>\1</u>'],   # 已某些关键词开头且后面有:的句子

[r'(^(This|The)\s.{0,50} (was|is) .{0,15}(supported|funded|carried|approved|financed)[^$]*)', r'删除38:<u>\1</u>'],  # 这项研究得到了...的支持
↓
[r'(^(This|The|These)\s.{0,50} (were|was|is) .{0,15}(supported|funded|carried|approved|financed)[^$]*)', r'删除38:<u>\1</u>'],  # 这项研究得到了...的支持

[r'(^(The authors?|We are).*(thanks?|grateful|acknowledge|indebted|appreciates?|gratitude).*)', r'删除26:<u>\1</u>'],  # 作者感谢...的支持之类的描述
↓
[r'(^(The authors?|We are|Authors?).*(thanks?|grateful|acknowledge|indebted|appreciates?|gratitude).*)', r'删除26:<u>\1</u>'],  # 作者感谢...的支持之类的描述


[r'(DOI:\()?10\.\d{4}/.*(Table|Fig|Figure|Video)\.?\s?\d\.[A-Z].*',r''],   固定格式续放在删除41前
[r'(.*([A-Z]\.){2,}\s?(and\s?([A-Z]\.){2,}\s?){1,}.*)',r'删除60:<u>\1</u>'],
[r'[\.?!]{1,}(\n|$)',r''],      # 单行只有一个标点
```

末尾段落删除新增

```
匹配到开头
Shareable PDF|The author confirms that|Provenance and peer review|Availability of supporting data|Support for this research
匹配到就行
There were no sources of funding for the study|Supplementary Data online at
```