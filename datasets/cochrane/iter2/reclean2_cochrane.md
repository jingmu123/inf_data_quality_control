## 1.reclean2_cochrane

### 1.1 此次清洗分析

初次清洗合格率=84.333%，质量分=93.30143。
各纬度问题频次F={'无关文本': 36, '无关链接': 4, '错误删除': 31, '页码/数字': 5, '语义不完整': 1, '多余标点': 1}
出现一类错误删除较多，可以解决。新出现的无关文本可以解决90%，无关链接以及页码数字可以解决100%

### 1.2 误删

误删出现在删除人名+年份类的无关文本，因为这类无关文本有时候出现格式比较不一样，所以一开始写的正则太过泛化。导致一些误删，例如：
(< 1500 g)
(3133 randomised patients)
(five studies, 1186 women)
(RR 1.16, 95% CI 1.09 to 1.23; 17 studies, N = 5247; I² = 40%; moderate‐quality evidence)
对这几类误删修改，
现在括号内开头不能为数字，并且必须有两个以上的字符（人名）。
括号内不能出现%和=。
在年份结尾处非空格字符最多出现两位。有时会出现这类（人名 2007-a）无关文本
补充括号内容，例如：\[ Lissauer 2002 \].
修改删除1

```
(\\?[(（[][^\d\n][^()（）\[\]\n%=]+\d{4}[^()（）\[\]\n%= ]{0,2} *\\?[)）\]])
```

2.3 无关链接补充
例如：
\[www.ceida.net.au\]
[www.adf.org.au]
[www. state.vt.su/adap/cork]
补充到删除8：

```
(\\?[(（【[][^（）()[\]\n]*(?:https?:\/\/(?:www\.)?|www\.)[ a-zA-Z0-9-]+(?:\.[a-zA-Z]{2,})+(?:\/[^ \n\u4e00-\u9fa5]*)?[^（）()[\]\n]*[)）】\]])
```

对在文中出现的无关链接增加删除，例如：
We also conducted searches of EMBASE (November 2007), LILACS and （这里）www.ClinicalTrials.gov (05 January 2010).
增加删除：

```
[^()（）【】\[\]] ((?:https?:\/\/(?:www\.)?|www\.)[ a-zA-Z0-9-]+(?:\.[a-zA-Z]{2,})+(?:\/[^ \n\u4e00-\u9fa5]*)?)
```

### 2.4 页码/数字的补充

例如：VAD. \[ 11 \] 
因为多余空格导致没有被正则匹配到，并且发现有时候会有\，补充到删除3
2.5 版权声明类的删除
例如：
Acute atopic eczema in a child. Copyright © 1991 Professor Hywel Williams: reproduced with permission
A house dust mite. Copyright © 2013 Professor Thomas Platts‐Millls: reproduced with permission
增加删除13：

```
(?:\n|^)(.*Copyright.{0,5} \d{4} .*)
```

### 2.6更新声明的删除

例如：
This search was updated in March 2010
This is an update of a Cochrane Review published in 2013.
增加删除14：

```
(?:\n|^)(\** *This.*updated?.* \d{4}\.?)(?=\n)
```

### 2.7摘自内容的删除

例如：From Osterloh 1986 ; Vamnes 2000 ; Drugs.com 2012 .

```
增加删除15：(?:\n|^)(From *(?: [^\n ]* \d{4} *[;.])+)*
```

### 2.8 询问内容是否最新的删除

出现几条没有被之前写的正则匹配到
例如：
**How up‐to‐date is this evidence?**
The evidence is current to 20 April 2022.
现在对回答的正则匹配改为，如果回答的结尾是这类的日期格式，配合之前问题的匹配，就会删除。修改删除11：

```
(?:\n)((?:(?:\**How up[‐ ]to[‐ ]date (?:was|is).*)|(?:\**Search date\** *))(?:\n*.*to \d{1,2}.*\d{4}.*))
```