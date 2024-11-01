## reclean4_healthcare_magic

### 1.结合欢迎词，对欢迎来到XXX的遗漏删除

例如：

Hello and welcome to healthcaremagicI am Dr. Kakkar.

 hello and welcome to HCM forum,

 Hi.Thanks for the query.

 Hello and welcome to ‘Ask A Doctor’ service.

因为这类删除是上一次清洗是开始标注的，已经不属于个例，属于出现频率比较高的无关文本，需要提取特征，对几类的欢迎词收集起来，当连续出现两次以上时会匹配到这一句结束，增加删除11：

```
[r'( *(?:[Hh][Ii][ \.!,]?|[Hh][Ee][Ll]{2}[Oo][ \.!,]?| ?and ?| ?[Dd][Ee][Aa][Rr] ?[A-Z][a-z]*\.[a-z]*[ \.!,]?| ?[Ww][Ee][Ll][Cc][Oo][Mm][Ee] ?| ?[Tt][Hh][Aa][Nn][Kk][Ss]? ?| ?[Ff][Oo][Rr] [Yy][Oo][Uu][Rr] [Qq][Uu][Ee][Rr][Yy] ?){2,}(?:(?:[^\n,\.!?])+(?:[Dd][Rr]\.))*(?:[^\n,\.!?])*[,\.!?])',r'删除11:<u>\1</u>'],#新
```

### 2.无关链接遗漏

例如：

psychiatrist. I hope this information has been both informative and helpful for you. Wish you Good Health. Regards, Dr.删除8:<u> Ashish Mittal www.99doctor.com </u>

把Dr.的英文逗号识别的上一句话的结尾了，现在补充到删除8：

```
[r'([\.\?!])((?:(?:[^\n\.!?])+(?:[Dd][Rr]\.))*(?:[^\n,\.!?])*)((?:[Hh]ttps?[：:][/／]{2}(?:www[.．])?|www[.．])[a-zA-Z0-9@／/-]+(?:[.．／/][a-zA-Z0-9@／/_\-]{2,})+.*)',r'\1删除8:<u>\2\3</u>'],#改
```

### 3.新一类的链接补充

例如：

thrice a day.（从这里开始） dr.mohsin madni madni66@saudia.com

form .（从这里开始） for Management kindly click on my link : bit.ly/drmunishsood

补充到删除3：

```
[r'([\.!\?])([^\n.]*(?:(?:[Dd ][Rr]\.)[^\n.]*)*(?:YYYY@YYYY|@[A-Za-z0-9]+\.com| [Ll][Ii][Nn][Kk] *[:：]).*)',r'\1删除3:<u>\2</u>'],#改
```

### 4.XXX医生的回复类的补充

例如：

 Otolaryngologist （符号）/ ENT Specialist,  Dr. Naveen Kumar Nanjasetty's  Response

Dentist, Periodontics,  Dr. Palvi （符号）'s  Response

补充符号：/、'到删除10：

```
[r'([:：])( *(?:(?:[A-Z\'][A-Za-z，,\'’\.]+|[&/]|[Aa][Nn][Dd]) +)+Response)',r'\1删除10:<u>\2</u>'],#改
```

### 5.新一类的祝福词+人名的删除

例如：

thank you very much. （从这里开始）Sincerely, XXXXXXX Whinston 11/19/18. 

shall be glad to answer any further apprehensions.（从这里开始）Sincerely,

 pain subsides after sometime.（从这里开始） help pls 

增加删除11：

```
[r'([,\.!?])( *(?:[Ss][Ii][Nn][Cc][Ee][Rr][Ee][Ll][Yy] *,.{0,100}|help pls *))(\n|$)',r'\1删除11:<u>\2</u>\3'],#新
```

### 6.无关符号删除

例如：

but it doesn't seem to work. Been going on for months. （从这里开始）+ 

Pls help Doctors.（从这里开始）✨ 

增加删除12：

```
[r'([.!?])( *[^\nA-Za-z0-9)\.!"”\'?/ ] *)(\n|$)',r'\1删除12:<u>\2</u>\3']#新
```