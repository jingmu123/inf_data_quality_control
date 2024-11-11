## reclean8_acjr_mdpub_cases问题
### 无关文本：
1.无关段落，Medical College， Thane. 400605，+918390465676， drmohi44@gmail.com，、DO： 10.5455/JMRCR.172-1643143162、Intensive Care Unit，、Maria Lume\*1， Salom Garcia\*，、Sep. 2004 Dec. 2004 Feb. 2005 Jul.2005、Medical School， University of Western Australia，、We are thankful to等。
```
[r'(^(Medical College， Thane|DO： 10\.5455\/|Intensive Care Unit，|Sep. 2004|Medical School，|We are thankful to).*)', r''],
```

2.通用结尾删除遗漏，ending_starts里补充Data availability、Conflict if interests、No relevant conflict of interests.、Ethics and Dissemination、Disclosure of interest等
```
[r'^[#\*]{0,4}\s?(Data [Aa]vailability( Statement)?|(Acknowledgements )?Cc?onflic?ts? [oi]f [Ii]nterest( and source of funding| [Ss]tatement)?|No relevant conflict of interests\.|Ethics and Dissemination|Disclosure of interest)s?[：\.]?[#\*]{0,4}\s{0,}($|\n)'],
```

3.References里提取出了无关文本，http/www.mp.pt/artykuly/?aid=29002、Arch Dermatol 2004、New York， 1989等。

将原先不符提取特征网址：```(htt[tp]s?[：:]\/\/)```，更改为：```(htt[tp]s?[：:]?\/)```

将原先不符提取特征年份：```([;；： ，\.]+(20|1[6-9])\d{2}[;；： ，\.])```，更改为：```(20|1[6-9])\d{2}```

4.零碎无关段落，SDF、TTT等
```
[r'(^(\w{1,3})$)', r''],
```

5.括号内一半无关内容图例，(3 bottle drainage system， Fig-3)、(2 bottle drainage system ， Fig-2)等。
```
[r'([（\(][^\)\(（）]*[^\.， ,])([\.， ,]+[Ff]igs?(ure)?[\- ]\d+)([\)）])', r'\1\4'],
```

6.文中或文末的Consent标题及其下一段无关内容。
```
context = re.sub(r'(\n\n(Consents?)\n\n.*)', r'', context)
```













