## reclean4_mimic_iv_discharge

### 1.句末结尾填空位置 多余换行补充

例如：

and they decided to commit suicide together.  ___ （多余换行）
outpatient psychologist called him at that time and suggested



suggestive of subacute to chronic hematoma/seroma. 6 ___ （多余换行）
catheter left to......

句末有句号和填空，并且下一段开头是小写字母，说明这是多余换行

补充到删除换行8：

```
((?:[A-Z，,;]|[DM][Drs]\.|\. *[0-9]*)[_ ]*(?:_)+[ -+]*)(\n+)( *(?:(?:[,，a-z‘)."“][^\n. ][^ \n:：]*( .*)?)|(?:[(（].{3,}[）)].*)))(?:\n)
```

### 2.小写字母—大写字母之间的多余换行的补充

例如：

circumferential edema, sensation intact to light touch in the 
RUE  （这里有多余的空格，导致没有匹配到）

补充到删除换行4：

```
(\n|^)( *(?:[^\n•●© ]{1,} +){4,}[^\n ]*[a-z，,0-9’;(/%\-+] *[-&*#]* *)(\n+)( *[A-Z][^.#\n•●©·:： ]*[^#\n•●©·:： ]*(?:(?: (?:(?:\d[:：]\d)*[^\n•●©·])*[^\n:：][^\n:：](?:\n|$))|(?: *\n| *$)))
```

### 3.小写字母—小写字母之间的多余换行的补充

例如：

___ 08:50AM BLOOD ___ pO2-35* pCO2-58* pH-7.30* 
calTCO2-30 Base XS-0 Comment-GREEN TOP

thick or like tomato juice 
color

补充连接符号：* 、，补充到删除换行1



例如：

........Mild（多余换行）

(1+) mitral regurgitation is seen. There is no pericardial  删除换行1 effusion.

mildly thickened. Severe （多余换行）
[4+] tricuspid

补充连接括号内容，改成起码括号内容有两个，并且起码要出现一个非数字字符，补充到删除换行1：

```
([a-z，,0-9’;()/] *(?:>|<|\+|\–|%|\'|≥|=|≤|-|&|~|"|\*|)* *)(\n+(?: *\n)?)( *(?:>|<|\+|:|%|\'|≥|=|≤|&|~|"|)* *(?:(?:["“,，./a-z‘)][^.])|(?:\$?\d+[^.\)][^.\\])|(?:[\(\[](?:[^\(\)\[\]\n]+[^\(\)\[\]\n0-9]+|[^\(\)\[\]\n0-9]+[^\(\)\[\]\n]+)[\)\]])))
```

### 4.大写字母—大写字母之间的多余换行的补充

例如：

\# Lightheadedness and Syncope: His symptoms were likely from  删除换行1 dehydration.  Patient describes orthostatic symptoms that  删除换行1 started shorly after increasing his diuretic regimen.  At OSH (多余换行)

ED, while patient



TO RCA, diffuse LAD(多余换行)

(max 80%) stenosis. 

去除标题限制，开头可以出现井号、增加下一段括号内容的连接，补充到删除换行15：

```
(\n|^)( ?(?:[^\n•●© ]{1,} +){5,}[^\n]+[A-Z] *)(\n+)( *[A-Z][^\n\. ]*[^:：\-] +(?:(?:(?:[^\n•●©:： ]{1,} +){5,}.*)|(?:[^\d\.\n:：]{2,}\. *(?:\n|$)))|(?: *\([^\(\)\n]{3,}\)))
```

### 5.非序号数字处多余换行

例如：

Pulsus at that time was （多余换行）

12.（非序号）

增加单独一行的数字的连接，因为这类数字不是序号，补充到删除换行14：

```
([A-Za-z，,0-9’;()/] *(?:>|<|\+|\–|%|\'|≥|=|≤|-|&)* *)(\n+(?: *\n)?)( *(?:>|<|\+|:|%|\'|≥|=|≤|&|~)* *(?:(?:\$?\d+\.\d+)|(?:\$?\d+ *[,，])|(?:\$?\d+ *\. *\n)) *)
```

### 6.特殊填空位置多余换行

例如：

You will have labwork drawn every ___ and ___ at the 
___ Lab (First Floor) with results to the  删除换行1 transplant clinic.

上一段结尾是小写字母，下一段填空位置后开头是大写字母，这类的不能直接写正则处理，因为检索全量发现会出现很多缺少换行，现在增加一类特殊的删除换行，上一段文本最后一个单词是非结尾性质的单词是，删除换行，例如：is、was、the...后面如果有再补充，增加删除换行：

```
( +(?:the|is|was) *)(\n+)( *(?:_)+ *(?:[0-9]+|(?:[:：].*))? *(?:(?:[-+,，A-Z‘).][^.])|(?:\n|$ *)))
```