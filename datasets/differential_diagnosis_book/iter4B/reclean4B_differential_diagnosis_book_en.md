## reclean3A_differential_diagnosis_book_en问题
1. 对book中每篇文章的无关开头结束标记，和无关结尾开始标记进行统计并验证。汇总到start_end_list中，对开头结尾无关文本进行批量删除。并调整清洗结构。
```
 for s_e in start_end_list:
        id = s_e[0]
        if seq_id == id:
            start = r'^' + s_e[1]
            end = [r'^' + s_e[2]]
            if s_e[1]:
                context = cp.delete_page_start(context, start)
            if s_e[2]:
                context = cp.delete_page_ending(context, end)
```

2. 对先删除换行后清洗和先清洗后删除换行进行衡量整改，减少误删、漏删。
```
 def move_hang2(self, context, lang):
        if lang == 'en':
            context = re.sub(r'(\n\n[\*_ ]*(?:\d+\.|\(\d+\)))([\*_ ]*\n\n[\*_ ]*)([A-Z].*)', r'\1|删除序号换行|\3', context)  # 引用序号换行删除
            context = re.sub(r'(\-|[^|\n]{45,}[a-z，→\)])([ \*]*\n+\n[ \*]*)(([\“a-z&\.\(]).{45,})', r'\1|删除0换行|\3', context)
            context = re.sub(r'(\n[\* _]*(?:[Ff]ig\.?s?(ure)?|FIG\.?S?(URE)?) ?\d+(?:.\d+)? (?:[Ff]ig\.?s?(ure)?|FIG\.?S?(URE)?) ?\d+(?:.\d+)?)([ _\*]*\n+\n[ _\*]*)(.*)([ _\*]*\n+\n[ _\*]*)(.*)', r'\1|删除3图换行|\7|删除3图换行|\9', context)
            context = re.sub(r'(\n\n[\*_]*(?:[Ff]ig\.?s?(ure)?|FIG\.?S?(URE)?) ?\d+.{50,})([ \*]*\n+\n[ \*]*)(.*(?:\([a-z](?:，[a-z])?\)|T\d|T\d[A-Z]{2}|image|\(arrow\)).*(?:\([a-z](?:，[a-z])?\)|T\d|T\d[A-Z]{2}|image|\(arrow\)).*)', r'\1|删除1图换行|\5', context)
            context = re.sub(r'([ \*_]*(?:[Ff]ig\.?s?(ure)?|FIG\.?S?(URE)?) ?\d+(?:.\d+)?)([ _\*]*\n+\n[ _\*]*)(.*[^\)\.\?？ _\*][ _\*]*\n)', r'\1|删除2图换行|\5', context)
        return context
```
```
def move_hang(self, context, lang):
        if lang == 'en':
            context = re.sub(r'([^|\n]{45,}[a-z，\-\d])([ \*]*\n+\n[ \*]*)(([a-z&][^\.\)]|\d+[^\.\d\\\)s]).{45,})', r'\1|删除1换行|\3', context)
            context = re.sub(r'([,，；\(\.,;].*?[^\.\| \*]|\-)([ \*]*\n+\n[ \*]*)([a-z&\(][^\.].{3,})', r'\1|删除换行|\3', context)
            context = re.sub(r'([a-z，\d\--])([ \*]*\n+\n[ \*]*(Table) [\W\w]*?)(\n+\n[ \*]*)([a-z][^ \--].{45,})', r'\1|删除表格换行|\5\2', context)
            context = re.sub(r'([^|\n]{45,}[a-z，\-\d])(\n+\n)([ \*]*[A-Ze][A-Z\-\'a-z]+(?: [A-Ze][A-Z\-\'a-z]+)?[ \*]*\n+\n)((?:[a-z&][^\.\)]|\d+[^\.\d\\\)s]).*)', r'\3\1|删除标题插入换行|\4', context)
```

3. 取消简短段落群删除，误删严重。





