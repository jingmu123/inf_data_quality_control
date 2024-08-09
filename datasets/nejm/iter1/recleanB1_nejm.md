reclean2_nejm

无关文本

```
添加几个关键词
[r'(\(\s?([Ff]igs?(ure)?|F\s?IGS?(URE)?|Table|Details|Appendix|Funded|Section|epoch)s?[\s\.][^\(\)]*\))',r'删除2:<u>\1</u>'],   # 固定格式  带有（）的图片表格描述 附录描述 协议描述

[r'(\([^\(\)]*\sNCT\d[^\(\)]*\))',r'删除5:<u>\1</u>'],    #固定形式  删除（... NCT112233 ...） 描述什么机构 拨打电话

[r'(<sup>(<a>)?[\d\s\-—,]{1,10}(</a>)?</sup>)',r'删除3:<u>\1</u>'],   # 特殊格式的数字引用删除
删除3为特殊数字引用的删除，中间匹配数字的地方10个字符不够用，添加到20个字符↓
[r'(<sup>(<a>)?[\d\s\-—,]{1,20}(</a>)?</sup>)',r'删除3:<u>\1</u>'],   

[r'(\([^\(\)]*(www\.|NEJM.org.)[^\(\)]*\))',r'删除7:<u>\1</u>'],    # 匹配带括号且有网址特征的句子
```

文章中有大量的以 . . .结尾的句子，后面内容被省略

例：_To the Editor:_ There are two distinct areas of radiation oncology — external-beam radiotherapy and brachytherapy. The paper by Lichter and Lawrence (Feb. 9 issue) <sup>1 </sup> mainly summarizes the advances in external-beam radiotherapy, without noting the advances in brachytherapy. The current advances in external-beam radiation have greatly enhanced the precision with which radiation treatment is planned and delivered. They have also reduced radiation-related toxic effects and improved the rates of locoregional control in various cancers.The advances in brachytherapy, and the resulting advantages, are equally noteworthy. <sup>2 </sup> <sup>5 </sup> Brachytherapy deals with the delivery of radiation from sources positioned either close to the . . .

目前的解决办法是将最后半句删掉

```
[r'(\.)(([^\.]*\d+\.[^\.]*)?([^\.]*.( .){1,5}$))',r'\1删除6:<u>\2</u>'],     #删除以... 省略的后半句，中间允许出现一个数字加点
```

错误删除

正则删除4想要删除一些关于年份的描述，但是造成了误删,换一种特征去匹配

```
[r'(\([^\(\)]{,40}[,\s]\d{4}[^\(\)]{,40}\))',r'删除4:<u>\1</u>']
修改为
[[r'(\([^\(\)]{,40}N Engl J Med[^\(\)]{,40}\))',r'删除4:<u>\1</u>'],     # 带有括号的引用 例(N Engl J Med 300:9–13, 1979)     
```

















