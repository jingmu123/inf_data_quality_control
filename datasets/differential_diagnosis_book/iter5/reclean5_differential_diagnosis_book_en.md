## reclean4A_differential_diagnosis_book_en问题
### 无关文本：
1. 一半括号的无关内容，of f-PTCL is distinct from AITL [471.
```
[r'((\\?\[[\d\s,，\–\-—]{1,}\\?\]?)|(\\?\[?[\d\s,，\–\-—]{1,}\\?\]))', r'通用删除6(英):<u>\1</u>'],
```

2. 序号开头的目录段落群删除。避免删除单个的章节标题。
**6.8 Caecal Carcinoma....**
**6.9 Crohn's Disease.**
**6.10 Sigmoid Diverticulitis. 100**
**6.11 Segmental Omental Infarction.**
6.12 Other Conditions 104
```
 # 目录段落群
pp = r'(^(?=.{0,150}$)[\*_\s]*\d+(\.\d+)+[\s_]*[A-Z].*)'
if i > 0 and i < len(context) - 1 and all((re.search(pp, context[j]) or re.search(r'^目录段删除', context[j])) for j in range(i-1, i+2) if j >= 0 and j < len(context)):
    context[i] = "目录段删除-1:<u>{}</u>".format(context[i])
    context[i-1] = "目录段删除-1:<u>{}</u>".format(context[i-1])
    context[i+1] = "目录段删除-1:<u>{}</u>".format(context[i+1])
    continue
```

3. 通用间距删除，补充优化delete_page_middle，删除CONTENTS标题开始的目录页段落群。	
```
def delete_page_middle(self, context):
    start_to_end = [
        [r'(^[\*_ ]*(CONTENTS|Contents)[\*_ ]*$)', r'(^[#\*_\s]*([A-Z][a-zA-Z]{3,}( [a-zA-Z]{3,}){0,8})：?[_\*\s]*$)|(.{200,})', 0],
    ]
    for middle in start_to_end:
        delete_line_index = []
        flag = False
        for index, item in enumerate(context):
            if re.search(middle[0], item):
                satrt = [index, 0]
                delete_line_index.append(satrt)
                flag = True
                continue
            if flag:
                if re.search(middle[1], item):
                    end = [index, 1]
                    delete_line_index.append(end)
                    flag = False
                else:
                    pass
        length = len(delete_line_index)
        if length >= 2:
            for i in range(1, length):
                if delete_line_index[i - 1][1] < delete_line_index[i][1]:
                    start_index = delete_line_index[i - 1][0]
                    end_index = delete_line_index[i][0]
                    for i in range(start_index, end_index + middle[2]):
                        context[i] = "通用间距删除-1:<u>{}</u>".format(context[i])
                        # context[i] = ""
    return context
```

4. 补充无关标题，Reterences、APPENDIX、Appendix、**APPENDIX16-1**等。
```
[r'(^[\\\*_ #]*([Rr][Ee][Fft][Ee][Rr][Ee][Nn][Cc] ?[Ee][Ss]?\.?)[\*_]*$)',  r'删除5:<u>\1</u>'], 
[r'(^[\*_]*(APPENDIX|Appendix).*)', r'删除12:<u>\1</u>'], 
```

5. 无关括号里的数字内容，(392)、(388，403)、(386，387，389，391-396，399，401-403，405)等。
```
[r'(\\?\([\d\s,\\，\-\–—]{1,}\\?\))', r'通用删除7(英):<u>\1</u>'],
```

6. 参考文献开头特征补充中括号序号，\[18\] Lawton S, Littlewood S. (2006). Vulval 、\[19\] Lawton S. Anatomy and等。
```
r'^[\*\.]*[\d _]*(\\?\[\d+\\?\]?|_\d+_ ?|\d+\\?[\.，][^\d]|[A-Ze][A-Z\-\'a-z]+[， ,]?[A-Z ]{1,4}[\.，,：\(])',
```





