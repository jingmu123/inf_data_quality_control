## reclean3_healthcare_magic

### 1.XXX科XXX医生的回复类的删除

例如：

**Answer**: （开始）Orthopaedic Surgeon,  Dr. Aashish Raghu's  Response （结束）It appears

**Answer**: （开始）Dentist,  Dr. Honey Arora's  Response （结束）Hi.Welcome to

增加删除10：

```
[r'([:：])( *(?:(?:[A-Z][A-Za-z，,\'’\.]+|&) +)+Response)',r'\1删除10:<u>\2</u>'],
```

### 2.邮箱类无关文本补充

例如：

try calcium in form of Calcium Citrate Maleate Take Tab. （从这里开始都是无关文本）Rockbon (Abbott) 1 tab daily for three months Dr. Manish R. Rijhwani +91-9422571734 drmanish78@gmail.com 

补充到删除3：

```
[r'([\.!\?])([^\n.]*(?:(?:[Dd ][Rr]\.)[^\n.]*)*(?:YYYY@YYYY|@gmail\.com).*)',r'\1删除3:<u>\2</u>'],
```



### 3.删除个例固定句式

例如：

 Thank you from HCM .
 Hi.Welcome to HEALTHCARE

  Hi.Welcome to HEALTHCARE MAGIC.

  Welcome to Healthcare Magic 

补充到删除个例：

```
[r'(\(about like the 0 in this print\)|\(If the answer has helped you, please indicate this\)|\**Question\**: image attached *| *I hope you will find this useful Regards take care *|Wathch the video and read the pdf file.*|David Dzsizan@gmail\.com *|RegardsBinu|Thank you for choosing HealthcareMagic\.|For a personalised comprehensive evaluation.*|[Tt](?:hank|HANK) (?:you|YOU) (?:from|FROM) (?:HCM|hcm) *\.?|(?:[Hh]i[ \.]?|[Hh]ello[ \.]?)?Welcome to (?:Healthcare|HEALTHCARE)(?: Magic *\.?| MAGIC *\.?)?)',r'删除个例:<u>\1</u>'],
```



### 4.祝福词+人名补充

例如：

s i have mentioned.  Thanks in advance, Arshad

urther query.RegardsBest of luckThanks

 upload reports? Many thanks XXXXXXX 

please. Best regards, Dr. Neelam.

补充了祝福词的内容，补充到删除1：

```
[r'([\.!\?])( *(?:Kind [Rr]egards|(?:[Tt]ake [Cc]are |[Ww]ith |[B]est )?[Rr][Ee][Gg][Aa][Rr][Dd][Ss] *[\.!,]?(?: *[Dd][Rr])?|[Dd][Rr]|Best wishes|(?:Take Care\.)?Best|Yours truly|Truly yours|Hennie|Kim|Cindy|Sandi Brown|Aisha|(?:Many *)?[Tt]hanks!?(?: and [Rr]egards[\.,]?)?|Best of luck|[Tt]ake care[\.!]?|Thank you(?: *[Dd][Rr])?|Cheers & Godspeed!|X{3,}|(?:[Ww]ish(?:ing)?(?: you| him)?)? *(?:(?:good)? health|[Aa]ll the best|a nice weekend)!?(?: *[Dd][Rr])?|"?[Ww]ith.{1,20}wishes[",]?Dr|(?:[Oo][Kk])? *than(?:Q|l?k u)|Get well soon|Thanks in advance)+(?:[ .&\-,]+[A-Z][^\n ]*)* *(?:\([^\(\)\n]+\))? ?)(\n|$)',r'\1删除1:<u>\2</u>\3'],
```