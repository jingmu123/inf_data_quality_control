## reclean1_mimic_iv_radiology

1.无关索引

例如：

(series 3a,  im 7)
(series 3 image 79)
(e.g. Series 2, Image 15)

增加删除1：

```
[r'(\([^\n()]*(?:[Ss]eries?|[Ii]mages?) *\d+[^\n()]*\))',r'删除1：<u>\1</u>'],
```

2.参考内容删除

例如：

Please refer to CT thoracic and lumbar spine myelogram following
（多余换行）intrathecal injection for further details.

可能会出现多余换行，所以这条正则放在处理多余换行后，增加删除4：

```
[r'(?:\n|^)(\d*\.? *Please refer to.*?)(?:\n)',r'\n删除4：<u>\1</u>\n']
```

3.空填空位置的删除

例如：

CLINICAL HISTORY:  ___ man with HIV/HCV infection.  Evaluate for HCC.

___.（这个是空选项）

增加删除2：

```
[r'(\.\n+)(_{1,3}\.)',r'\1删除2：<u>\2</u>'],
```

4.单独字母的删除

例如：

normal.  Dr. ___ was e-mailed regarding the findings.
gb（无关字母）

增加删除3：

```
[r'(?:\n|^)( ?[A-Za-z0-9](?: ?[A-Za-z0-9]){0,1} *)(?:\n|$)',r'删除3：<u>\1</u>'],
```

5.多余换行

5.1 大多数情况例如：

Transvaginal imaging was performed to better evaluate the
（多余换行）uterus and the adnexa.

增加删除换行1：

```
[r'([a-z，,0-9’;()/] *(?:>|<|\+|\–|%|\'|≥|=|≤|-)* *)(\n+)( *(?:>|<|\+|:|%|\'|≥|=|≤|-)* *([“_,，./a-z‘)][^.]|\d+[^.][^.\\])|\(.{3,}\))',r'\1 删除换行1 \3'],
```

5.2 括号内容出现多余换行，例如：

There is a trace amount of fluid within the tract (less than
（多余换行）1 cc).

增加删除换行2：

```
[r'(?:\n|^)(.*\([^\n()]*)(\n+)([^\n()]*\).*)',r'\1 删除换行2 \3'],
```

5.3 特殊格式位置多余换行

例如：

There is mild increase of the pelvic lymphadenopathy, e.g.（多余换行，e.g.不是结尾）
an internal iliac lymph node (series 3, image 102) which currently measures 21

增加删除换行3:

```
[r'((?:i\.e\. *)|(?:e\.g\. *))(\n+)( *(?:>|<|\+)* *[./a-zA-Z0-9‘()])',r'\1 删除换行3 \3'],
```

例如：

liver or spleen enlargement,
（多余换行）i.e. lymphoma, lymphoproliferative disorder, or POEMS syndrome.

增加删除换行3:

```
[r'((?:>|<|\+)* *[./a-zA-Z0-9‘(),] *)(\n+)( *(?:i\.e\. *)|(?:e\.g\. *))',r'\1 删除换行3 \3'],
```

5.4大小写字母之间多余换行

例如：

most marked at
（多余换行）C6- C7, where there is

增加删除换行4：

```
[r'(?:\n|^)((?:[^#\n•●©>·:： ]{1,} +){10,}[^\n ]*[a-z，,0-9’;(/] *)(\n+)( *[A-Z][^. ] *(?:[^#\n•●©>·:： ]{1,} +){10,}[^\n :：]*)',r'\1 删除换行4 \3'],
```

例如：

Two views of the pelvis demonstrate no widening of the pubic symphysis or SI
（多余换行）joints. 

增加删除换行4：

```
[r'(?:\n|^)((?:[^#\n•●©>·:： ]{1,} +){10,}[^\n ]*[A-Z] *)(\n+)( *[a-z，,0-9’;)/][^. ] *(?:[^#\n•●©>·:： ]{1,} +){10,}[^\n :：]*)',r'\1 删除换行4 \3'],
```

5.5逗号位置多余换行

例如：

Acquisition 0.9 s,
（多余换行）0.2 cm; 

增加删除换行5：

```
[r'([,，] *)(\n+)( *[^#\n•●©>·:：|])',r'\1 删除换行5 \3'],
```

5.6算式中出现多余换行

例如：

Sequenced Acquisition 16.0 s, 17.0 cm; CTDIvol = 47.1 mGy (Head) DLP =
（多余换行）802.7 mGy-cm.

增加删除换行6：

```
[r'(\n|^)(.*(?:>|<|\+|\–|%|\'|≥|=|≤|-) *)(\n+)( *[0-9].*)',r'\1\2 删除换行6 \4'],
```

例如：

Length proximal graft to lowest renal artery:  1.7 +/- 0.1 cm; compared to 07
（多余换行）+/-0.1 cm.

增加删除换行6：

```
[r'(?:\n|^)(.*[0-9] *)(\n+)( {0,3}(?:>|<|\+|\–|%|\'|≥|=|≤).*)',r'\1 删除换行6 \3'],
```

5.7个例填空位置多余换行

例如：

OPERATORS:  Drs. ___ and ___, attending.  Dr.
（多余换行）___ was supervising the procedure.

```
[r'(.*Dr\.)(\n+)(_{3}[^\.])',r'\1 删除换行7 \3'],
```