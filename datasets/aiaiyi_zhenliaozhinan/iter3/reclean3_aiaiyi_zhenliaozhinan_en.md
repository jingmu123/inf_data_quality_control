## reclean3_aiaiyi_zhenliaozhinan_en
### 标点错误：
1.英文中带有中文标点【，。；】，将之转换为英文标点【,.;】。

```[r'。', r'\.'], [r'，', r','], [r'；', r';']```

### 页码/数字:
1.句中(7,8)、(3,4,5,6)等。

正则删除：```[r'([A-Za-z\)）] ?)([\(\[（](\d+(([\s，,\-––]+\d+){0,20}))[\)\]）])', r'\1删除13:<u>\2</u>']```。


### 无关文本：
1.人物简介、成员组成等。

正则删除：```[r'((Professor Alan|We are grateful to)[\w\W]+?(\n *\n))', r'删除14:<u>\1</u>']```。

2.(Box 1)、(Box 1 and Box 2)等。

正则补充：```[r'([\(（]([fF]ig|NCT|Grade|[pP]icture|FIGURE|PICTURE|[iI]mage|[tT]able|[Ss]ee|[Rr]efer|Appendix|NICE|[Bb]ox) *([^\(\)（）]*[\)）]))', r'删除5:<u>\1</u>']```。


**0819补充：**
### 页码/数字:
1.句中(7,8)、(3,4,5,6)等补充排除前面是and的情况。

正则补充：```[r'([A-Za-z\d）\)](?<! and) ?)([\(\[（](\d+(([\s，,\-––]+\d+){0,20}))[\)\]）])', r'\1删除13:<u>\2</u>']```。

### 多余换行：
1.多余换行造成的无关文本一并解决。

正则替换：
```[r'([a-z\)）])(\s{3,}([(（]\d+[)）]|(\\?\[[\d\s\-,～~，;；–—\\]{0,100}\]))?)( ?[a-z])', r'\1 删除1换行\5']```,
```[r'([a-z\)）])(\s{3,}([(（]\d+[)）]|(\\?\[[\d\s\-,～~，;；–—\\]{0,100}\]))?)( ?[,，;；.。])', r'\1删除2换行\5']```,
```[r'([a-z\)）])(\-\s{3,}([(（]\d+[)）]|(\\?\[[\d\s\-,～~，;；–—\\]{0,100}\]))?)( ?[a-z])', r'\1删除3换行\5']```。


### 无关文本：
1.无关特殊文本补充。

```[r'((Professor Alan|We are grateful to|The development of this framework|Douglas P\.|A\. John Camm|To help you)[\w\W]+?(\n[  ]*\n))', r'删除14:<u>\1</u>']```,
```[r'((ó 2011 European|Perth:|Date written:|Final submission:|Author:|Stack A|For more detailed|Footnote:|See the NICE|Entries to MEDLINE|From the National|CREST wishes|Dr Mark Gibson|Experts of the guideline|Copies of the full-text)[^\n]+)', r'删除15:<u>\1</u>']```,
```[r'((\\\*Refer to)[\w\W]*)', r'删除16:<u>\1</u>']```。

特殊文本包含[Aa]ppendix|in [Tt]able|on pages?的，删除后标点替换，为避免需要连续删除的时候会遗漏后面那个，就不加标签了。
```[r'([,\.][^\n\.,。？\?\(\)（）]+([Aa]ppendix|in [Tt]able|on pages?)[^\n\.,。？\?\(\)（）]+?[\.,])', r'.']```。

2.括号内无关本文补充。

```[r'([\(（]([fF]ig|NCT|Grade|[pP]icture|FIGURE|PICTURE|[iI]mage|[tT]able|[Ss]ee|[Rr]efer|[Aa]ppendix|NICE|[Bb]ox|Kannel|Bordley|Giorgi2004) *([^\(\)（）]*[\)）]))', r'删除5:<u>\1</u>']```, 

3.\[D\]、[A]等。

补充正则：```[r'(\\?\[[\w\s\-,～~，;；–—\\]{0,100}\])', r'删除7:<u>\1</u>']```。

4.Stein et al. （4）、Stein et al. （6）等。

正则删除：```r'(et al\. )([\(（]\d+[\)）] *)', r'\1删除16:<u>\2</u>']```。

5.补充句首小写字母的无关数字，部分情况会误删，取几个不会误删的小写字母。

正则补充：```[r'([^\d][,，;；.。] *)(\d+(([\s，,\-–]+\d+){0,20}) *)([A-Zabeih])', r'\1删除6:<u>\2</u>\5']```。
