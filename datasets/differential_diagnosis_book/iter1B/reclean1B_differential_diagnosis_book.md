## iter1B是清洗reclean1剩余的问题
## reclean0B_differential_diagnosis_book剩余问题
### 多余换行：
1. 图例和图注内容多余换行，删除图例换行后没有标点结尾的图注段落。删除换行即可。Fig. 4.28(\n换行\n)Cord. Hyper。。。leg pattern（无标点结尾）、Fig. 4.27(\n换行\n)Serpiginous cord. Lar 。。。the dermis（无标点结尾）、Fig. 5.1(\n换行\n)Vesicles. Ac。。。towards weeping（无标点结尾）等。
```
context = re.sub(r'([\*_]*(?:[Ff]ig\.?s?(ure)?|FIG\.?S?(URE)?) ?\d+(?:.\d+)?)([ \*]*\n+\n[ \*]*)(.*[^\.\?？][ \*]*\n)', r'\1|删除2图换行|\5', context)
```

### 无关文本：
1. 人物介绍段落，(1)|删除序号换行|Hôpital Universitaire de Strasbourg, Strasbourg, France、(1)|删除序号换行|Harvard-MIT Division of Health Sciences and Technology, Harvard Medical School, Boston, MA, USA、(2)|删除序号换行|Department of Dermatology, Massachusetts General Hospital, Harvard Medical School, Boston, MA, USA等。
```
[r'(^(?=.{0,200}$)(?:\d+\.|\(\d+\)) ?.*[,，] ?[A-Za-z]{2,}[,，] ?[A-Za-z]{2,}$)', r'删除10:<u>\1</u>'],
```

2. 两个重复标题之间到Keywords之间的无关内容，人物介绍，Joi B. Carter , Amrita Goyal and Lyn McDivitt Duncan (eds.) Atlas of Cutaneous Lymphomas 10.1007/978-3-319-17217-0\_3、等。
```
context = re.sub(r'\n\n(# ?(\d+\. ?.*)[\w\W]*?\n\n)(\2[\w\W]*?\n\n)(Keywords)', r'\n\n|删除重复标题之间内容|\2\n\n\4', context)
```


