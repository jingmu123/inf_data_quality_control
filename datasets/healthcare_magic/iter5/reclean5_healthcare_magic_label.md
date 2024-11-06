## reclean5_healthcare_magic_label

### 1.无关数字

例如：

Wait for the right person and you will feel better then. GOOD LUCK !!!1（无关数字）

增加删除14：

```
[r'([^0-9][.!?])( *[0-9] *)(\n|$)',r'\1删除14:<u>\2</u>\3'],#11.5新
```

### 2.重复语句

例如：

【2】**Answer**:删除10:<u> General & Family Physician,  Dr. Pavan Kumar Gupta's  Response</u> Hello.Welcome.If the doctor has prescribed inhaler and she doesn't know how to use it then why nebulizers are not tried.good luck. 

【3】**Answer**:删除10:<u> General & Family Physician,  Dr. Pavan Kumar Gupta's  Response</u> Hello.Welcome.If the doctor has prescribed inhaler and she doesn't know how to use it then why nebulizers are not tried.good luck. 

增加删除重复语句：

```
def rm_lid_piece(self, context):  # 删除重复语句
    end_index = len(context)
    same_lis = []
    for index, part in enumerate(context):
        if index + 1 == end_index:
            break

        if not re.sub(r'\s', '', part) or not re.sub(r'\s', '', context[index + 1]):
            continue
        if part == context[index + 1]:
            context[index + 1] = '删除重复语句：<u>'+context[index+1]+'</u>'
            same_lis.append(part)
        elif part in context[index + 1] or context[index + 1] in part:
            context[index + 1] = ''

    return context
```

### 3.无关文本补充

例如：

【1】**Answer**:General & Family Physician,  Dr. Vakul Aren's  Response (这里开始)Welcome to HCM.（这里结束）The sensory paraesthesia........

补充到删除11：

```
[r'( *(?:[Hh][Ii](?: [A-Za-z0-9]{2,15})?[ \.!,]?|[Hh][Ee][Ll]{2}[Oo](?: [A-Za-z0-9]{2,15})?[ \.!,]?| ?and ?| ?[Tt][Oo] ?| ?[Dd][Ee][Aa][Rr] ?[A-Z][a-z]*\.[a-z]*[ \.!,]?| ?[Ww][Ee][Ll][Cc][Oo][Mm][Ee] ?| ?[Tt][Hh][Aa][Nn][Kk][Ss]? ?| ?[Ff][Oo][Rr] [Yy][Oo][Uu][Rr] [Qq][Uu][Ee][Rr][Yy] ?){2,}[^\n.?!]*(?:service|HCM|hcm|[Mm][Aa][Gg][Ii][Cc]|[Hh][Ee][Aa][Ll][Tt][Hh] ?[Cc][Aa][Rr][Ee]|site|[Ff][Oo][Rr][Uu][Mm])[\.?!]?)',r'删除11:<u>\1</u>'],#新
```

### 4.无关链接补充

例如：

my email address is safia\_Ahmed\_23@ WWW.WWWW.WW 

补充到删除3：

```
[r'([\.!\?])([^\n.]*(?:(?:[Dd ][Rr]\.)[^\n.]*)*(?:YYYY@YYYY|@[A-Za-z0-9]+\.com| [Ll][Ii][Nn][Kk] *[:：]|@ *[Ww]{2,4}\.).*)',r'\1删除3:<u>\2</u>'],#改
```

### 5.Regards类的补充

例如：

 recovery. Regards, Rajiv K Khandelwal http://goo.gl/SuCjl 

 day.With regards,Dr Sanjay KanodiaMD-DERMATOLOGY & Sexually transmitted diseases 

增加删除16：

```
[r'(?:([\.!\?,"]))( *[A-Za-z]* *[Rr][Ee][Gg][Aa][Rr][Dd][Ss].{0,100})(\n|$)',r'\1删除16:<u>\2</u>\3'],
```

### 6.新一类的链接补充：

#### 6.1例如：

 any other questions, please feel free to ask me directly at any time at the link below: http://doctor.healthcaremagic.com/Funnel?page=askDoctorDirectly&docId=69765Bes.

特征是链接在link below: 后面，删除与链接相连的话，以符号（，。？！）作为界限，补充句号，增加删除17：

```
[r'([,\.?!][^\n\.,?!]*link below:.*)',r'.删除17:<u>\1</u>'],
```

#### 6.2例如：

I recommend you consult a pediatrician as early as possible for examination of her skull and doing the appropriate investigations.删除18:<u> If you need more help, go to: www.med50.blogspot.com </u>

完整链接所在的那一句短句子整句删除，增加删除18：

```
[r'([^\n.]*(?:https?[：:][/／]{1,2}(?:www[.．])?|www[.．])[a-zA-Z0-9@／/-]+(?:[.．／/&][a-zA-Z0-9@／/_?=\-]{2,})+[^\n.?!]*[.?!]?)(\n|$)',r'删除18:<u>\1</u>\2']
```