## reclean5_differential_diagnosis_book_en问题
1. 零碎段落删除补充，减少误删，补充不删除出现序号和：的段。
```
count = True if len(re.findall(r'[A-Za-z]', con)) <= 3 and re.search(r'[^A-Za-z]]', con) else False
if len(con) <= 15 and count and not re.search(r'[:：]|\d+\\?\.', con):
    context[i] = "零碎段删除-1:<u>{}</u>".format(context[i])
    # context[i] = ''
    continue
```

2. 因误删问题取消人名和索引段删除。


3. 段末无关数字补充，
...of depression. 8 , 9 , 10 , 11
...many years. 18 , 19
...strategies. 1 , 2等。
```
[r'([a-z]\.)( ?[\|\d]+([，, \.\-\|]+\d*)*$)', r'\1删除14:<u>\2</u>'], 
```

4.包含网址的无关段落，避免误删长文本，加上字符限定。并对原来的部门，人物学校介绍删除加长字符限定长度。
```
[r'((^(?=.{0,200}$).*(Department|University).*)|(^(?=.{0,400}$).*(Depa[ri]tment of|Tel：|@[a-z]{2,10}\.com|https?).*)|(^(?=.{0,600}$).*[Ff]rom.*(https?).*))', r'删除15:<u>\1</u>']
```


