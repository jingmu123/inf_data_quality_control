## reclean5_medical_case_handle

### 1.补充 改编 许可类的删除

例如：
(Adapted， with permission， from Mescher AL. Junqueira’s Basic Histology： Textand Attas， 12th ed. New York： McGraw-Hill， 2010： Figure 16-11.\]
补充到删除21：

```
(?:\n|^|\()( *(?:Reproduced，?|Adapted，?) (?:with permission|from|by).*)(?:\n|\)|\])
```

### 2.修改单行字母的删除

扩大范围，单行字母或数字出现三个及以下会删除
补充到删除14：

```
(?:\n|^)( ?\'?[A-Za-z0-9](?: ?[A-Za-z0-9]){0,2} *)(?:\n|$)
```

### 3.参见类删除的补充

例如：
(characteristic facies， history of steroid ingestion； see p.538)   （缩写的页数）
补充到删除25：

```
(\([^()\n]*see[^()\n]*(?:page|[pP]\.\d*|Table|Case|text|Plate)[^()\n]*\))
```

### 4.标注类的删除

例如：
NOTE： The author would like to recognize Amanda La Manna， RN， ANP for her contribution to the editing of this case.
增加删除35：

```
(?<=\n)(N(?:OTES?|otes?)[：:] *The author.*)
```

### 5.人物介绍类的删除

例如：
Sir Johnathan Hutchinson (1828-1913) was ....

H Clutton (1850-1901)， an English surgeon who worked at St Thomas’s Hospital， London.

Emanuel Zaufal (1833-1910)， a Czechoslovakian rhinologist.
增加删除36：

```
(?:\n)((?:(?:[A-Z]+[^A-Z\n ]* ){2,}\(\d{4}-\d{4}\).*(?:\n|$)+){2,})
```

### 6.修改图片描述的删除

之前是对图片描述只删除大于等于3个单词的描述，发现会漏删。现在改为字数限制，11个字符以上。

### 7.修改人物加年份类的删除

误删了两例：
(white blood cell [WBC] count was7300/uL， platelet count 401，000/pL， and creatinine 0.5 mg/dL)
(normal range： 313-6181U/L)
把带单位的数量识别成年份了，修改正则，在年份后面不会出现单位符号/

### 8.多余标点删除

8.1 例如：

 |（多余符号）CASE 5**

增加删除37：

```
(?:\n|^)(\|)(CASE \d+)
```

8.2 例如：

(（多余符号）Gastroesophageal reflux disease.

增加删除38：

```
(?<=\n)([^\n\(\)]*)(\()([^\n\)]*)(?:\n)
```

8.3 例如：

B)（多余符号）.Increased preterm delivery rate

增加删除38：

```
(?<=\n)([^\n\(]*)(\))(.*)(?:\n|$)
```

8.4 例如：

but there use is empiric and not evidence-based.。（多余中文句号）

增加删除39：

```
(\.)( *。)
```

### 9.序号不一致（部分情况）

发现较多时候是序号B.链接到了上一句A选项的末尾，例如：

ALeft bundle branch block with normal sinus rhythmB（序号）

Idioventricular tachycardia

C.Right bundle branch block

D.Third-degree atrioventricular block (complete heart block)

增加换行2：

```
(?:\n)(A)\.?(.*)(B)\n+(.*)(\n+C\..*)(\n+D\..*)
```

### 10.删除重复语句

重复标题，在全量里出现几次，例如：

Key Points

Key Points

增加删除：

```
(?:\n)([*_]*Key Points[*_]*)(\n+[*_]*Key Points[*_]*)
```

删除个例重复语句

```
(?:\n)([*_]*Ms. Rose is a 36 year-old attractive Caucasian woman.*[*_]*)(\n+[*_]*Ms. Rose is a 36 year-old attractive Caucasian woman.*[*_]*)
```

### 11.空标题的删除

例如：

• Autoimmune haemolytic anaemia is a known complication of CLL, caused by auto￾antibody production by diseased lymphocytes against red blood cells.（从这开始是无关文本）Case 62: Worsening fatigue and bleeding gums

（后面没有其他内容了，为空标题，但是缺少换行）

增加删除：

```
((?:Case *\d+[:：].*\n*))(?:$)
```