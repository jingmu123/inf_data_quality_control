## reclean5_acjr_mdpub_cases问题
### 无关文本：
1.删除无关段落。

a. Depaitment of Orthopedics， University Hospital of Patras， Patras， Greece.
```
[r'((^(?=.{0,75}$).*(Department| Center|et al).*)|(^(?=.{0,150}$).*(Depa[ri]tment of|Tel：|@[a-z]{2,10}\.com).*))', r'删除14:<u>\1</u>'],
```

b. The authors would like to thank Katarzyna Jonczyk-Potoczna，删除12补充。
```
[r'(^((We|The authors) would like to (acknowledge|thank)|American Medical Center，).*)', r'删除12:<u>\1</u>'],
```

c. American Medical Center，、Respiratory Medicine Department， Diana Princess of Wales Hospital， Grimsby， United Kingdom。删除14补充关键字，将范围改为0-100。
```
[r'((^(?=.{0,100}$).*(Department| Center|et al|Medical|Medicine).*)|(^(?=.{0,150}$).*(Depa[ri]tment of|Tel：|@[a-z]{2,10}\.com).*))', r'删除14:<u>\1</u>'],
```

2.通用结尾删除，ending_starts里补充Declarations of interest、Informed consent and patient details、Cconflicts of interest、Disclosure of financial arrangement、Ethics Committee、Informed consent
```
[r'^[#\*]{0,4}\s?(Ethic(s|al) ([Cc]ommittee ?)?([Aa]pproval：?)?( and informed consent)?|(Acknowledgements )?Cc?onflic?ts? of [Ii]nterest( and source of funding)?|Informed consent( and patient detail)?|Disclosure of financial arrangement)s?[：\.]?[#\*]{0,4}\s{0,}($|\n)'],
```

3.补充删除无关文本， \[figure2，34J.、(Table、1)、See Figure 1.、\[Table1T
```[r'((\\?[\[\(][Ff]igure[^\]\.\\]*\\?[\]1lJ])|(\\\[[Ff]igure))', r'删除19:<u>\1</u>'],```
```[r'((\(Table|\\\[Table1T)$)', r'删除23:<u>\1</u>'],```
```[r'(\([Pp]icture ?\d+\)|See Figure \d+\.)', r'删除22:<u>\1</u>'],```

4.删除括号内人名注释， (Brugueras et al.， 2020； Monge -Maillo et al.，2015；Sonden et al.2014)
```
[r'([（\(][^\)\(（）]*[\.， ,]+(20|1[6-9])\d{2}[\)）])', r'删除20:<u>\1</u>'],
```

5.无关零碎简短段落，1\)、OSG\. B、Japan、C： 957.0.W： 1913.0、WaS直接删除。
```
[r'(^(50um|1\)|OSG\. B|Japan|C： 957.0.W： 1913.0|WaS)$)', r'删除17:<u>\1</u>'],
```

6.References里正文内容未正确提取，造成无关文本，不符提取特征补充，补充单独年份： 2019.、 卷号期号5th ed； vol. 1。类似网址httt：、\.himl等特殊情况。
```
(\d{4}[;；： \.]+\d+(\(\d+\))?[:：； ]*[\d\-]+)|(htt[tp]s?[：:]\/\/)|([^\[]\d+(\(\w+\))?[:：； ]*\d+[\-]\d+)|([;；： ，\.]+(20|1[6-9])\d{2}[;；： ，\.])|(^Table \d)|([Vv]ol\.| ed[\.；]|Volume|\.h[ti]ml)
```

### 多余换行：
1.上段小写结尾，下段是大写开头的特殊情况，stem-related embryonic antigens OCT4 and(\n换行\n)Nanog . Indeed， MPBCs were found to。inactivating genetic polymorphisms in the(\n换行\n)CYP2C19gene. This gene encodes、 screw (2.4 mm Cortex Screw，DePuy(\n换行\n)Synthes) ；the distal
```
context = re.sub(r'([^|\n]{100,}[，,a-z])(\n+\n *)([A-Z][A-Za-z\d]{3,}[ \.,，；\)]+.{40,})', r'\1|删除5换行|\3', context)
```

2.a. 上段数字结尾，下段\[开头，\[CXCL，GRO-x \[CXCL-1J，NAP-2(\n换行\n)\[CXCL)，

b. 上段逗号结尾，下段数字开头，type oftactile response，(\n换行\n)6.67% each.

c. 上段等号结尾，下段数字开头，than controls. (P-value=(\n换行\n)0.04).

d. 上段小写结尾，下段数字开头，from baseline or a(\n换行\n)0.5 mg/dL (44 umol/L) 
```
context = re.sub(r'([^|\n]{50,}[a-z\-\d，\=])(\n+\n)( *\.|\\\[|\d+\.\d+ ?(\%|\)|mg\/))', r'\1删除3换行\3', context)
```










