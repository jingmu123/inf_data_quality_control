## reclean1_differential_diagnosis_book_en问题清洗
### 错误删除：
1. 误删CASE 29，当成页码段，page_number_duan函数整改，添加判断。
```
        if re.search(r'(^(CASE|[Cc]ase))', con):
             new_list.append(con)
             continue
```

2. 删除9误删正文，针对图例内容其他方法已清洗，删除9直接取消。

### 无关文本：
1. 建议阅读文献，SUGGESTED READING及参考。在move_ref函数里将特征补充，补充英文的标点符号,;：:
```
patterns = [
            r'^[\*\.]*[\d _]*(\d+\\?\.|[A-Z][A-Z\-\'a-z]+[，,]? [A-Z ]{1,4}[\.，,：\(])',  # 参考文献开头，序号或者人名
            r'([\s，,]+et al[\.:：，,]+)',  # et al
            r'(\d+(\(\d+\))?[：:；; ,，]+[a-zA-Z]?\d+)|([a-zA-Z]?\d+[\-–][a-zA-Z]?\d+[，,\.])',  # 页码范围格式
            r'([Dd]oi[：:])',  # DOI
            r'([Vv]ol\.?\s*\d+)',  # 卷号
            r'(no\.?\s*\d+)',  # 期号
            r'([，, ]+p[p \.]*\d+|p[p \.]*\d+[：,，\- ]+)',  # 页码
            r'(ht ?tps?[：:])',  # 网址
            r'([，,；;][A-Za-z_ ]*\d{4}[，,\._]+)|([A-Z]\. ?\(\d{4}\)\.)|([\.;；：:，, ]\d{4}[;；：:，,\.])',  # 年份
            r'(ed \d+[，,])|((2nd|1st|3rd|\d+th) ed)',  # 版本号
            r'(Accessed|editor：|Pub\-?lishing|Germany：|London：)',  # 访问、出版、编辑、地点
            r'(， ?[A-Z]{2,3}[，,：\.])'  # 地名，缩写
            r'(ISBN：)'  # ISBN
        ]
```

2. 删除无关标题，SUGGESTED READING、**ACKNOWLEDGMENT**、Acknowledgments等。删除5补充。
```
[r'(^[\\\*_ ]*(\d+|[A-Z]{1,2}|SUGGESTED READING|ACKNOWLEDGMENT|Acknowledgments?|I. INTRODUCTION|REFERENCES?|(Selected )?References?|FURTHER READING|Further reading|5\'\-\-CACGTAAGCTATGCAGGCTT\-\-3\'|Useful websites)[\*_]*$)',  r'删除5:<u>\1</u>'],
```

3. 致谢段落，The author thanks。。。、The authors would like to thank。。等
```
[r'(^(The authors? (would like to )?thanks?).*)', r'删除11:<u>\1</u>'],
```

4. 参考文献补充小写开头的人名，_4_ eesbrough MJ. Osteolysiss aanndd psoriasis. Clin Exp Dermatol 1979；4：341-4.补充类似_4_ 序号开头，补充et a.等，move_ref函数里patterns补充特征。
```
r'^[\*\.]*[\d _]*(\d+\\?\.|[A-Ze][A-Z\-\'a-z]+[，,]? [A-Z ]{1,4}[\.，,：\(])',
r'([\s\.，,]+et al?[\.:：，,]+)', 
```

5. 图注无关内容，两个图例同一段，及后面两段相关的图注内容。FIGURE 8.1 FIGURE 8.2|删除3图换行|Psoriatic subungual hyperkeratosis associated with _Trichophyton rubrum invasion._|删除3图换行|Psoriatic onycholysis associated with Trichophyton _rubrum invasion._
```
context = re.sub(r'(\n[\* _]*(?:[Ff]ig\.?s?(ure)?|FIG\.?S?(URE)?) ?\d+(?:.\d+)? (?:[Ff]ig\.?s?(ure)?|FIG\.?S?(URE)?) ?\d+(?:.\d+)?)([ \*]*\n+\n[ \*]*)(.*)([ \*]*\n+\n[ \*]*)(.*)', r'\1|删除3图换行|\7|删除3图换行|\9', context)
```

6. 无关段落，Also， see Chapter 39.、For more details， you may refer to Chapter 39.、Acknowledgements are
```
[r'(^(Also[,，]? [Ss]ee [Cc]hapter|For more details?[,，]|Acknowledgements are).*)', r'删除12:<u>\1</u>'], 
```

7.文献来源，**From： Jackson MA， Nelson JD.、**from： Aitken G. Proximal femoral 、**From： Endocrine Pathology：、Source： Reprinted with permission from等。
```
[r'(^[\*_]*([Ff]rom：|Source：).*)', r'删除13:<u>\1</u>'],
```

8. 参考文献补充，当特征满足两个且段落长度小于200时，也进行删除。
```
             if p_sum >= 3 or (p_sum == 2 and len(con) < 200):
                 con = "参考删除-1:<u>{}</u>".format(con)
```

### 多余换行：
1. 标题穿插导致的多余换行，。。particularly in the presence of contact with a（换行）**Hemoptysis**（换行）known case. 。。等。
```
context = re.sub(r'([^|\n]{45,}[a-z，\-\d])(\n+\n)([ \*]*[A-Ze][A-Z\-\'a-z]+(?: [A-Ze][A-Z\-\'a-z]+)?[ \*]*\n+\n)((?:[a-z&][^\.\)]|\d+[^\.\d\\\)s]).*)', r'\3\1|删除标题插入换行|\4', context)
```

2. →结尾的需要换行的情况，gene (CTNNB1) to 3p22→（换行）p21.3 by fluorescence in。。。删除0换行里补充。
```
context = re.sub(r'([^|\n]{45,}[A-Za-z，\-\d→\)])([ \*]*\n+\n[ \*]*)(([\“a-z&\(]|\d+[^\.\d\\\)s]).{45,})', r'\1|删除0换行|\3', context)
```



