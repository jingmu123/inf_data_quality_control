## 1.格式规范性	
### a. 缺少换行  补充
- 中文 数字. ---》中文 换行数字.  
- [r'。 +(\d{1,2}\.)', r'\n\1'] ----> [r'[。\u4e00-\u9fa5] *(\d{1,2}\.)', r'\n\1']


### b. 多余换行
- case1：识别每一行时，不知是什么逻辑合成full_blocks，造成的行内多于换行
- case2：ocr识别时页面过长，直接将正文分为两个full_blocks，导致多余换行。
- 两个汉字之间有换行-----------> 需要在正则替换前后都跑一遍！
```
text = re.sub(r'(^[^#\d\n\(（一二三四五六七八九十].*?[\u4e00-\u9fa5])( *\n{1,} *)([\u4e00-\u9fa5])', r'\1\3', item["text"], flags=re.MULTILINE) 
```

## 2.文本干净度
### 2.1 无关文本
- a. 加入判定侧栏、图注，并进行删除。
- b. 由漏识别一行导致的无关文本：5d7b48d7-9b3f-4898-ac0f-a633ae2b4a23
- c. 句末   __    添加  。__\s  ♥ 


## 3.信息有用性
3.1 替换step4的人名检测模型以及检测逻辑，去除单个姓氏(名字只有一个字)的误识别与对一个名字的重复识别：
（7.24 增加机构的识别来辅助判断参考文献，例如：中国工程院士中国医学科学院北京协科医学院北京协和医院妇产科主任、教校中华医学会妇产科学分会主任委员 《中华妇产科条志》总编辑中国医师协会妇产科医师分会会长）
```
    def get_person_idx(context):
    name_list,ORG_list = [],[]
    if len(context) > 500:
        context_part = context.split('。')
        for part in context_part:
            if len(part) > 512:
                div, remain = len(part) // 400, len(part) % 400
                if remain != 0:
                    div += 1
                count = len(part) // div
                start = 0
                for i in range(div):
                    part_piece = part[start:count]
                    context_part.append(part_piece)
                    start = count
                    count += count
                context_part.remove(part)

    else:
        context_part = [context]
    for part in context_part:
        if len(part) == 0 or len(part) > 512:
            continue
        result = ner_pipeline(part)
        result = result['output']
        print(1,result)
        for answer in result:
            if answer['type'] == 'PER':
                if len(answer['span']) > 1 and answer['span'] not in name_list:
                    name_list.append(answer['span'])
            elif answer['type'] == 'ORG':
                ORG_list.append(answer['span'])
    print(ORG_list)
    print(name_list)
    return name_list,ORG_list

```

3.2 更改替换逻辑，并且添加分类模型辅助判断，当名字字符与机构字符的长度占整段30%以上时删除、当人名超2个就交给分类模型分类，当识别为文献且置信度到0.7以上就删除：

```
if name_lens / len(context) > 0.3:
                return "参考删除-1:<u>{}</u>".format(context_raw)

            if name_num > 2:  # 超2个人名
                hypothesis_template = "The type of this text is {}"
                classes_verbalized = ["Text content", "reference"]
                output = self.zeroshot_classifier(context_raw, classes_verbalized, hypothesis_template=hypothesis_template,multi_label=False)
                if output["labels"][0] == 'reference' and output['scores'][0] > 0.7:
                    return "参考删除-2:<u>{}</u>".format(context_raw)

```

## 4.语义有效性
### 4.1栏目混乱
添加后续再次判断单列多列的情况，应对识别序号为单个full_block的情况。多一次判断有无同行的文本，当之前逻辑识别结果为多列时，去查看文本的同行情况，遍历到每一对同行时会去除同行的部分文本是序号的例子，最终计算出有几对同行，当最终对数高于第二长列的一半时，判断为确实为多列。

```
origin_lis.sort(key=lambda x: x[1])
    for index, single in enumerate(origin_lis):
        if index == 0:
            height_lis.append([single[-1]])
            temple_index = 0
            continue
        y_def = abs(origin_lis[temple_index][1] - origin_lis[index][1])
        sum_half_y = origin_lis[temple_index][3] / 2 + origin_lis[index][3] / 2
        if y_def < sum_half_y:
            height_lis[-1].append(single[-1])
        else:
            temple_index = index
            height_lis.append([single[-1]])
（判断有无同行的文本）

    count=0
    if len(locate_lis)>1:（当之前逻辑识别到多列时）
        for h in height_lis:
            if len(h)>1:
                print(h)
                for words in h:
                    word=words.replace('\n','')
                    word=word.replace('#','')
                    if len(word)<15:

                        print(word)
                        print(len(word))
                        count-=1
                        break
                count+=1
        len_lis=sorted([len(i) for i in locate_lis])
        min_num=len_lis[-2]
        print(count,(min_num/2))
        if count>=(min_num/2):
            print('多')
            pass
        else:
            print('单')
            locate_lis = [list(itertools.chain(*locate_lis))]
            index_lis = [list(itertools.chain(*index_lis))]

```