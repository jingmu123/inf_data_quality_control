## reclean0B_differential_diagnosis_book问题
### 无关文本：
1. (Roos et al.， 1991)、(Geschwind et al.， 1999)、(Brodaty et al.， 2002； Oliveira et al.， 2004； Wszolek et al.， 2006)等括号内无关人名。
```
[r'([\(（][^（）\(\)]+et al\.?[，；,; ]+\d{4}[^（）\(\)]*[）\)])', r'删除1:<u>\1</u>'],
```

2. (Fig. 11.98a )、(Figure 6.5c)、(Figure 29.20)、(Figure 5.60a and b)、(Page 348)、(see Table 14-1)、(Exhibit 15-1)等。补充删除括号内第几章，Table，box，(Chapter 15)、(Chapter 9)、(Box 9)、(Table 1-2)等。
```
[r'([\(（]([Ff]ig\.?(ure)?|[Ss]ee|[Pp]age|[Ee]xhibit|[Pp]icture|Chapter|[Bb]ox|[Tt]able) [^（）\(\)]*[）\)])', r'删除2:<u>\1</u>'],
```

3. 零碎简短的无关段落，B、C、_a_ b C、a b C、a bC、_a_ bC等
```
[r'(^[\*_]*(\w{1,2}( \w{1,2})+|(\w\.?)|[\d_ ]+)[\*_]*$)', r'删除3:<u>\1</u>'], 
```

4. 无关的页码索引段落群，**innervated by， 361-362**、Ureteral stones， 366-367、**Ureteral obstruction， 362**等，以及较长的一大段无关的页码索引段落。
```
    def page_number_duan(self, context):
        new_list = []
        for con in context:
            number_len = len(re.findall(r'([，；] ?\d+[a-z]?[\d\-]*[a-z]?)', con))
            if number_len > 30:
                con = f'此段无关页码删除:<u>{con}</u>'
            if re.search(r'([^\d][，；\._ ]+\d+[a-z]?[\d\-]*[a-z]?[\*_]*$)|(^[\*_]*[a-z\\\-A-Z ]+\d+[\*_]*$)', con) and len(con)<150:
                con = f'此段无关页码删除:<u>{con}</u>'
            new_list.append(con)
        return new_list
```

5. 无关参考文献，Albin RL， Bromberg MB， Penney JB， et al. (1988) Chorea and dystonia： a remote effect of carcinoma.Mov Disord 3：162-169.补充ed 1， St. Louis， MO， 2015，_ 、ed 2， vol. 1. Balti-_ more， 1999，、at https：//www.kidney.org/sites/default/files/uti.pdf、Ac-cessed June 28，2016等样式。以及无关标题I. INTRODUCTION、REFERENCES。
```
[r'(^[\*\.]*[\d _]*(?:(\d+\\?\.)|([A-Z][A-Z\-\'a-z]+，? [A-Z \.]{1,6}[，：\(])).*(\d+(?:\(\d+\))?[：:； ]+[a-zA-Z]?\d+|[a-zA-Z]?\d+\-[a-zA-Z]?\d+[，\.]|et al\.|https?：\/\/|[， ]+p ?\d+|ed \d+，|[\.，][A-Za-z_ ]+\d{4}[，;；\._]+).*)', r'删除4:<u>\1</u>'], 
```
```
[r'(^[\*_]*(\d+|[A-Z]{1,4}|I. INTRODUCTION|REFERENCES?|(Selected )?References?|FURTHER READING|Further reading|5\'\-\-CACGTAAGCTATGCAGGCTT\-\-3\'|Useful websites)[\*_]*$)',  r'删除5:<u>\1</u>'],
```

6. 补充删除参考遗留的零碎段落，Knutson T.， Bothwell J.， Durbin R. Evaluation and management\n(换行)of traumatic knee injuries in the emergency department.
```
[r'(^(?=[\w\W]{0,150}$)[A-Z][a-z]+ [A-Z\.]{1,6}，.*\n?.*)', r'删除6:<u>\1</u>'],  # 删除4参考遗留的段落
```

7. 删除参考文献move_ref补充整改优化，判定特征个数，将大于等于三个参考特征的段落删除。
```
    def move_ref(self, context):
        new_list = []
        patterns = [
            r'^[\*\.]*[\d _]*(\d+\\?\.|[A-Z][A-Z\-\'a-z]+，? [A-Z \.]{1,6}[，：\(])',  # 参考文献开头，序号或者人名
            r'([\s，]+et al[\.:：，]+)',  # et al
            r'(\d+(\(\d+\))?[：:； ]+[a-zA-Z]?\d+|[a-zA-Z]?\d+\-[a-zA-Z]?\d+[，\.])',  # 页码范围格式
            r'([Dd]oi[：:])',  # DOI
            r'([Vv]ol\.?\s*\d+)',  # 卷号
            r'(no\.?\s*\d+)',  # 期号
            r'([， ]+p[p \.]*\d+|p[p \.]*\d+[：，\- ]+)',  # 页码
            r'(ht ?tps?[：:])',  # 网址
            r'(，[A-Za-z_ ]*\d{4}[，\._]+)|([A-Z]\. ?\(\d{4}\)\.)',  # 年份
            r'(ed \d+，)',  # 版本号
            r'(Accessed|editor：|Pub\-?lishing|Germany：)',  # 访问、出版、编辑
            r'(， ?[A-Z]{2,3}[，：\.])'  # 地名，缩写
        ]
        for con in context:
            p_sum = 0
            for pat in patterns:
                if re.search(pat, con):
                    p_sum += 1

            if p_sum >= 3:
                con = "参考删除-1:<u>{}</u>".format(con)

            new_list.append(con)
        return new_list
```

8. 段落开头的无关中文字符。咖II：s your urine clear or cloudy?、咖When you go out into cold、·上Have you ever been、\*上Have you had any problems with等。
```
 # [r'(^[\\\*· ]*)([\u4e00-\u9fff]+)', r'\1'],  # 去标签时打开
```

9. 无关段落，del(13q)..、This page intentionally left blank、(a) _(b)_ (c)、(a)(b)等。
```
[r'(^[\*_]*(del\(13q\).{0,10}|This page intentionally left blank|( ?\([a-z]\) ?_?)+|[a-z_\d]{1,3} [a-zA-Z])[\*_]*$)', r'删除7:<u>\1</u>'],
```

10. 开头包含特定无关内容的段落，例**www.pms.org.UK**、www.nlm.nih.gov/medlines、邮箱Email:等。
```
[r'(^[\*_]*(www\.|E?mail:).*)', r'删除8:<u>\1</u>'],
```

11. 补充删除图注多余换行遗留的无关部分，包含(arrow)、T1、T2WI 、(b)、(C)等特征。
```
[r'(^(?=.{50,350}$)(.*(?:\([a-zA-Z]\)|T\d|T\d[A-Z]{2}|image|\(arrow\)).*(?:\([a-zA-Z]\)|T\d|T\d[A-Z]{2}|image|\(arrow\)).*))', r'删除9:<u>\1</u>'],  # 图注换行部分
```

12. 特殊符号删除，■、©、●等。
```
[r'(■|©|●)', r''],
```

### 多余换行：
1. go through a prolonged\n\n(换行)prodromal phase 、how hypotension and \n\n(换行)develop 等。

2. 表格插入换行。

3. 一般多余换行，加入开头和结尾都有*号的情况， if one or more of the following are**\n\npresent：**。

4. 补充上段结尾是小写字母结尾，下端是括号（开头的多余换行。

5. 图片描述段落多余换行导致漏删，在删除前补充删除换行。并补充上段大写字母结尾，下段（括号开头的情况。

6. 引用文献的序号单独一行，导致引用漏删，9.\n\nShehan JM, Kalaaji AN, Markovic SN, 、5.\n\nBerge RL, Oudejans JJ,等。
```
    def move_hang(self, context, lang):
        if lang == 'en':
            context = re.sub(r'([^|\n]{45,}[a-z，\-\d])([ \*]*\n+\n[ \*]*)(([a-z&][^\.\)]|\d+[^\.\d\\\)s]).{45,})', r'\1|删除1换行|\3', context)
            context = re.sub(r'([^|\n]{45,}[a-z，\-\d])([ \*]*\n+\n[ \*]*)((\( ?[^\d]).{45,})', r'\1|删除2换行|\3', context)
            context = re.sub(r'([a-z，\d\--])([ \*]*\n+\n[ \*]*(Table) [\W\w]*?)(\n+\n[ \*]*)([a-z][^ \--].{45,})', r'\1|删除表格换行|\5\2', context)
        return context
```
```
    def move_hang2(self, context, lang):
        if lang == 'en':
            context = re.sub(r'(\n\n[\*_ ]*(?:\d+\.|\(\d+\)))([\*_ ]*\n\n[\*_ ]*)([A-Z].*)', r'\1|删除序号换行|\3', context)  # 引用序号换行删除
            context = re.sub(r'([^|\n]{45,}[A-Za-z，\-\d\)])([ \*]*\n+\n[ \*]*)(([\“a-z&\(][^\d\.\)]|\d+[^\.\d\\\)s]).{45,})', r'\1|删除1换行|\3', context)
            context = re.sub(r'(\n\n[\*_]*(?:[Ff]ig\.?s?(ure)?|FIG\.?S?(URE)?) ?\d+.{50,})([ \*]*\n+\n[ \*]*)(.*(?:\([a-z](?:，[a-z])?\)|T\d|T\d[A-Z]{2}|image|\(arrow\)).*(?:\([a-z](?:，[a-z])?\)|T\d|T\d[A-Z]{2}|image|\(arrow\)).*)', r'\1|删除图换行|\5', context)

        return context
```


