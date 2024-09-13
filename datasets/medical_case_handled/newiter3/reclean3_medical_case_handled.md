## medical_case_handled的清洗

### 1.改编类的删除（补充）

增加了在括号内出现的改变类的删除

补充到删除21

```
 [r'(?:\n|^|\()( *(?:Reproduced，?|Adapted) (?:with permission|from).*)(?:\n|\))',r'删除21：<u>\1</u>']
```

### 2.特例句子的删除（补充）

例如：
followed by lymphangiography.（这后面是无关文本）SWOLLEN LEG 189

### 3.多余标点的删除

例如：
A.\]_ Increase the dose of alprazolam（\]是多余标点）
增加删除28：(?:\n)(\** *_*[A-Z]\.)(\\\])

### 4.增加删除换行

例如：
inferior epigastric vessels i.e. （i.e.并不是结尾，这类属于比较特殊的多余换行）
upwards and inwards with a grooved director.
例如：
In Fig. （这里多余换行，并不是句号，是图片格式）
8.9 the lateral view of the duct shows how it curves posterior to the 
增加换行删除：((?:i\.e\. *)|F[iI][gG][sS]?(?:ures?|URES?)?\. *)(\n+)( *(?:>|<|\+)* *[./a-zA-Z0-9‘()])

### 5.括号内容发生多余换行

例如：
...genetically susceptible (although only about 10 per (这里多余换行，括号的内容被拆开，有时会因为结尾字符不符合删除换行常理被漏掉，现在单独出一条正则)
cent have a family history at presentation). There...
增加删除换行：(?<=\n)(.*\([^\n()]*)(\n+)([^\n()]*\).*)

### 6.修改图片索引删除

之前因为多个图片索引挤在一起导致漏删除了一些图片描述。现在调整正则：
(?<=\n)(\**F[iI][gG][sS]?(?:ures?|URES?|\.) ?[0-9A-Z]+([.-]\d+)*[:：.]?(?:\n+(?:[^\n ]{1,} ){4,}.*[^\n.?!](?=\n)|.*))

### 7.推荐阅读类的补充

由于标题个别字符大小写问题导致没有匹配到，以及空格的位置导致的没有匹配到。
调整正则：
(?:\n|^)(#* *(?:Recommended Reading|Bibllography|REFERENCES?|Further [Rr]eading|(?:CLINICAL)? *CASE CORRELATION|Suggested Reading|Disclosure Statement)\n*(?:.*\n*)*)(?:\n|$)

### 8.无用标题的删除

例如：
Case 15: A thirsty boy（后面没有任何内容）
Duties of a Doctor（后面没有任何内容）
Rheumatology（后面没有任何内容）
ORTHOPAEDIC（后面没有任何内容）
增加删除29：
(?<=\n)((?:Case *\d+[:：].*\n*)|Duties of a Doctor *\n*| *Rheumatology *\n*|ORTHOPAEDIC\n*)(?:$)