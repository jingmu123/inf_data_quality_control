## 1.无关文本

### 1.1 人物+年份类的无关文本

例如：( Li 2001b )
( Dalusung‐Angosta 2011 ; Lee 2007 )
(Issue 5, 2013) (Ovid, 1950 to 11 June 2013)
增加删除1：

```
([(（][^()（）\n]*\d{4}[^()（）\n]*[)）])
```

### 1.2 鉴定研究的检索方法|电子检索 类的无关文本

当出现这类的标题时，以下的内容都是无关文本，会全部删除，增加删除2：

```
(?<=\n)([# ]+(?:Search methods for identification of studies|Electronic searches) *(?:.*\n?.*)*)
```

### 1.3 退刊原因 类的无关文本

例如：

Reason for withdrawal from publication

Editorial note 7 March 2017: The protocol was published in 2009 but the review was never submitted.
Withdrawn from publication for reasons stated in the review

Visual summary

Close
这类标题出现时，整页内容都是无关文本，直接整页删除
增加删除：

```
(\n*(?:Reason for withdrawal from publication) *(?:.*\n?.*)*)
```

### 1.4 文中无用序号的删除

例如：###### Intervention (2)

增加删除

### 1.5 一些特定无关文本（单行出现）

例如：
Visual summary
See more on using PICO in the Cochrane Handbook .
Unlock the full review
出现频率较高，可以单独删除，增加删除4：

```
(?:\n|^)((?:Visual summary|See more on using PICO in the Cochrane Handbook .|Unlock the full review) *)(?=\n|$)
```

### 1.6 语言总结类的无关文本

例如：

Plain language summary（这句话可能不会出现）

available in
* English

* Español

* فارسی

* Français

* 繁體中文
  增加删除5：

  ```
  (?:\n)((?:Plain language summary *\n)?-+\n*available in *\n*(?:\*.*\n)+)
  ```

  

### 1.7 重复出现的标题

例如：
PICOs

PICOs

现在把多余的第一个标题删除，增加删除6：

```
(?:\n)(PICOs\n-+\n*)#+ *PICOs
```

### 1.8 （英文附录或图表类的无关文本）的删除

例如：( Appendix 1 )( Figure 1 )(Table 1 )
(see Appendix 2 ).(see Module).
增加删除7：

```
([(（] *(?:Appendix|Figure|Table|[Ss]ee[^\n()（）]*)[ 0-9]*[）)])
```

### 1.9无关链接

例如：( http://www.who.int/ictrp/en/ )
增加删除8：

```
(\([^（）()\n]*(?:https?:\/\/)?(?:www\.)?[a-zA-Z0-9-]+(?:\.[a-zA-Z]{2,})+(?:\/[^ \n\u4e00-\u9fa5]*)?[^（）()\n]*\))
```

### 2.0图表索引类

例如：
Figure 1

* * *
* * *
(see summary of findings Table for the main comparison ).
 (see Module)
对括号内出现关键字（图表附录）的括号文本删除
对单独一行出现关键字的文本删除
对括号内出现“见”字样的的括号文本删除
增加到删除7：

```
([(（\n] *(?:Appendix|Figure|Table|(?:\* ?)+)[ 0-9.]*[\n）)])|([(（] *(?:[Ss]ee[^\n()（）]*)[ 0-9.]*[）)])
```



### 2.1 文中穿插的见图表类

例如：
 See Appendix 1 for details of the search strategy used to search CENTRAL. （前面这句是无关文本）The Specialised Register is maintained by the TSC and is constructed from weekly electronic searches of MEDLINE, 
增加删除9：

```
(?:\n|\.)([^.\n()（）]{0,10}[Ss]ee [^\n()（）]*(?:[Aa]ppendix|[Ff]igure|[Tt]able|module).*?\.(?: |\n))
```

### 2.2综述证据类的删除

例如：
The evidence in this review, carried out by authors from Cochrane Oral Health, is up to date as of 12 November 2018.
增加删除10：

```
(?<=\n)(The evidence in this review,.*carried out.*is up[‐ ]to[‐ ]date.*\d{4}\.)
```

### 2.3关于综述时间类的删除

例如：

**How up to date is this review?**
We searched for studies that were available up to June 2020.*

*Search date**
We searched for studies in December 2015.
增加删除11：

```
((?:(?:\**How up[‐ ]to[‐ ]date (?:was|is).*)|(?:\**Search date\** *))(?:\n*We searched for studies.*\d{4}.*))
```

### 2.4信息类的删除

例如：

Information

DOI:https://doi.org/10.1002/14651858.ED000058 Copy DOI （以下内容都为无关文本，一直到结束）
增加删除12：

```
(?:\n)(\**Information\** *\n*-+(.*\n*.*)*)

```

