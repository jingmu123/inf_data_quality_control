## reclean2_paper-medjournals_zh

### 1.错误删除

删除2：(n = 5503, 32.8%)
错误把5503识别成年份，增加不能出现的关键符号=%
修改到删除2：

```
[r'([(（]\D[^\n()（）=]*[^0-9=\.\-\-：:]\d{4}[:：;；,，年][^\n()（）%]*[）)])',r'删除2：<u>\1</u>'],
```

### 2.杂志刊号类

例如：
percutaneous transluminal angioplasty. （后面是无关文本）Chin Med J 2001; 114(2): 139-142
增加删除8：

```
[r'(\.)( *Chin Med J \d{4}; *\d+\(\d+\): *\d+-\d+)',r'\1删除8：<u>\2</u>'],
```

### 3.固定句式开头的文本文本

例如：
Peer review under responsibility of...
The datasets supporting the conclusions...
This paper is a review article...
All data generated or analyzed....
这类文本非常多，并没有一类固定的特征，话术不一样。但是开头都是固定句式，检查全量后发现都是介绍类的无关文本，全部增加到删除7，后续有发现再补充

### 4.补充类

例如：
Supplementary data related to this article can be found at https://doi.org/10.1016/j.cjtee.2017.08.006.
Supplementary information
增加删除9：

```
[r'(\n|^)(Supplementary (?:data|information).*)',r'\1删除9：<u>\2</u>'],
```

5.无关链接类

例1如：

The primer sequences are listed in Supplementary Table 1, http://links.lww.com/CM9/A95. 

and SMIS are shown in Supplementary Figure 1, http://links.lww.com/CM9/A585.

出现在文中句子末尾，增加删除10：

```
[r'(,)( *(?:https?[：:][/／]{2}(?:www[.．])?|www[.．])[a-zA-Z0-9@／/-]+(?:[.．／/][a-zA-Z0-9@／/_]{2,})+)(\.)',r'删除10：<u>\1\2</u>\3'],
```

例2如：

http://dx.doi.org/10.1016/j.cjtee.2015.12.0081008-1275

正则缺少符号-，补充到删除6：

```
[r'(\n|\(|（)((?:https?[：:][/／]{2}(?:www[.．])?|www[.．])[a-zA-Z0-9@／/-]+(?:[-.．／/][a-zA-Z0-9@／/_]{2,})+)(\n|$|\)|）)',r'删除6：<u>\1\2\3</u>'],
```

6.语句重复

例如：

EGCG: Epigallocatechin-3-gallate; miRNAs: microRNAs.（重复）
Expression levels of miRNAs exhibiting >2-fold changes in response to both concentrations of EGCG
删除重复语句：<u>Expression levels of miRNAs exhibiting >2-fold changes in response to both concentrations of EGCG</u>
EGCG: Epigallocatechin-3-gallate; miRNAs: microRNAs.（重复）

重复的句子距离比较远，错过了之前的删除检查，现在在分段部分增加一层检查

```
if item in final_results:
    final_results.append(f'删除重复语句2：<u>{item}</u>')
else:
    final_results.append(item)
```

7.通用错误删除修改

例如：

通用删除1(英):<u>(OR = 1.889; 95% confidence interval = 1.166–7.490; P = 0.024; Table 2)</u>

（OR = 1.889; 95% confidence interval = 1.166–7.490; P = 0.024; 是有用信息）

通用删除8(英):<u>[P < 0.05, Table 2]</u>  （P < 0.05是有用信息）

通用删除8(英):<u>[P = 0.414, Tables 5 and Tables 6]</u>. （P = 0.414,是有用信息）

在通用删除1和删除8前面增加几条提前删除后半部分无关文本：

```
[r'((\([^\(\)]*)([,;] ([Ff]igs?(?:ure)?|F\s?IGS?(?:URE)?|Table|[sS]ee\s|For more|http|www|NCT\d+|N[oO]\.|Participant \d+|Provider \d+|software|version)s?[\s\.:][^\(\)]*\)))',r'\2)删除11：<u>\3</u>'],
```

```
[r'(((?:\\)?\[\s?[^\[\]]*)([,;] ([Ff]igs?(?:ure)?|F\s?IGS?(?:URE)?|Tables \d and|[sS]ee|For more|panel|http|www|NCT\d+|NO\.|version)s?[^\[\]]*(?:\\)?\]))',r'\2]删除11：<u>\3</u>'],
[r'(((?:\\)?\[\s?[^\[\]]*)([,;] ([Ff]igs?(?:ure)?|F\s?IGS?(?:URE)?|Table|[sS]ee|For more|panel|http|www|NCT\d+|NO\.|version)s?[^\[\]]*(?:\\)?\]))',r'\2]删除11：<u>\3</u>'],
```