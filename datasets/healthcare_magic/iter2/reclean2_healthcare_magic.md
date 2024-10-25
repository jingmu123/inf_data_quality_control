## reclean2_healthcare_magic

### 1.祝福词+人名 



#### 1.1补充符号

例如：

I will be glad to assist.Take care,（补充逗号到匹配结尾的固定格式）Dr. Johny Chacko

should also regress gradually.Yours truly,（补充逗号到匹配结尾的固定格式）Dr Brenes-Salazar MDMayo Clinic MN

Aurvidic med? Thanks and Regards, -（补充横杠到匹配结尾的固定格式）Rohit Nagpal 

因为之前遇到的单词间隔都是空格，所以在后续人名的匹配上，间隔符号只有空格、句号（用于人名时是人名的格式）、&、

例如：

by quitting alcohol.Regards,（以逗号结尾，补充结尾符号逗号）

这类句子没有人名在后面，只有一个祝福词和一个逗号结尾



#### 1.2大小写补充

例如：

this will help you.REGARDS.

 all by itself. take care regards 

补充相关大小写字符到正则



#### 1.3单词粘连导致没有匹配到

例如：

plan further line of management.Please feel free to revert for further queries.RegardsDr.Praveen（Regards和Dr粘连）
  free to revert for further queries.RegardsDr.Praveen（Regards和Dr粘连）

 Consult your dentist if problem persist. Take Care Regards Dr.Neha（Regards和Dr没有粘连，但是没有符号连接，补充在这一类）



#### 1.4新类型的无关文本

例如：

 Have a great weekend. （从这里开始后面都是）Many Thanks XXXXX
Once again, thank you and have a nice day. （从这里开始后面都是）XXXX 

anic disorder/attacks.（从这里开始后面都是）Truly yours,Dr Brenes-Salazar MDCardiologyMayo Clinic MN

Hope to have clarified some of your uncertainties!（从这里开始后面都是）Wishing all the best, Dr. Iliri 
Hope to have clarified some of your uncertainties!（从这里开始后面都是）Wishing good health, Dr. Iliri

If you have any further queries I will be happy to help.（从这里开始后面都是）"With good health wishes"Dr Sanjay Kumar KanodiaMD (Dermatology & STDs)
e real fact and accordingly treatment may be planed.（从这里开始后面都是）Regards - Dr KK ( Karade )

to cum completly.（从这里开始后面都是） thanlk u
investigations. （从这里开始后面都是）thanQ 
Hence consult good dermatologist. Defenetly Ur problem will be solve.（从这里开始后面都是）ok thanQ 

以上补充到删除1，分为两条正则

```
[r'([\.!\?])( *(?:Kind [Rr]egards|(?:[Tt]ake [Cc]are )?[Rr][Ee][Gg][Aa][Rr][Dd][Ss][\.!,]?(?: *[Dd][Rr])?|[Dd][Rr]|Best wishes|(?:Take Care\.)?Best|Yours truly|Truly yours)(?:[ .&\-,]+[A-Z][^\n ]*)* *(?:\([^\(\)\n]+\))? ?)(\n|$)',r'\1删除1:<u>\2</u>\3'],
[r'([\.!\?])( *(?:(?:Many *)?Thanks!?(?: and [Rr]egards[\.,])?|Best of luck\.|(?: Wishing you )?[Aa]ll the best!?|[Tt]ake care[\.!]?|Thank you(?: *[Dd][Rr])?|Cheers & Godspeed!|X{3,}|Wishing *(?:good health|all the best)|"With good health wishes"Dr|(?:[Oo][Kk])? *than(?:Q|l?k u))(?:[ .&\-,]+[A-Z][^\n ]*)* *(?:\([^\(\)\n]+\))? ?)(\n|$)',r'\1删除1:<u>\2</u>\3'],
```

### 2.特殊符号补充

例如：:-)

补充到删除符号

```
[r'((?:\:\-?\()|(?:\:\-?\)))',r'删除符号:<u>\1</u>']
```



### 3.链接文本补充

例如：

**Answer**: Brief Answer:You are welcome!（从这里开始后面都是）Detailed Answer:I am glad to have been helpful!If you have any other uncertainties you can ask me directly at any time at the link below: http://doctor.healthcaremagic.com/Funnel?page=askDoctorDirectly&docId=69765Wishing a relaxing evening to you too!Dr. Iliri

补充到删除8：

```
[r'([\.!\?])([^\n.]*)((?:[Hh]ttps?[：:][/／]{2}(?:www[.．])?|www[.．])[a-zA-Z0-9@／/-]+(?:[.．／/][a-zA-Z0-9@／/_\-]{2,})+.*)',r'\1删除8:<u>\2\3</u>'],
```

### 4.删除个例补充

例如：

Thank you for choosing HealthcareMagic.

补充到删除个例

### 5.祝福词与正文粘连（需要补充标点）

例如：

hope I have answered your query（从这里开始后面都是）regardsDR.Alekhya

Hope this answers your query（从这里开始后面都是）Regards,Dr.Alekhya

Awaiting your reply（从这里开始后面都是）Regards 

增加删除9：

```
[r'([A-Za-z])((?:[Rr][Ee][Gg][Aa][Rr][Dd][Ss]).{0,30})(\n|$)',r'\1.删除9:<u>\2</u>\3']
```