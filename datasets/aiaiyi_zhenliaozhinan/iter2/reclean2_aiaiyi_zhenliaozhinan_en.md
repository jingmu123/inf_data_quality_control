## reclean1B_aiaiyi_zhenliaozhinan_en

### 错误删除：
1.```[r'(([\(（][^\(\)（）]{0,50})([fF]igure|NCT|Grade|[pP]icture|FIGURE|PICTURE|[iI]mage|[tT]able) *([^\(\)（）]{0,50}[\)）]))', r'删除5:<u>\1</u>']```，错误删除了括号文本中带有table的长单词，例如（eg, coronary re vascular iz ation patients with unstable symptoms）。
修改为：```[r'([\(（]([fF]igure|NCT|Grade|[pP]icture|FIGURE|PICTURE|[iI]mage|[tT]able|[Ss]ee|[Rr]efer) *([^\(\)（）]*[\)）]))', r'删除5:<u>\1</u>']```。



### 无关文本：
1.网址，带括号，如(www.acc.org)。

补充正则：```[r'([\(（]?\**[  ]*(https?:\/\/)?(www\.)?([\da-z\.\-@]+)\.([a-z]{2,6})([\/\w\?=\.-]+)?\/?[\)）]?)', r'删除2:<u>\1</u>']```。

2.参考补充(J Clin Endocrinol Metab 2013 Nov;98(11):4227-49)类似情况。

补充正则：```[r'(\\*[\(\[（][^\(\)\[\]（）]*(\set[\s\xa0]{1,3}al|\d+(\(\d+\))?[:：] *\w+([\-\.]\d+)?|ICD)[^\(\)\[\]（）\n]*[\)\]）]?)', r'删除5:<u>\1</u>']```。

**0813补充：**

3.下载提示误删，当文本结尾没有标点且下载提示在同一行时，会将整行文本误删。

补充修改为两个正则：```[r'(\*+点击下载[^\n]+)', r'删除0:<u>\1</u>'],
[r'([^\n\.。？]*[\*\\]*(完整版?下载|下载地?址?：|相关专题链接：|点击查看原文：|\*[  ]*下载)[^\n]+)', r'删除1:<u>\1</u>']```。

4.补充（see ....）、（Refer）等情况。

补充正则：```[r'([\(（]([fF]igure|NCT|Grade|[pP]icture|FIGURE|PICTURE|[iI]mage|[tT]able|[Ss]ee|[Rr]efer) *([^\(\)（）]*[\)）]))', r'删除5:<u>\1</u>']```。

5.文本中人名文献，如J Am Coll Cardiol 2006;48:e247-e346.、Pediatrics 2011;127:994–1006等。

正则删除：```[r'([^。\.\n]+\d{4}[;；]\w+[:：]\w+[^\nA-Z]+)', r'删除8:<u>\1</u>']```。


**0814补充：**

6.人名成员，（D.B. Sacks, D.E. Bruns）

正则删除：```[r'([\(（] *([A-Z]\.)+[^\(\)（）]+[\)）])', r'删除9:<u>\1</u>']```。
考虑整段删除。

7.无关文本特定删除：
```[r'(See pages 31–33 for the updated information\.|See Table 1\.|\*\*《2014BSG Barrett食管诊断和治疗指南》\*\*|as summarized in Table1\.)', r'删除11:<u>\1</u>']```，
```[r'((Professor Alan B\.R\.)[\w\W]*?(\n\n))', r'删除10:<u>\1</u>']```。

8.详见附录，Full details are given in Appendix 1.、this guideline can be found in Appendix I.等。

正则删除：```[r'([^\n\.。？\?]+Appendix[^\n\.。？\?]+?\.)', r'删除12:<u>\1</u>']```。

9.补充(Appendix 1)，（Dr ...）附录。

补充：```[r'([\(（]([fF]ig|NCT|Grade|[pP]icture|FIGURE|PICTURE|[iI]mage|[tT]able|[Ss]ee|[Rr]efer|Appendix|Dr|NICE) *([^\(\)（）]*[\)）]))', r'删除5:<u>\1</u>']```。

10.下载提示误删修改后，会遗漏点击下载，第一个不打标签直接替换空，第二个正则补充上。

修改正则：```[r'(\*+点击下载[^\n]+)', r'']```,
```[r'([^\n\.。？]*[\*\\]*(点击下载|完整版?下载|下载地?址?：|相关专题链接：|点击查看原文：|\*[  ]*下载)[^\n]+)', r'删除1:<u>\1</u>']```。

11.人物介绍，网站介绍等整段无关文本。
```
def step6_unrelated_text(self, context):
    split_token = "\n"
    result = []
    context = context.split(split_token)
    patter1 = r'(( *[A-Z][a-z]?\.)+ ?[A-Za-z]{,20})'
    patter2 = r'([\(（]?\**[  ]*(https?:\/\/)?(www\.)?([\da-z\.\-@]+)\.([a-z]{2,6})([\/\w\?=\.-]+)?\/?[\)）]?)'
    for item in context:
        if len(re.findall(patter1, item)) > 4 or len(re.findall(patter1, item)) > 1 and len(item) < 200:
            item = "(此段删除)无关文本-1：" + item

        if len(re.findall(patter2, item)) > 2:
            item = "(此段删除)无关文本-2：" + item
        result.append(item)
    context = split_token.join(result)
    return context
```
此函数正在测试优化。

10.优化网址误删，将网址、电话、邮箱成员介绍等正则加入判断，判断是否整段删除。
```
def step6_unrelated_text(self, context):
    split_token = "\n"
    result = []
    context = context.split(split_token)
    patter1 = r'([^A-Za-z]([A-Z][a-z]?\.)+ ?[A-Za-z]{,20})'
    patter2 = r'([\(（]\**[  ]*(https?:\/\/)?(www\.)?([\da-z \.\-@]+)\.([a-z]{2,6})([\/\w\?=\.-]+)?\/?[\)）]|\**[  ]*(https?:\/\/)?(www\.)?([\da-z \.\-@]+)\.([a-z]{2,6})([\/\w\?=\.-]+)?\/?)'
    patter3 = r'(MD|Professor)'
    patter4 = r'(Fax|mail|calling)'
    for item in context:
        if len(re.findall(patter1, item)) > 4 or len(re.findall(patter3, item)) > 4 or (len(re.findall(patter3, item)) > 2 and len(item) < 500):
            item = "(此段删除)无关文本-1：" + item
        website_list = re.findall(patter2, item)
        # print(website_list)
        if len(website_list) > 2 or len(re.findall(patter4, item)) > 2:
            item = "(此段删除)无关文本-2：" + item
        for web in website_list:
            if len(re.findall(r'\.', web[0])) >= 2:
                item = re.sub(re.escape(web[0]), rf'删除2:<u>{web[0]}</u>',item)
        result.append(item)
    context = split_token.join(result)
    return context
```

### 缺少换行：
1.为了减少step6_unrelated_text误删，将内容简介和内容预览之间的缺少换行补充。

正则补充：```[r'([\.。？\?][  ]*)((\*\*)?(《[^《》]+》)(内容预览))', r'\1\n增加换行:\2']```。

