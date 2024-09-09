## medical_case_handled的清洗

## 1.作者许可类

例如：
© The Author(s), xxxxx 2023（开头的格式与结尾的年份是特征）
xxxhttps://doi.org/10.1007/978-3-031-20193-6\_16（一般在作者许可的下一句或上一句，特征是结尾的网址）
上面例子的第二句又是会在上面，第一句在下面，为了避免正则太长，分成两句正则去删除。
增加删除1：

```
(?:\n|^)((?:©.*\d{4}\n*)(?:.*(?:https?:\/\/(?:www\.)?|www\.)?[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9]{2,})+(?:\/[^ \n\u4e00-\u9fa5]*)?))
```

## 1.2 特殊格式的地址类的介绍

例如：
Atooshe Rohani <sup><a>1</a><a><span class="ContactIcon"></span></a></sup>
(1)
Northern Ontario School of Medicine, Thunder Bay, ON, Canada
Atooshe Rohani
Email: arohani@nosm.ca
增加删除2：

```
(?:\n|^)((.*(?:https?:\/\/(?:www\.)?|www\.)?[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9]{2,})+(?:\/[^ \n\u4e00-\u9fa5]*)?\n*)(©.*\d{4}))
```

### 1.3图片索引与图片描述类的删除

例如：
Fig. 63.1 . The appearance of the Umbrella cockatoo being positioned for whole body radiographs.（单行出现）
Fig. 19.2
Alopecic nodular lesions on the hairy scalp with malodorous discharge（索引与描述存在换行，特征为下面如果为描述没有标点符号结尾）
增加删除3：

```
(?:\n|^)(Fig(?:ures?|\.) ?\d+\.\d+(?:\n+(?:[^\n ]{1,} ){3,}[^\n ]{2,}[^.?!]|.*))
```

### 1.4表格类的删除

例如：
Table 63.1 . Hematology findings.
<sup>a </sup> Campbell and Ellis (2007).
<sup>b </sup> Johnston-Delaney and Harrison (1996).
增加删除4：

```
(?:\n)(Table [0-9.]+ \. .*\n+)(\n<sup>(<em>)?[a-z ]+(<\/em>)?<\/sup>.*\n)+
```

### 1.5无关数字的删除

例如：
24（单独一行出现）
the efficacy and potency of drugs.43（出现在句尾）
增加删除5：

```
(\n|\.|\?|!)(\d+)(?:\n)
```

### 1.6特例句子的删除

例如：This page intentionally left blank（意思：这一页故意空着）
这一句可能会单行出现也可能与其他句子连接
增加删除6：

```
([_*]*This page intentionally left blank *(?:\d+|to match pagination of print book)?[_*]*)
```

### 1.7举例的删除

例如：
100 Cases in Emergency Medicine and Critical Care
100 Cases in Clinical Ethics and Law
增加删除7：

```
([0-9 ]+ Cases in[^\n.]*)(?:\n)
```

### 1.8特殊符号的删除

例如：repli口cation
会在某些单词里出现方框
增加删除，后续还有类似的就继续补充

### 1.9网址删除

例如：http://taylorandfrancis.com297
增加删除：((?:https?:\/\/(?:www\.)?|www\.)[ a-zA-Z0-9-]+(?:\.[a-zA-Z0-9]{2,})+(?:\/[^ \n\u4e00-\u9fa5]*)?)

### 1.10（人名+年份）的删除

例如： (Westra 2004 )
增加删除10：

```
(\\?[(（[][^\d\n][^()（）\[\]\n%=]+\d{4}[^()（）\[\]\n%= ]{0,2} *\\?[)）\]])
```

### 1.11一些特例句子的删除

增加删除：

```
(?:\n|^)(> Courtesy of Dr. Mae Melvin, Centers for Disease Control and Prevention.|> Reproduced, with permission, from USMLERx.com.|FAITH, VALUES AND CULTURE|Faith, Values and Culture|_Kimberly L. DiMaria_|_Children’s Hospital Colorado, Aurora, CO, USA_)
```

### 1.12多余换行

例如：
He is found to have multiple metastases and it is likely that he （多余换行）
is in the terminal stage of his disease.
添加删除换行：

```
([a-zA-Z，,0-9’:：;()] ?)(\n+)([a-z0-9‘()][^.])
```

### 1.13 空标题的删除

例如：

Key Points15

Case 8: Another Doctor’s Patient

这类标题下面没有内容，属于无关文本

增加删除12：

```
(?:\n|^)((?:Key Points[0-9]+\n+)(?:Case [0-9]+:.*)?)
```

### 1.14作者介绍

例如：

By Kathy J. Booker， PhD， RN

增加删除11：

```
(?:\n|^)(By [A-Z].*[^\n.])
```

1.15案例例子删除

例如：

**CASE CORRELATES**

●See Cases 1-10 (cellular and molecular neuroscience cases).

增加删除13：

```
(?:\n|^)([*| ]*CASE CORRELATES[*| ]*\n*[*| -]*\n*[*| -●·]*See.*\n{0,2}[| -]*)
```

### 1.15汉字与单行单独字母的删除

例如：

59.55 上Benign cystic teratoma (dermoid cyst)（偶尔会出现无关汉字，在这次英文任务中，不会出现汉字）

R（会出现一行一个字母的情况）

增加删除

```
([\u4e00-\u9fff])
(?:\n|^)([A-Za-z]{1,2})(?:\n)
```

### 1.16推荐阅读删除

例如：

Recommended Reading

Goldsmith LA et al. Fitzpatrick’s dermatology in general medicine. 8th ed. New York: McGraw-Hill Co; 2012. p. 2367–8

增加删除16：

```
(?:\n|^)(Recommended Reading\n*(?:.*\n*)*)(?:\n|$)
```

