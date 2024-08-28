## reclean1_cdc问题
### 多余标点：
1., , ,由 <sup>, </sup> <sup>, </sup> <sup>, </sup>造成。

```[r'(<[\/\w]+>,? ?)+', ''],```

### 无关文本：
1.无关网址句子和段落。
```
def step1_del_wuguan(self, context):
    count = 0
    patter2 = r'([\(（][^\(\)（）\n]*(https?:\/\/)?(www\.|[Ee]?-?mail:)?([\da-z \.\-@]+)\.([a-z]{2,6})([\/\\\w\?=\.-]+)?\/?[^\(\)（）\n]*[\)）]|\s*(https?:\/\/)?(www\.|[Ee]?-?mail:)?([\da-z \.\-@]+)\.([a-z]{2,6})([\/\\\w\?=\.-]+)?\/?)'
    website_list = re.findall(patter2, context)
    for web in website_list:
        if len(re.findall(r'(\.|:|\/\/)', web[0])) >= 2:
            count += 1
            if re.findall(r'([\(\)（）])', web[0]):
                context = re.sub(re.escape(web[0]), rf'删除1:<u>{web[0]}</u>', context)
            else:
                context = re.sub(r'([^\n\.]*' + re.escape(web[0]) + r'[^\n\.]*\.?)', r'删除1-1:<u>\1</u>', context)
    if count >= 3:
        context = "(此段删除)无关文本-1:" + context
        # context = ""
    return context
```

2.( figure 1 )、( appendix )、( panel )、( table 4 )、(Oct 14, p 1324)、(pp 13–15 )
```
[r'([\(（][^\(\)（）\n]*([Ss]ee|[Ff]ig|[Tt]able|[Aa]ppendix|[Nn]o\.|pp? \d+|panel)[^\(\)（）\n]*[\)）])', r'删除2:<u>\1</u>'],
```

3.Author contributions、Contributors、Article info、Appendix.
```
[r'(\n[  \t\*]*(Author contributions|Contributors|Article info|Appendix|The following are the supplementary)[\w\W]*)',r'以下都删除1:<u>\1</u>'],
```

4.\[ \]、\[ 2\]等。
```
[r'(\\?\[[\d\-,～~;–—、\s\\_]+\])', r'删除3:<u>\1</u>'],
```

5.*   View Large Image、*   Figure Viewe、*   Download Hi-res image等。
```
[r'(\n[  \t\*]*(View|Figure|Download|Show full caption|Open table)[^\n]*)', r'删除4:<u>\1</u>'],
```

**0828补充：**
1.Funding相关的段落，补充 2.5 Role of the funding source、到To read this article in full
```
[r'(\n[  \t\*\.\w#]*([Ff]unding)[\w ]*\n[\w\W]*?\n)([^\n]+\n(\-{7,})|To read this article in full)', r'删除5:<u>\1</u>\3'],
```

2.无关段落补充，We declare....、Copyright、This online publication
```
[r'(\n[  \t\*]*(This online publication|Copyright|View|Figure|Download|Show full caption|Open table)[^\n]*)', r'删除4:<u>\1</u>'],
```

3.无关批量段落补充，Supplementary Material、Authors’ contributions、To read this article in full、This article is available free、
```
[r'(\n[  \t\*]*(This article is available free|To read this article in full|Authors?’? contributions|Contributors|Article info|Appendix|The following are the supplementary|GBD 2016 Neurology Collaborators|Supplementary Material)[\w\W]*)', r'以下都删除1:<u>\1</u>'],
```

4.括号内无关内容补充，(Supplementary ...)、link、
```
[r'([\(（][^\(\)（）\n]*([Ss]ee|[Ff]ig|[Tt]able|[Aa]ppendix|[Nn]o\.|pp? \d+|panel|[Ss]upplementary|[Ll]ink)[^\(\)（）\n]*[\)）])', r'删除2:<u>\1</u>'],
```

5.\[see ( , ) for recent reviews\]、\[e.g., ( )\]等。
```
[r'(\\?\[(see|e\.g\.)[^\[\]]+\])', r'删除6:<u>\1</u>'],
```

6.( , )、( )、( , , )等。
```
[r'([\(（][ ,]*[\)）])', r'删除7:<u>\1</u>'],
```

7.This trial is registered with ClinicalTrials.gov , number NCT02302066.
```
[r'(This trial is registered[^\n]*)', r'删除8:<u>\1</u>'],
```

8.无关声明段落单独删除，TK declares no 、We declare no、All the other authors declare no等。
```
[r'([^\n]*(declare[\w ]*no|no[\w ]*declare)[^\n]*)', r'删除9:<u>\1</u>'],
```

