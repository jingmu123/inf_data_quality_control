## reclean0_cdc
### 无关文本：
1.( _10_ )、( _9_ , _11_ – _13_ )、句末(2)(4-3)等。

```[r'([^,\.;\n] +)([\(（][\d\-,～~，;；–—、\s_]+[\)）])', r'\1删除1:<u>\2</u>'],```

2.网址删除。

```
def step6_unrelated_text(self, context):
    patter2 = r'([\(（]\**[  ]*(https?:\/\/)?(www\.)?([\da-z \.\-@]+)\.([a-z]{2,6})([\/\w\?=\.-]+)?\/?[\)）]|\**[  ]*(https?:\/\/)?(www\.)?([\da-z \.\-@]+)\.([a-z]{2,6})([\/\w\?=\.-]+)?\/?)'
    website_list = re.findall(patter2, context)
    for web in website_list:
        if len(re.findall(r'\.', web[0])) >= 2:
            context = re.sub(re.escape(web[0]), rf'删除2:<u>{web[0]}</u>', context)
    return context
```

3.| --- |表格类型。
```
[r'\|', ''],
[r'([\-]{3,})', ''],
```

4.<img></a></td></tr></tbody>等网页符号元素。
```
[r'(<[\/\w]+>)+', ''],
```

**0823补充：**

1.无关页面删除。
```
def wuguan_ye(context):
    exit_flag = False
    wuguan = ["COMMENTARY_PCD_ s First", ]
    for txt in wuguan:
        if txt in context:
            context = "(本页删除)本页文本质量太差:\n" + context
            exit_flag = True
            break
    return context
```

2.Author Information
```
[r'((Author Information)[\w\W]*?(\n[  ]*\n))', r'删除3:<u>\1</u>'],
```

3.( Appendix Table 1)、( Figure 2 , panel B)、( Table 1 )等。
```
[r'([\(（]\s*(Figure|Table|Appendix)[^\(\)（）\n]*[\)）])', r'删除4:<u>\1</u>'],
```

4.Figure 1 . 、Figure . Frank 图注，表注，附录等。
```
[r'([  \t]*(Figure|Table|Appendix)[^\(\)\n]*)', r'删除5:<u>\1</u>'],
```

5.网址、邮箱链接判断优化。
```
def step1_delurl(self, context):
    patter2 = r'([\(（][^\(\)（）\n]*(https?:\/\/)?(www\.|[Ee]?-?mail:)?([\da-z \.\-@]+)\.([a-z]{2,6})([\/\\\w\?=\.-]+)?\/?[^\(\)（）\n]*[\)）]|\s*(https?:\/\/)?(www\.|[Ee]?-?mail:)?([\da-z \.\-@]+)\.([a-z]{2,6})([\/\\\w\?=\.-]+)?\/?)'
    website_list = re.findall(patter2, context)
    for web in website_list:
        if len(re.findall(r'(\.|:|\/\/)', web[0])) >= 2:
            context = re.sub(re.escape(web[0]), rf'删除2:<u>{web[0]}</u>', context) 
    return context
```

6.将删除4和5合一起防止误删。
```
[r'(([\(（][^\(\)（）\n]*(Figure|Table|Appendix)[^\(\)（）\n]*[\)）])|([  \t]*(Figure|Table|Appendix)[^\n]*))', r'删除4:<u>\1</u>'],
```

7.step1补充人物介绍等无关文本（还在补充）。
```
def step1_del_wuguan(self, context):
    patter3 = r'(Dr\.? |[Pp]rofessor |[Uu]niversity | is a |research(er)? )'
    if len(re.findall(patter3, context)) >= 3:
        context = "(此段删除)无关文本-1:" + context
        # context = ""
    return context
```

8.Author Information修改补充。
```
[r'(\n[  \t]*(Author Information)[\w\W]*)', r'删除3:<u>\1</u>'],
```

9.Abstract --------前的无关内容。
```
[r'([\w\W]*)(\n[  \t]*Abstract\n(\-{7,}))', r'删除6:<u>\1</u>(以上都删除)\2'],
```

**0826补充：**

1.Author contributions、Author Affiliations
```
[r'((Author contributions:|Author Affiliations:)[^\n]*)', r'删除7:<u>\1</u>'],
```

2.补充删除不带括号的网址相关的句子。
```
for web in website_list:
    if len(re.findall(r'(\.|:|\/\/)', web[0])) >= 2:
        if re.findall(r'([\(\)（）])', web[0]):
            context = re.sub(re.escape(web[0]), rf'删除2:<u>{web[0]}</u>', context)
        else:
            context = re.sub(r'([^\n\.]*' + re.escape(web[0]) + r'[^\n\.]*\.?)', r'删除2-1:<u>\1</u>', context)
```

3.补充Background --------前的无关内容。
```
[r'([\w\W]*)(\n[  \t]*(Abstract|Background)\n(\-{7,}))', r'删除6:<u>\1</u>(以上都删除)\2'],
```

4.删除致谢Acknowledgments、引用References、作者信息Author Information。
```
[r'((Acknowledgments|References|Author Information)\n(\-{7,})[\w\W]*)', r'以下都删除1:<u>\1</u>'],
```

5.一些特定无关段落。
```
[r'((Members of the CDC Brazil Investigation Team:)[^\n]*)', r'删除8:<u>\1</u>'],  
```

6.补充括号内no.无关文本，(GenBank accession no. AY029767)。
```
[r'(([\(（][^\(\)（）\n]*(Figure|Table|Appendix|no\.)[^\(\)（）\n]*[\)）])|([  \t]*(Figure|Table|Appendix)[^\n]*))', r'删除4:<u>\1</u>'],
```

7.补充特定无关Top of Page、Top、### Box.。
```
[r'((Members of the CDC Brazil Investigation Team:|\n[  \t]*Top|\*+Public Health and pharmacy:|### Box\.|On This Page)[^\n]*)', r'删除8:<u>\1</u>'], 
```

8.人物介绍，Dr Agüero is a、Ms. Pham is a 、Col. G. Dennis Shanks is the等。
```
[r'((\n[  \t]*(Drs?|M[sr]|Prof|Col\. G|Hanna Y)\.? )[^\n]+)', r'删除9:<u>\1</u>'], 
```

9.\[ _11_ \]、 [ 11 ]等。
```
[r'([^,\.;\n] +)(\\?\[[\d\-,～~，;；–—、\s\\_]+\])', r'\1删除10:<u>\2</u>'],
```

10.补充图注，表注，附录，句中图表描述。
```
[r'(\n[  \t]*\**(Figure|Table|Appendix)[^\n]*)', r'删除5:<u>\1</u>'],
[r'([^\.\n]*(((Figure|Table|Appendix)[\d\-～~–—\. _]+shows?)|( in (Figure|Table|Appendix) \d))[^\.\n]*\.)', r'删除5-1:<u>\1</u>'],
```

11.Related Pages。
```
[r'(\n[  \t]*(Related Pages)[\w\W]*)', r'以下都删除2:<u>\1</u>'],
```

