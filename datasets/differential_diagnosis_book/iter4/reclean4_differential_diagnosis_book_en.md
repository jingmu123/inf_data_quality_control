## reclean1B、2B_differential_diagnosis_book_en问题
### 无关文本：
1. This work was supported in part by NIH grants R01-H52810A and Al-32247.、ISBN-13：978-3-642-84223-8 等。
```
[r'(^[\*_]*(Also[,，]? [Ss]ee [Cc]hapter|For more details?[,，]|Acknowledgements are|We (also )?thank|This work was|ISBN).*)', r'删除12:<u>\1</u>'], 
```

2. 包含Department of、Medical、Medicine的一些简短段落。
```
[r'((^(?=.{0,150}$).*(Department).*)|(^(?=.{0,300}$).*(Depa[ri]tment of|Tel：|@[a-z]{2,10}\.com).*))', r'删除15:<u>\1</u>'],  # 部门介绍
```

3. 一些无关标题及其后面一些无关段落删除，#### Further reading list、
```
def is_title(self, con):
        patter = r'(^[\\\*_ #]*(SUGGESTED READING|Suggested Reading|ACKNOWLEDGMENTS?|Acknowledge?ments?|[Rr][Ee][Ff][Ee][Rr][Ee][Nn][Cc] ?[Ee][Ss]?|(Selected )?References?|FURTHER READING|Further reading( list)|Useful websites)[\*_]*$)'
        if re.search(patter, con):
            return True
        else:
            return False

if self.is_title(con):
        context[i] = "无关标题删除-1:<u>{}</u>".format(context[i])
        context[i+1] = "无关标题后段删除-1:<u>{}</u>".format(context[i+1])
        continue
```

4. 一些简短的段落群，且与文本无关的段落群。
**spontaneously**、**fabortive**、appendicitis)、Appendiceal、**The obstruction**、**lumen is**、**persists**、**obstructed**等等。
```
if len(con) < 150 and not re.search(r'^[\* _]*(\d+\\?\. ?|[a-z]\. )', con) and (i > 0 and i < len(context) - 1 and all((len(context[j]) < 150 and not re.search(r'^[\* _]*(\d+\\?\. ?|[a-z]\. )', context[j])) for j in range(i-2, i+2) if j >= 0 and j < len(context))):
    context[i] = "简短段落群删除-1:<u>{}</u>".format(context[i])
    if not re.search(r'(^[#\*_\s]*([A-Z][a-zA-Z]+( [a-zA-Z]+){0,8})：?[_\*\s]*$)|(^[\u4e00-\u9fff]+)', context[i-1]):
        context[i-1] = "简短段落群删除-1:<u>{}</u>".format(context[i-1])
    if not re.search(r'(^[#\*_\s]*([A-Z][a-zA-Z]+( [a-zA-Z]+){0,8})：?[_\*\s]*$)|(^[\u4e00-\u9fff]+)', context[i-2]):
        context[i-2] = "简短段落群删除-1:<u>{}</u>".format(context[i-2])
    continue
```

5. 参考段落补充括号内年份特征(2009)、(1999)、(1987)。
```
(\((20[012]\d|1[89]\d{2})\))
```

6.is_page_number目录页补充排除特征为TABLE、SCA、HDL的段。
```
 if re.search(r'(^[#\*\s_]*(CASE|[Cc]ase|[Cc]hapter|Question) \d+)|(^TABLE|SCA|HDL|[Tt]able)', con):
     return False
```





