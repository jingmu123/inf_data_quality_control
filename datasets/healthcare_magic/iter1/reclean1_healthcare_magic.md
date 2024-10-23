reclean1_healthcare_magic

1.个例删除

例如：

(about like the 0 in this print)

**Question**: image attached 

 I hope you will find this useful Regards take care 

(If the answer has helped you, please indicate this)

David Dzsizan@gmail.com

类似这类的，只出现一次，没有什么共同特征，收集在个例里统一删除，增加个例删除：

```
(\(about like the 0 in this print\)|\(If the answer has helped you, please indicate this\)|\**Question\**: image attached *| *I hope you will find this useful Regards take care *|Wathch the video and read the pdf file.*|David Dzsizan@gmail.com *|RegardsBinu)
```

2.特殊符号删除

例如：

:-(

:)

这是笑脸和哭脸，不是正常文本用到的符号

增加符号删除：

```
((?:\:\-\()|(?:\:\)))
```

3.祝福词+某人类 的删除

例如：

.....feel free to ask me again.（从这里开始）Kind regards,Dr. Iliri

.....at all.Get well soon.（从这里开始）Best,Dr.Praveen

.....that could predispose to fungal infections. （从这里开始）Yours truly, Dr Brenes-Salazar MD Mayo Clinic MN 

......can assist you further. （从这里开始）Take care Regards, Dr. Ilir Sharka, Cardiologist 

有单独出现祝福词或人名的情况，祝福词类型很多，收集在一起删除，如果还有类似的再继续补充，增加删除1：

```
([\.!\?])( *(?:Kind [Rr]egards|(?:Take care )?[Rr]egards[\.!]?|[Dd][Rr]|Best wishes|(?:Take Care\.)?Best|Yours truly,|Thanks(?: and regards.)?|Best of luck\.|(?: Wishing you )?[Aa]ll the best!?|Take care\.|Thank you|Cheers & Godspeed!)(?:[ ,.&]*[A-Z][^\n ]*)* ?)(\n|$)
```

4.链接类型1删除

例如：

you can ask a direct question to me on this forum, following the below link.http://www.healthcaremagic.com/doctors/dr-rahul-kumar/64818Wishing you a good health.Thank you 

这类链接的前后话也是无关文本，增加删除2：

```
(you can ask a direct question to me on this forum, following the below link.*)
```

5.邮箱联系类的删除

例如：

 Reply may be sent to my email YYYY@YYYY Thanks 

You can mail me the photos to YYYY@YYYY with subject:ATTN Dr Sudarshan. Please do confirm the sending of the photos by writing here, so that I can reply you back at the earliest. Hope you have got answer to your query. Anticipating your response. Regards, 

增加删除3：

```
([\.!\?])([^\n.]*YYYY@YYYY.*)
```

6.句末无关文本的删除

例如：

......it hurts. what is this?（从这里开始） j 

What might it be?（从这里开始） Randi Ginder 

......physician for further management.（从这里开始） thanks dr.dhara dhara.shah84@yahoo.in 

增加删除4：

```
([\.!\?])( *(?:Please suggest|, take care|[A-Za-z]|Randi Ginder|thanks dr.dhara dhara.shah84@yahoo\.in) *)(\n|$)
```

7.句末无关文本+缺少标点

例如:

 consult your cardiologist and modify the BP medicine （从这里开始）, take care 

 Hope this information helpful to you（从这里开始）, take care and have a nice day.Regards - Dr KK ( Karade )

You can use other depigmenting agents with consultation of dermatologist（从这里开始）, Take care. muktangan@gmail.com 

特征是在逗号后面有 take care 字样，到结尾都是无关文本，并且需要补上一个英文逗号

增加删除5：

```
([,，] *(?:[Tt]ake care).{1,50})(\n|$)
```

8.感谢使用/给答案打分 类的删除

例如：

**Answer**: Brief Answer:Thank you using HCMDetailed Answer: Hi and thank you using HCM. Wish you a good day too and fast recovery. Dr.Klerida （整句都是感谢使用xxx）

**Answer**: Brief Answer:Please rate the answer.Detailed Answer:Hi.If your query is resolved please give a five star rating and write a positive review as a token of appreciation.Regards. （整句都是给xxx评分）

增加删除6：

```
(\*\*Answer\*\*: Brief Answer: *(?:Thank you using|Please rate).*)
```

9.链接类型2删除

例如：

Regards With Best Wishes:Dr Anil GroverMBBS, MD (Medicine) DM(Cardiology)Cardiologist and Internisthttp:/ WWW.WWWW.WW

特征是在祝福词+人名后面的增加一个不完全的网址，例如：http:/ WWW.WWWW.WW

因为小细节上与第一类删除不一样，所以单独拿出来删除，增加删除7：

```
([\.!\?])( *(?:With Best Wishes|Dr|Regards)(?:[ ,.&]*(?:[A-Za-z]|\([^\n\(\)]*\))[^\n ]*)* ?http:\/+(?:www\/)?(?:[ \.]+W+)+ *)(\n|$)
```

10.链接类型3删除

例如：

**Answer**: Brief Answer:Pleasure :) Detailed Answer:Happy I could help. （从这里开始）Regards Dr Priyank Mody, Lilavati Hospital, XXXXXXX For any further assistance you may directly axcess me through HCM @Http://doctor.healthcaremagic.com/doctors/dr-priyank-mody/70273

这类链接前面也会跟着描述和无关文本，增加删除8：

```
([\.!\?])([^\n.]*)((?:Https?[：:][/／]{2}(?:www[.．])?|www[.．])[a-zA-Z0-9@／/-]+(?:[.．／/][a-zA-Z0-9@／/_\-]{2,})+.*)
```

