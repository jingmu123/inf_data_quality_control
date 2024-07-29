## gpt_reclean_2总结及新一轮的reclean1_guidelines_ly_gptpdf清洗

### 信息完整性

#### 1.信息有用性-图片的描述信息（问题较多，但是比较难解）

这里的图片描述信息和之前删除的图片描述信息不同，这里的图片描述信息中基本没有明显的特征，这就很难识别到，

例：信息有用性#3#3#图片描述内容
【3】TELE-COLLABORATORS hundreds of miles apart consider a computer-generated medical model, which both of them can manipulate as though it were a real object. The headpiece helps the computers locate the position and orientation of the user’s head; such positioning is essential for presenting the right view of a face. In the future,
 the headpiece should be unnecessary.

信息有用性#1#1#图片描述内容

【1】DISTURBANCES IN THE MAGNETOSPHERE occur when the interplanetary magnetic field (IMF) carried by the solar wind turns southward. In a process called reconnection, the field lines of the IMF connect with the northward geomagnetic field lines at the dayside of the magnetopause 删除11:(1). Energy and particles from the solar wind rush into the magnetosphere, enlarging its northern and southern lobes and narrowing the plasma sheet. Then the geomagnetic field lines themselves reconnect 删除11:(2), accelerating ions and electrons toward the earth.

#### 2.信息有用性-侧栏内容（性质和1相同，比较难解）

目前侧栏内容已经和正文融合在一块了，也没有块信息，侧栏信息已经很难识别出来了

#### 3.信息不完整（先不管）

本页的前面或者后面缺少一段正文，这可能是由于在识别前一页的时候将本页前面的部分识别到前面页去了，后面缺少的正文也可能是被后面页识别走了，这个问题在之前就出现过

#### 4.信息有用性-目录信息（正在解）

### 语义有效性

#### 1.栏目混乱（暂时无解）

### 文本干净度

#### 1.页眉页脚（正在解）

#### 2.无关文本-文本中没有的内容疑似ai自己补充（先不管）

#### 3.特殊格式的数字引用





## 解决

### 信息完整性

##### 1.信息有用性-图片的描述信息（单段）

可使用[A-Z]{5,}\*\*[\s\n]{0,5}[a-z]找出来解决一小部分

#### 4.信息有用性-目录信息

新加入step4_is_mulupage的方法，此方法加入了锦恭之前调研的模型来区分正文和目录，和一些目录的特征，模型的准确率不高，难判断出来且运行特别慢，目前只用特征来判断，后续考虑在分类模型中添加目录样本重新训练可能效率比此模型高

```
def step4_is_mulupage(self,duans):
    """
    目录页的特点:
    1.文章前几页
    2.可能存在多个\.的情况(参考文献处理中已经把\.多的页给删掉了)
    3.循环context，item长度短数量多
    :param context: 文本信息
    :param page_num: 页码
    :return: context
    """
    # 对文本进行分类判断
    hypothesis_template = "The format of this text belongs to {}"
    classes_verbalized = ["Text content", "catalogue"]

    short_item_num = 0
    lines_num = 0
    catalogue1_num = 0
    catalogue2_num = 0
    for item in duans:
        if len(item.strip()) <= 200:
            short_item_num += 1
        lines = re.split(r"\n", item.strip())
        for line in lines:
            lines_num+=1
            if re.search('\.{8,10}',line) or re.search('^([-·]|[\d\.\s]{1,10})',line.strip()):
                catalogue1_num += 1

            if zeroshot_classifier(line,classes_verbalized,hypothesis_template=hypothesis_template,multi_label=False)["labels"][0] == "catalogue":
                catalogue2_num += 1

    print(catalogue1_num,catalogue2_num,lines_num)
    if short_item_num > len(duans) * 0.7 or catalogue1_num > lines_num * 0.5:
        duans.insert(0, "(本页删除)本页使用特征判断为目录页")
    if catalogue2_num > lines_num * 0.5:
        duans.insert(0, "(本页删除)本页使用模型判断为目录页")
    return duans
```

### 文本干净度

#### 1.页眉页脚

在解决页眉页脚问题上，调研了几个模型，但是没什么效果，都要去再用数据训练，否则都不准，目前还是利用当前的ngram模型打分判断

```
def step2_is_pagefoot(self, duans):
    # duans是一个列表，取第一段和最后一段进行if判断，判断页眉页脚

    first_line = duans[0]
    if re.search("】",duans[-1]):
        last_paragraph = duans[-1].split("】")[1]
    else:
        last_paragraph = duans[-1]
    # 提取中间段落
    middle_duans = duans[1:-1]
    middle_content = " ".join(middle_duans)
    middle_content = re.sub(r"【\d+】",r'',middle_content)
    first_line_score = self.get_score(first_line)
    last_paragraph_score = self.get_score(last_paragraph)
    middle_content_score = self.get_score(middle_content)
    print(first_line_score,first_line)
    print(middle_content_score,middle_content)
    print(last_paragraph_score,last_paragraph)
    if first_line_score > 4000 and not re.search('\|',first_line):
        duans[0] = "疑似页眉" + duans[0]
    elif first_line_score > 8000 and not re.search("#",first_line) and not re.search('\|',first_line):
        duans[0] = "疑似页眉" + duans[0]

    if last_paragraph_score > 3500:
        duans[-1] = "疑似页脚" + duans[-1]
    return duans
```

#### 3.特殊格式的数字引用

新加特殊删除方式

```
[
    r'(\$\^\{\d+\}\$)',
    r'删除22:<u>\1</u>'
],
[
    r'(<sup>\d+</sup>)',
    r'删除23:<u>\1</u>'
]
```



目前gpt中做了

step1:删除图片的描述

step2:页眉页脚的判断

step3_1:多于换行

step3_2:缺少换行

step4:目录页判断

step5:正则替换

step6:参考页判断

```
duans = sp.step1_delete_photo_describe(duans)
duans = sp.step2_is_pagefoot(duans)
duans = sp.step3_1_more_linefeed_duannei(duans)
duans = sp.step3_2_more_linefeed_duan(duans)
duans = sp.step4_is_mulupage(duans)
正则替换
text = sp.is_cankaopage(text, lang)
```