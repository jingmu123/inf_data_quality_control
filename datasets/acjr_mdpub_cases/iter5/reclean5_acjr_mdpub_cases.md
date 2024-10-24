## reclean4_acjr_mdpub_cases问题
### 无关文本：
1.补充通用结尾段落删除，| REFERENCES：  |、Conflicts of interest and source of funding、Declaration of competing interests、CONFLICT OF INTEREST、ACKNOWLEDGMENT、Declaration of interests、1\. Littre E： Oeuvres completes d'Hippocrate. 10 volumes， Paris： Bailliere et、1. Rafael H： 。。等。ending_starts里补充：
```
(\|? *REFERENCES?：? *\|?|(Acknowledgements )?Conflic?ts? of [Ii]nterest( and source of funding)?|Declaration( of( competing)? interest)?|CONFLICT OF INTEREST：?||ACKNOWLEDGE?MENTS?)
```
```
[r'(^(\d|l)\\?\..*\d{3,4}[;；：\.] ?\w+(\(\d+\))?[:：\.；]?[\w \-]+.*)|(^(\d|l)\\?\. ?[A-Z][a-z]+ [A-Z]：)']
```

2.无关段落，Supplementary Materials、Diaz PJ， Garcia SF， Sanchez LJ， Saborido FJ.、Our data were obtained under the、come of Surgical Treatment、Northwestern Tanzania： A Tertiary Hospital Experience、World Journal of Emergency Surgery， 6， 31、Graph 1： Mean dose。。、Graph 2： Mean dose、Head and Neck tumours：、bone tumours. Virchows Archiv. 2018. 、We want to thank、This study received no 、Histopathological proven stage Ⅲ&IVA、S1S.ociety of America：、This study was approved by。。、address：、number： 等。
```
[r'(^(Our data were|Diaz PJ，|Supplementary Material|come of Surgical|Northwestern Tanzania：|World Journal|Graph ?\d+：|Head and Neck tumours： |bone tumours\.|We want to thank|This study (received no|was approved)|Histopathological proven|S1S\.ociety|[Aa]ddress：|number：).*)', r'删除21:<u>\1</u>'],
```

3.零散简短无关段落，Frame 30 of 44、Flow chart for study、(CT3-4a，cN0-2c)、125 1000、CDS-FITC、C F CD19-PCS、Follow-up、apy. 2009.、December 2018.等，删除17补充：
```
[r'(^([a-z][\w]{0,20}|[\d\/]{1,10}|Images|B0ml i.v. KM|Frame \d+ of \d+|Flow chart for study|\(CT3-4a，cN0-2c\)|\d+ \d+|[A-Z]{3,4}\-[A-Z]{3,4}|C F CD19-PCS|Follow-up|apy. 2009.|December 2018.)$)', r'删除17:<u>\1</u>'],
```

4.括号内图片索引，(picture 2)、(Picture 1)等。
```
[r'(\([Pp]icture ?\d+\))', r'删除22:<u>\1</u>']
```

5.通用间距删除delete_page_middle里结尾标记补充，```(^[a-z]{1,3}.{72,}\.)有句号的句子补充结尾符$,(^[a-z]{1,3}.{72,}\.$)```。

6.遗漏的参考文献，1\. Bobba RK， Arsura El， Sarna PS et al：，无标题的参考文献通用结尾删除ending_starts格式补充 。
```
[r'(^(\d|l)\\?\..*\d{3,4}[;；：\.] ?\w+(\(\d+\))?[:：\.；]?[\w \-]+.*)|(^(\d|l)\\?\. ?[A-Z][a-z]+ ?[A-Z]{1,2}[：\.，])']
```

### 多余换行：
1.表格插入导致的多余换行，由于普通多余换行处理在表格换行之前，导致一些表格换行格式匹配不上，将表格插入换行复制一条在普通换行前。
```
context = re.sub(r'([a-zA-Z，\d\--])(\n+\n((Supplementary )?Table|\|) [\W\w]*?)(\n+\n)(([a-z\(][^ \--].*)|([A-Z][a-z]{2,10}\..{100,}))', r'\1 \6\2', context)
```

2.补充删除换行，上段小写字母或逗号结尾，下段大写开头且非标题的多余换行，可能会有误删换行。
```
context = re.sub(r'([^|\n]{50,}[，,a-z])(\n+\n *)([A-Z][a-z]{3,}[,，].{40,})', r'\1 \3', context)
```

3.标题插入导致的多余换行，例如： Augments were utilized to reconstitute\n\n(换行)Discussion\n\n(换行)the anatomical joint line，。
```
context = re.sub(r'([^|\n]{50,}[，,a-z])(\n+\n *([A-Z][A-Za-z]+( and)?( [A-Z][A-Za-z]+)?)\n+\n *)([a-z].{50,})', r'\1|删除标题插入换行|\6\2', context)
```

4.处理换行时上一段的字符限定更改为45，补充了数字开头非标号的多余换行。caspofungin (MIC 2 yg/mL) and amphotericin-B (MIC删除2换行1 vg/mL). Candida 
```context = re.sub(r'([^|\n]{45,}[a-z，：\-\d])(\n+\n)([a-z\(&][^\.\)]|\d+[^\.\\\)s])', r'\1删除1换行\3', context)```
```context = re.sub(r'([^|\n]{50,}[^\.])(\n+\n *)([a-z][^\)\.]|\d+ ?[^\.\\\)s])', r'\1删除2换行\3', context)```

5.分段处理时，一些处理后空的段落在拼接时会有多余的\n，在clean_text里分段处理后加入```final_results = [con for con in final_results if con]```








