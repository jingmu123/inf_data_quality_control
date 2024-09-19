## reclean4_medical_case的清洗

### 1.空选项的删除

例如：
(a) (b)
(a) (b)304
单独一行出现，结合上下文确定没有意义
增加删除：

```
(?:\n|^)((?:\([a-z]\) ?\d*)+)(?:\n)
```

### 2.新出现的人物介绍的删除

例如：
_Jennette Firlein_
_Nemours/Alfred I. duPont Hospital for Children, Wilmington, DE, USA_
增加删除30：

```
(=+\n+)((?:.*\n+)(?:.*USA_?\n+)+)
```

## 3.表格标题的删除（没有内容）

3.1 例如：Table 4-2 lists...
增加删除：

```
(?:\n|^)(Table \d+[-–]\d+ [^\n•]*)(\n+[^\n|])
```

3.2 例如：
Tablee 11： ：Cimnical/ biochenical...
增加删除：

```
(?<=\n)(Tablee? *\d+[：:].*)
```

### 4.特殊符号的补充

例如：†、￥、(●、■
补充到特殊符号删除：(�|◻||◆|†|￥\d*||\(●|■\(?)

### 5.人物事迹的删除

例如：

In 1867， Potain described the waveforms of the internal jugular vein.

In 1902， James Mackenzie championed that the jugular venous pulse is an essential part of the cardiovascular physical examination.
增加删除：

```
(?:\n)((?:In \d{4}.*(?:\n|$)+){2,})
```

### 6.转载类的补充

例如：
Reproduced by permission from Benarroch, Eduardo E., Jeremy K. Cutsforth-Gregory, and Kelly D. Flemming, Mayo Clinic Medical Neurosciences: Organized by Neurologic System and Level (New York, New York: Oxford University Press, 2017).### Additional information

补充到删除21

### 7.资源介绍类的删除

例如:
Source： Courtesy of Joseph M. Lane， MD.
增加删除31：

```
(?<=\n)( *Source *[：:].*)
```

### 8.拼音人名的删除

例如：
(Hao Li, Guoju Dong, Bing Wang, Tingting Zhang)
增加删除32：

```
(?<=\n)(\(([A-Z][^A-Z\n\d]+ )+[A-Z][^A-Z\n\d]+\) *\n*)(?:$)
```

### 9.图片索引的删除

例如： (Fig. 9.2 )
增加删除33：

```
(\([^()\n]*F[iI][gG][sS]?(?:ures?|URES?|\.)?[^()\n]*\))
```

### 10.多余标点的删除

例如：●(Generalized pigmentation（左括号是多余标点）
增加删除：

```
(?:\n)([●·])( *[。(])
```

例如：●History of intravenous drug abuse●●●●（后面的是多余标点）
增加删除：

```
(●+)(?:\n|$)
```

### 11.多余换行问题

之前因为有些断句的连接处是大写字母，不好处理，现在增加大写与小写之间的多余换行
11.1 上一段结尾字符是小写字母，下一段开头是大写字母，增加换行删除：

```
((?:[^\n ]{1,} +){5,}[^\n ]*[a-z，,0-9’:：;()/] *)(\n+)( *[A-Z][^. ] *(?:[^\n ：:]{1,} +){5,}[^\n :：]*)
```

11.2上一段结尾字符是大写字母，下一段开头是小写字母，增加换行删除：

```
((?:[^\n ]{1,} +){5,}[^\n ]*[A-Z] *)(\n+)( *[a-z，,0-9’:：;()/][^. ] *(?:[^\n ：:]{1,} +){5,}[^\n :：]*)
```

### 12.无用索引的删除

例如：3\. List the diagnostic criteria for SLE. (EPA 3，12)  （括号内的内容是无关文本）

增加删除34：

```
(\([^()\n]*EPA *\d+(?:[ ，]+\d+)*\))
```
