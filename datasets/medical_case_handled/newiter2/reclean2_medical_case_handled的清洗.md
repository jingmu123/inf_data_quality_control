## medical_case_handled的清洗

1.无用标题的删除

例如：

Ethics and Law in Clinical Practice: Beginning of Life

临床实践中的伦理与法律:生命的开端（冒号后面的名字会改变，检索全量，发现这类标题是无用的，下面也没有内容）

增加删除22：

```
[r'((?:ETHICS AND LAW IN CLINICAL|Ethics and Law in Clinical) *\n*(?:PRACTICE|Practice):.*)',r'删除22：<u>\1</u>'],
```

2.特例句子的删除

例如：

main perforators of the thigh and leg.（后面是无关文本）VARICOSE VEIN AND VENOUS ULCER 147

drugs is in doubt.（后面是无关文本）174 A TEXTBOOK ON SURGICAL SHORT CASES

 infrahyoid.（后面是无关文本）SWELLINGS IN THE NECK 107

这类特例总是固定的句式，整句大写，前面或后面会跟着数字，联系上下文发现是无关文本

增加删除27：

```
[r'(VARICOSE VEIN AND VENOUS ULCER \d+|SWELLINGS IN THE NECK \d+|\d+ A TEXTBOOK ON SURGICAL SHORT CASES)',r'删除27：<u>\1</u>'],
```

3.补充 医院介绍类的删除

例如：

William Eng <sup>1 <a><span class="ContactIcon"></span></a></sup> and Martin J. Walsh <sup>2</sup>

(1)

Department of Pathology, University of Central Florida Medical School, Orlando, FL, USA

Email: drwilliameng@yahoo.com

xxx（正文标题，可能不存在）

（之前会已开头的特殊格式匹配到下一个正文标题结束，但是像这类是没有一个标题去截断的，所以漏掉了）

补充删除2，分为两条正则，这条为没有标题截断的：

```
[r'(?:\n|^)((?:.*class="ContactIcon">.*\n+)(?:.*\n)*)(Email:.*)',r'\n删除2：<u>\1\2</u>'],
```

4.文献类的补充

例如：

(CLINICAL)? CASE CORRELATION | Suggested Reading | Disclosure Statement   （标题）

xxx

xxx（这类标题开始的以下内容是无关文本）

补充到删除16：

```
[r'(?:\n|^)(#* *(?:Recommended Reading|Bibllography|REFERENCES?|Further Reading|(?:CLINICAL)? CASE CORRELATION|Suggested Reading|Disclosure Statement)\n*(?:.*\n*)*)(?:\n|$)',r'删除16：<u>\1</u>']
```

5.转载许可、改编许可的删除

例如：

(Reproduced， with permission， from Le T， et al. First Aid for the USMLE Step 1： 2011. New York： McGraw-Hill， 2011：270.\]

增加删除21：

```
[r'(?:\n|^|\()( *(Reproduced，|Adapted) with permission[^\n()（）\[\]]*)(?:\n|\)|\])',r'删除21：<u>\1</u>']
```

6.数据来源类的删除

例如：

**_(Data from Stone NJ， Robinson J， Lichtenstein AH， et al. ACC/AHA Guideline on the Treatment of Blood Cholesterol_ _to Reduce Atherosclerotic Cardiovascular Risk in Adults： a report of the American College of Cardiology/Am erican Heart_ _Association Task Force on Practice Guidelines published online Novem ber 12， 2013\]. Circulation. doi：10.1161/01._ _cir：0000437738.63853.7a.)_**

增加删除23：

```
[r'(?:\n|^|\()( *Data from\D[^\n()（）]*\d{4}\D[^\n()（）\[\]]{0,20})(?:\n|\))',r'删除23：<u>\1</u>']
```

7.请参考...类的删除

7.1单行出现的

例如：

Please refer to Case 44 for discussion.

增加删除：

```
[r'(?:\n|^)( *Please refer to.*?)(?:\n)',r'删除24：<u>\1</u>']
```

7.2 穿插在文中的

例如：

...side effects.（这句话是参考）Please refer to Chapter 12 on noninvasive ventilation.The use of invas...

增加删除：

```
[r'(\.)( *Please refer to.*?(?:\(p\. \d+\)\.\d+)?)(\D\.|\n)',r'\1删除24：<u>\2\3</u>']
```

8.参见...类的删除

例如：

See also Case 14 (Pulmonary Embolism)， Case 15 (Chronic Obstructive Pulmonary Disease)， and Case 16 (Chronic Cough/Asthma).

增加删除：

```
[r'(?:\n|^)(See.*(?:page|Table|Case|text).*)',r'删除25：<u>\1</u>']
```

9.多余标点的删除

例如：

! The Ficat classification

。SScleral and mucosal icterus with physical findings consistent with ascites

增加删除：

```
[r'(?:\n|^)(!|\.|;|。)',r'删除26：<u>\1</u>']
```

10.通用参考类的删除（这类没有标题）

例如：

**De Ugarte CM， Buyalos RP， Laufer LR. Puberty and disorders of pubertal development. In： Hacker NF，** **Moore JG， Gambone JC， eds. Essentials of Obstetrics and Gynecology. 6th ed. Philadelphia，PA：Saunders： 2015：386-397.**

**Fritz MA，SperoffL.Normal and abnormal growth and puberty. In： Fritz MA， Speroof L. Clinical Gyne-cology and Infertility. 8th ed. Philadelphia， PA： Lippincott Williams and Wilkins； 2012：391-410.**

**Pisarska MD， Alexander CJ， Azziz R， Buyalos RP. Puberty and disorders of pubertal development. In：Hacker NF，Gambone JC， Hobel CJ， eds. Essentials ofObstetrics and Gynecology. 6th ed.Philadelphia，** **PA： Saunders； 2015：345-354.**

这类没有标题，只能去匹配这个文献的格式，测试正则后发现不存在误删，增加删除20：

```
[r'(?:\n)((?:(?:.*((?:\d{4}(?: *.{0,9} *\d*)?[;；:：])|(?:[:：;；,，] *\d{4}))\d*(\([0-9A-Z]+\))?[:：]?[0-9A-Za-z]*(?:-\d+)*)[^\n)\]]{0,15}(\n{1,}|$)){2,})',r'删除20：<u>\1</u>']
```

11.表格名称的多余换行

例如：

Table 11.1

Various “cool down” methods prior to initiating phototherapy for inflammatory skin conditions

增加删除换行：

```
[r'(?:\n|^)(Table \d+\.\d+)(\n+)(.*[^.?!])',r'\1 删除换行 \3'],
```

12 修改通用删除换行

补充上一段文本结尾字符：/（

```
[r'([a-z，,0-9’:：;()/] ?)(\n+)([a-z0-9‘)][^.][^.])',r'\1 删除换行 \3'],
```