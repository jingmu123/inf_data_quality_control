## reclean1_paper-medjournals_zh

### 1.介绍类无关文本

例如：

原文：xxxxxxx

分类号：xxxxxxx

志谢：xxxxxxx

基金资助(Funding)：xxxxxxx

透明度（Transparency)：xxxxxxx

关于作者（Contributors)：xxxxxxx

来源与同行评议(Provenance and peer review)：xxxxxxx

特征类似，整理到一个正则里，增加删除1：

```
[r'(\n|^)(—*(?:原文|分类号|志谢|(?:基金)?资助[(（]Funding[）)]|透明度[(（]Transparency[）)]|关于作者[(（]Contributors[）)]|来源与同行评议[(（]Provenance and peer review[）)])[:：].+)',r'\1删除1：<u>\2</u>'],
```

### 2.引用类的删除

例如：

（中华眼科杂志，2018，54：258-262）

（nutrition risk screening 2002，NRS2002）

增加删除2：

```
[r'([(（]\D[^\n()（）]*[^0-9=\.\-\-]\d{4}[:：;；,，年][^\n()（）]*[）)])',r'删除2：<u>\1</u>'],
```

### 3.研究资助说明删除

例如：

This study was supported by grants from the Science and Technology Planning Project of Guangdong Province, China (No. 2013B021800323) and the Science and Popularization Planning Project of Haizhu District, Guangzhou, Guangdong, China (No. 2014HZKP-TJ-13).
There are no conflicts of interest.

增加删除3：

```
[r'(?:\n|^)((?:(?:This [a-z]{2,} (?:is|was) supported by.*\(No.*\).*)|Nil\.)(?:\n*There are no conflicts of interest\.))',r'\n删除3：<u>\1</u>'],
```

### 4.无关数字删除

例如：

.....of Sniffin’ Sticks, statistical significance was not achieved.42(无关数字)

增加删除4：

```
[r'([\.]\s*)(\d{1,3}[\s–,\d{1,3}]{0,20})($|\n)',r'\1删除4：<u>\2</u>\3'],
```

### 5.利益 冲突/竞争 说明类删除

例如：

利益竞争(Competing interests): None declared.
BMJ 2012; 345: e7634

利益冲突(Competing interests)：无申明。
参考文献w1～w5见网站bmj.com。
BMJ 2004；329：1300-1

增加删除：

```
[r'(?:\n|^)((?:利益(?:冲突|竞争)\(Competing interests\)[:：].*)(?:\n[^\n0-9][^\n.．].*)+)',r'\n删除5：<u>\1</u>'],
```

### 6.无关链接删除：

例如：

https://doi.org/10.1016/j.wjorl.2018.08.006

使用brainmap.org标准MNI template file（http://brainmap.org/ale/colin1.1_2X2X2.nii）脑解剖模板。

增加删除6：

```
[r'(\n|\(|（)((?:https?[：:][/／]{2}(?:www[.．])?|www[.．])[a-zA-Z0-9@／/-]+(?:[.．／/][a-zA-Z0-9@／/_]{2,})+)(\n|$|\)|）)',r'删除6：<u>\1\2\3</u>'],
```

### 7.个例删除

目前就一个个例，没有明显特征，固定句式出现不止一次就添加在这里删除

例如：

希望广大读者继续关注本刊，提出宝贵的意见和建议，积极提供文稿，本刊将择优刊登于相应栏目。

增加删除个例：

```
[r'(?:\n)(希望广大读者继续关注本刊，提出宝贵的意见和建议，积极提供文稿，本刊将择优刊登于相应栏目。)',r'删除个例：<u>\1</u>']
```

### 8.删除重复语句

例如：

晚孕期孕妇心力储备指标心率异常的可能影响因素的分析结果
晚孕期孕妇心力储备指标心率异常的可能影响因素的分析结果
注：1 mmHg＝0.133 kPa

```
def rm_lid_piece(self, context):
    end_index=len(context)
    same_lis=[]
    for index,part in enumerate(context):
        if index+1==end_index:
            break
        # print(part,1)
        # print(context[index+1],2)
        if part==context[index+1]:
            context[index+1]='删除重复语句：<u>'+context[index+1]+'</u>'
            same_lis.append(part)

    # print(same_lis)
    # for part in same_lis:
    #     context.remove(part)
    return context
```

### 9.删除无关短文本

例如：

《中国医药》杂志是由中华医学会主办，国家卫生部主管的国家级学术性期刊，为保护作者和杂志的合法权益，避免引起著作权纠纷，根据《中华人民共和国著作权法》相关法规，遵照中华医学会相关规定，在《中国医药》杂志刊登文章的作者（著作权人）必须在文章刊登前签署中华医学会系列杂志《论文著作权转让书》，否则不予采用，特此说明。希望能得到您的理解和支持!

该类文本通常只有一段话，现在对只有一段话的文本检查关键字，发现无关短文本的关键字特征就整段删除

```
def short_paragraphs(self,context):
    Key_words=['特此说明','欢迎作者与读者使用']
    if len(context) == 1:
        for word in Key_words:
            if word in context[0]:
                context[0]='删除整段：'+context[0]

    else:
        return context
    return context
```