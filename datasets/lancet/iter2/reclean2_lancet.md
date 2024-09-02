## reclean1_lancet问题
### 错误删除：
1.括号内有用内容误删，(trend p=0·86; figure 1 )、(around 0·2 events per 1000 patient-years in placebo groups; appendix p 21 )等。

将原：```[r'([\(（][^\(\)（）\n]*([Ss]ee|[Ff]ig|[Tt]able|[Aa]ppendix|[Nn]o\.|pp? \d+|panel|[Ss]upplementary|[Ll]ink)[^\(\)（）\n]*[\)）])', r'删除2:<u>\1</u>']```,
更改为：```[r'([\(（][  \t]*([Ss]ee|[Ff]ig|[Tt]able|[Aa]ppendix|[Nn]o\.|pp? \d+|panel|[Ss]upplementary|[Ll]ink)[^\(\)（）\n]*[\)）])', r'删除2:<u>\1</u>']```,
```[r'([\(（][^\(\)（）\n]*?)(([,;] *([Ff]ig|[Tt]able|[Aa]ppendix|[Nn]o\.|pp? \d+|panel|[Ss]upplementary|[Ll]ink)[^\(\)（）\n,;]*)+)([^\(\)（）\n]*[\)）])', r'\1删除2-1:<u>\2</u>\5']```,
为了防止漏删，删除2-1在去标签时复制一条运行两次。

### 无关文本：
1.加删除标签导致一些删除的情况匹配不上，漏删。

将```[r'(\n[  \t\*\.\w#]*([Ff]unding)[\w ]*\n[\w\W]*?\n)([^\n]+\n(\-{7,})|To read this article in full)', r'删除5:<u>\1</u>\3']```,后面的删除标签上加\n： r'删除5:<u>\1</u>\n\3'。

2.补充Conflict of interest statement、Author statement、Declaration of Interests以下无关段落。
```
[r'(\n[  \t\*#]*(This article is available free|To read this article in full|Authors?’? [Cc]ontributions?|Contributors|Article info|Appendix|The following are the supplementary|GBD 2016 Neurology Collaborators|Supplementary Material|Conflict of interest statement|Author statement|Declaration of Interests)[\w\W]*)', r'以下都删除1:<u>\1</u>'],
```

3.Funding结尾标记补充，This article is available free 前。
```
[r'(\n[  \t\*\.\w#]*([Ff]unding)[\w ]*\n[\w\W]*?\n)([^\n]+\n(\-{7,})|To read this article in full|This article is available free)', r'删除5:<u>\1</u>\n\3'],
```

4.补充文章开头*   View Large Image等情况。
```
[r'(^[  \t\*]*(This online publication|Copyright|View|Fig(ure)?|Download|Show full caption|Open table)[^\n]*)', r'删除4-1:<u>\1</u>'],
```

5.开头为Sir\n\n。
```
[r'(^[  \t\*]*Sir\n\n)', r'删除10:<u>\1</u>'],
```

6.无关页面文章。"title": "Department of Error"页面删除。
```
title = item["title"]
if title == "Department of Error":
    context = "(本页删除)本页文本质量太差:\n" + context
    # return None 
```

7.句末see Fig. 1。
```
[r'([,;] see Fig\.[^\.]+)', r'删除11:<u>\1</u>'],
```

8.补充括号内无关内容，( Arch Neurol 2000; 57 : 1461–63)。
```
[r'([\(（][^\(\)（）\n]*(\d+;[ \d\*]{2,}:[ –\-\d\*]{2,})[^\(\)（）\n]*[\)）])', r'删除12:<u>\1</u>'],
```

9.无关网址补充ClinicalTrials.gov形式。
```
elif re.findall(r'(\.gov)', web[0]):
    context = re.sub(r'([^\n\.]*' + re.escape(web[0]) + r'[^\n\.]*\.?)', r'删除1-2:<u>\1</u>', context)
```

10.补充无关句子，Please submit your paper等。
```
[r'((This trial is registered|Please submit your paper|Bill Hayes\. Random House|EA has received fellowship funding)[^\n]*)', r'删除8:<u>\1</u>'],
```