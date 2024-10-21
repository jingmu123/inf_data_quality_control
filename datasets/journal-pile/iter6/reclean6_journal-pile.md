reclean6_journal-pile

reclean5_journal-pile分析

本次清洗较上次基本没有什么变化

本次清洗无关文本清洗90%，一些没有公共特征，有人名但是单从人名上去提取特征风险较大，约能提升6分

错误删除已经全部修复

主要关注点还是合格率

无关文本删除

```
[r'(^10.(7717|1136).*$)',r'删除41:<u>\1</u>'],  # 固定表述  单独一行 10.7717...
↓
[r'(^10.7717.*$)',r'删除41:<u>\1</u>'],  # 固定表述  单独一行 10.7717...

[r'(^(E-mail):[.\n]*)',r'删除44:<u>\1</u>'],   # E-mail:开头的句子
↓
[r'(^(E-mail|Twitter|Published|iThenticate screening|Financial source|Clinical Trial number \(ReBEC\)):[.\n]*)',r'删除44:<u>\1</u>'],   # E-mail:开头的句子


[r'(^Appendix .*)',r'删除53:<u>\1</u>'],   # 附录 。。。
[r'(^All calculations.*)',r'删除54:<u>\1</u>'],
[r'(.*the manuscript.*)',r'删除55:<u>\1</u>'],   # 。。。手稿 一般在末尾段落
# [r'(.*[A-Z]\.[A-Z]\.[A-Z]\..*)',r'删除56:<u>\1</u>'],
[r'(.*version to be published.*)',r'删除56:<u>\1</u>'], # ...版本
[r'(\(\s?(video)\s?\))',r'删除57:<u>\1</u>'],    # 括号 括号里面只有一个单词固定单词
[r'(\(\s?(see|Fig|[Ff]igure|Table)[^\)]*$)',r'删除58:<u>\1</u>'],    # 只有左半边括号 图片，表...
[r'\\',r''],   # 多余符号 \\
```

无关结尾删除添加

```
Contributor|Sources of Funding|References and recommended reading|The Supporting Information is|All authors contributed to the writing|Ethical clearance|Declaration of conflicting interest|We wish to thank|Trial status|Enhanced Digital Features|SUPPLEMENTAL DATA
```

错误删除已修复