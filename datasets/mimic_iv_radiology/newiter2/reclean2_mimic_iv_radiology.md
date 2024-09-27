## reclean2_mimic_iv_radiology

### 1.多余换行补充（小写字母结尾，大写字母开头）

例1如：

Contiguous axial images of the head were performed without administration of
IV contrast.（比较短）

之前有限制匹配第二段文本的长度，现在去掉长度限制，只要下一段文本的结尾是正常的结尾标点符号就会去删除换行。

例2如：

INDICATION:  NO_PO contrast; History: ___ with sharp right flank painNO_Po

Contrast  // Evaluate for nephrolithiasis

比较特殊的下一段文本没有标点符号结尾，但是有一段类似注释的文本，出现类似注释的文本的特征时也会删除换行

### 2.多余换行补充（大写字母结尾，小写字母开头）

例1如：

TECHNIQUE:  Contiguous axial images of the head were obtained without  IV

contrast.（比较短）

例2如：

INDICATION:  ___ year old woman with postmenopausal bleeding Is S/P by HX
hysterectomy ?SCH no cervix appreciated on exam for fibroids/HX hydrosalpinx  删除换行1 // cause of postmenopausal bleeding

同样做出以上改动

### 3.填空位置多余换行

例如：

COMPARISON:  Multiple prior chest radiographs, most recent from ___ (多余换行)
at 13:34.

COMPARISONS:  Multiple prior head NECTs, most recently of 
(多余换行)___at 13:53 p.m.

根据填空多余换行的位置增加两条删除换行8：

```
[r'(_{3})(\n+)([^#\n•●©>·:：]+(?:\d[:：]\d)*[^#\n•●©>·:：]*\n)',r'\1 删除换行8 \3'],
[r'([^#\n•●©>·:：]*)(\n+)(_{3}.*)',r'\1 删除换行8 \3'],
```

### 4.数字运算处的多余换行

例如：

Intraparenchymal hemorrhage centered at the right caudate head measures 2.6 x（多余换行）
2.5 cm, not appreciably changed since the prior exam, allowing for difference

前面的正则会避免匹配到序号，所以这类就被错过了，补充到删除换行6：

```
[r'(\n|^)(.*(?:>|<|\+|\–|%|\'|≥|=|≤|-| x) *)(\n+)( *[0-9].*)',r'\1\2 删除换行6 \4'],
[r'(?:\n|^)(.*[0-9] *)(\n+)( {0,3}(?:>|<|\+|\–|%|\'|≥|=|≤| x).*)',r'\1 删除换行6 \3'],
```

例如：

The second largest fibroid is located to the left and measures
3.3 x 2.8 x 3.0 cm, previously measuring 3.3 x 2.2 x 3.0 cm. The endometrium 

前面的正则会避免匹配到序号，所以这类就被错过了，增加删除换行9：

```
[r'(.*)(\n+)(\d+\.\d+ x.*)',r'\1 删除换行9 \3'],
```

### 5.时间处多余换行

例如：

Findings were discussed with Dr. ___ on ___ at 5:23

a.m.

前面的正则会避免匹配到序号，所以这类就被错过了，增加删除换行10：

```
[r'(\d+[:：]\d+)(\n+)((?:p\.m|a\.m).*)',r'\1 删除换行10 \3'],
```

### 6.大写标题多余换行

例如：

EXAMINATION:  LEFT DIGITAL 2D DIAGNOSTIC MAMMOGRAM INTERPRETED WITH CAD AND

LEFT BREAST ULTRASOUND.

整句话都是大写的，第二换文本不能出现冒号，避免两个标题连接

增加删除换行11：

```
[r'(?:\n|^)([^\na-z]+[^\na-z:：])(\n+)([^\na-z:：]+)(?:\n|$)',r'\1 删除换行11 \3'],
```