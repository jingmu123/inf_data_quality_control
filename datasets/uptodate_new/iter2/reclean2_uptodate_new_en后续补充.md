reclean2_uptodate_new_en后续补充

```
修改正则，满足既能匹配到( figure 2 )的情况又能匹配到( ( figure 2 ), panels A and C)的情况
[r'(\([^\(\)]{1,50}){1,}([fF]igure|NCT|Grade|[pP]icture|FIGURE|PICTURE|[iI]mage|[tT]able)\s([^\(\)]{1,50}\)){1,}','']
两个新情况 固定形式
[r'^\s?(Please read the Disclaimer at the end of this page|Links to society and government-sponsored guidelines|Beyond the Basics topics).*',''],
[r'\([^\(\)]{1,50}(waveform|movie|calculator)[^\(\)]{1,50}\)','']

```

对于step3的部分删除做了改动，之前的方式，匹配到某几段无关文本后获取他们的index采取了截断的方法，这样会导致如果下文仍然匹配到了几段无关文本，上一步的截断导致index被更新，那么此时的索引对应的是错误位置，会导致错误删除，无关文本却还存在，换用了new_context[i] = ''用空来代替，另外又补充了新的无关文本的匹配方法，由于出现特殊情况

例：

```
if re.search(r'^(SOCIETY GUIDELINE LINKS)',item.strip()):
    guidelines += 1
    guidelines_index.append(index)
if re.search(r'^.{,5}(Basics topics|Beyond the Basics topics)', item.strip()):
    guidelines -= 1
    guidelines_index.append(index)
```

在这里有些文章我应该用Basics topics作为截至的特征，有些是Beyond the Basics topics，还有特殊的情况两个都存在那么我就应该拿到最后一个加入guidelines_index的index作为截至的索引

```
def step3_reference(self, context):
    new_context = []
    references_started = False   #定义一个删除reference的开关  只要出现固定格式的表述就对后面的内容进行删除
    introduce = 0
    introduce_index = []
    Inc = 0
    Inc_index = []

    guidelines = 0
    guidelines_index = []
    for index, item in enumerate(context):
        if re.search(r'^(References|参考文献|见参考文献|致谢|REFERENCES|ACKNOWLEDGMENT|The following organizations also provide reliable health information|More on this topic|Topic[^\.]*Version|For country code abbreviations|ACKNOWLEGMENT)', item.strip()):
            references_started = True
        if references_started:
            item = ""

        if re.search(r'^2024© UpToDate, Inc', item.strip()):
            Inc += 1
            Inc_index.append(index)
        if re.search(r'ALERT: ', item.strip()):
            Inc -= 1
            Inc_index.append(index)

        # 要删除从Author到引言 设定了两个条件在循环时同时出现Author和引言，记下index，对相应的index进行删除
        if re.search(r'^(Author)', item.strip()):
            introduce += 1
            introduce_index.append(index)
        if re.search(r'^(引言|简介)', item.strip()) or re.search(r'^INTRODUCTION', item.strip()) or re.search(r'^Please read the Disclaimer at the end of this page',item.strip()):
            introduce -= 1
            introduce_index.append(index)

        if re.search(r'^(SOCIETY GUIDELINE LINKS)',item.strip()):
            guidelines += 1
            guidelines_index.append(index)
        if re.search(r'^INFORMATION FOR PATIENT',item.strip()) and guidelines == 0:
            guidelines += 1
            guidelines_index.append(index)
        if re.search(r'^.{,5}(Basics topics|Beyond the Basics topics)', item.strip()):
            guidelines -= 1
            guidelines_index.append(index)

        new_context.append(item)

        if introduce <= 0 and len(introduce_index) >= 2:
            start_index = introduce_index[0]
            end_index = introduce_index[-1]
            # 循环遍历需要替换的片段
            for i in range(start_index, end_index + 1):
                # 将当前索引处的字符替换为你想要的字符，这里以空字符为例
                new_context[i] = ''


        if Inc <= 0 and len(Inc_index) >= 2:
            start_index = Inc_index[0]
            end_index = Inc_index[-1]
            # 循环遍历需要替换的片段
            for i in range(start_index, end_index + 1):
                # 将当前索引处的字符替换为你想要的字符，这里以空字符为例
                new_context[i] = ''



        if guidelines <= 0 and len(guidelines_index) >= 2:
            start_index = guidelines_index[0]
            end_index = guidelines_index[-1]
            # 循环遍历需要替换的片段
            for i in range(start_index, end_index + 1):
                # 将当前索引处的字符替换为你想要的字符，这里以空字符为例
                new_context[i] = ''
    return new_context
```

```
添加两种情况出现直接删除之后的内容  都存在于段尾  
Topic[^\.]*Version|For country code abbreviations

针对删除出现次数较多从SOCIETY GUIDELINE LINKS -》(Basics topics|Beyond the Basics topics)的固定形式
if re.search(r'^(SOCIETY GUIDELINE LINKS)',item.strip()):
    guidelines += 1
    guidelines_index.append(index)
if re.search(r'^.{,5}(Basics topics|Beyond the Basics topics)', item.strip()):
    guidelines -= 1
    guidelines_index.append(index)
 
```








