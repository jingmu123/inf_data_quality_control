reclean4总结

## 缺少换行逻辑修改

```
def step5_lack_linefeed(self,context):
    new_context = []
    for item in context:
        # 查找 #•，并在其前后加换行符
        # parts = re.split(r'(?<=\s)([#•]{1,3}\s?[A-Z][^#•]*)', item)
        splitchar = r'([#•]{1,3}\s)'
        parts = re.split(splitchar, item)
        new_parts = []
        for part in parts:
            if part.strip() in ["#","•"]:
                new_parts.append(part.strip())
            else:
                new_parts.append(part.strip()+'\n')

        item = "".join(parts)
        new_context.append(item)

    return new_context
```

未解决的换行问题

带有序号缺少换行

例：3.Anterior open bites derived from finger sucking habits usually do not need to be treated because there is a spontaneous correction after the habit is abandoned, especially if it ceases before the patient reaches three years of age. 删除1:(5) 4. The attitude of the child: the child must always be part of the decision-making process, this way the child will not consider the intervention as a punishment.



## 多余换行

补充段落中只有序号且下一段是大写开头的情况进行连接

## 信息有用性

- 书籍的最前或最后几页，不含参考文献信息，但是也是无关内容（例如书籍的介绍，出版信息等），无明显信息

## 无关文本

处理没有参考文献的特征但是有很多名字存在的情况，也将它看做参看文献

```
# 如果名字的总长度>=句长的0.5且名字的个数>=3 或 段中名字的个数>=5
elif (total_len >= len(item)*0.5 and person_num >= 3) or person_num >= 5:
    return True
```



step1侧栏的删除会误删正文不合适，要删掉

例：'seq_id': 'df7b3bd2-6031-457a-803d-70bb78568153'











## 多余换行逻辑添加



介词相连  已完成







reclean4总结

## 序号不一致的问题

- 序号识别出来丢失了，缺少序号
- 序号位置识别错误（例如：序号应该在句首但是识别出来没在句首）
- 识别错误，例如把1识别成了l （可解决）

```
context = re.sub("l[\.,]" , '1.' ,context)
```

## 无关文本问题未解决

- 侧栏里的内容  要解决侧栏问题



## 缺少换行问题

- 如果有存在[。？！...] 后面是小写的情况换行  （已解决）

- 没什么特征但是在原pdf中不是同一段   例：这里标注的 缺少换行#0#0#In conclusion, post–cardiac arrest……  没有什么特征去在这里添加一个换行    （较难解决）

  ```
  Other ventilatory parameters may affect the outcome of patients on mechanical ventilation after cardiac arrest, particularly when acute lung injury or ARDS develops. Over the last decade attention has focused on low-volume/high-rate ventilation. In a comparison of high- and low-tidal-volume ventilation, the death rate of patients with ARDS was reduced from 40% to 31% in the group with reduced tidal volume (V T ).删除3: 106 This and subsequent studies recommend ventilating patients to maintain V T of 6 to 8 mL/kg predicted body weight and inspiratory plateau pressure ≤ 30 cm H 2 O to reduce ventilator-associated lung injury.删除3: 107 Because low V T ventilation (6 mL/kg) is associated with an increased incidence of atelectasis, PEEP and other lung “recruitment maneuver” procedures may be warranted.删除3: 108 However, one study reported no difference in the rate of discharge or survival between ARDS patients receiving high- or low- PEEP regimens.删除3: 109 Furthermore, a recent historical comparison of ventilation practice after cardiac arrest reported no differences in pneumonia, oxygenation, lung compliance, and ventilator days when a low V T strategy versus a more liberal “old practice” V T was applied.删除3: 110 In conclusion, post–cardiac arrest patients are at risk of acute lung injury and ARDS, but refractory hypoxemia is not a frequent mode of death after cardiac arrest. There is no reason to recommend hyperventilation and “permissive hypercapnia” (hypoventilation) for these patients, and normocapnia should be considered the standard. There is also no data to recommend unique ventilation strategies in this population different from usual care of other mechanically ventilated patients at risk for acute lung injury and ARDS.
  ```

- 有序号类似于·的情况（此情况标注较多，可解决）

缺少换行这里补充两种情况

```
elif re.search(r'([\.\)])(\s\d{1,2}\.\s?[A-Z])',part):
    part = re.sub(r'([\.\)])(\s\d{1,2}\.\s?[A-Z])',r'\1\n\2',part)
    new_parts.append(part.strip() + '\n')

elif re.search(r'([\.?!]\s?)([a-z])',part):
    # 在句末标点符号（。？！...）后面接小写字母的情况进行换行
    part = re.sub(r'([\.?!]\s?)([a-z])', r'\1\n\2', part)
    new_parts.append(part.strip() + '\n')
```

## 代码目前存在的问题

- 需要调短段落所占的比例

- 错误删除的校正

- 之前的step1除不掉页眉页脚，需要将用块判定页眉页脚的方法加进来（已解决目前通过某个例子中是将页脚成功删掉）

  

reclean5分析

## 代码存在的问题

参考删除1，0.3可能太小有误删

删除图片正则是删除整段，但是整段里面除了对图片的描述还可能有正文

## 无关文本

- 还有数字引用未删除，添加新规则 （已解决部分）

  不能解决的情况

  例如，下面这句话中的121不能把前面的逗号和后面的小写作为特征，因为这种情况是合理的

  To give the victim the best chance of survival, 3 actions must occur within the first moments of a cardiac arrest 删除7:<u>120</u> : activation of the EMS system, 121 provision of CPR, and operation of a defibrillator.

  添加

  ```
  # 上一句的句号\d中间没有点[大写]，这里的\d后面没有点不是序号可能是上一句的引用数字
  [r'([^\d][\.,])((\s{1,3}\d+[\s\n]{1,3}){1,5}\.?)(\s?[A-Z])',r'\1删除6:<u>\2</u>\4'],
  # 介词前面有数字会有问题
  [r'((\d+[\.,]?){1,5})(\s(and|or|the|:)\s)',r'删除7:<u>\1</u>\3'],
  # 结尾句号后面为数字和序号区别开序号后面还有一个.
  [r'\.(\s?\d+)\n',r'删除8:<u>\1</u>'],
  [r'(#{1,3})\n',r'\1']
  ```



- 如果是图片页，使用看盒子的大小占整页的比例来决定他是不是只是一小块内容     （有点问题，存在有一页pdf大部分为图片，只有很少的内容，但是这部分少的内容还是正文，不能被删还需要优化）

1.在step1去掉页边角后面添加

2.一个大块为一段，大块数量小于等于3

3.求面积，(右-左)*(下-上)     /    整页的面积 

4.设定某个阈值，有内容的面积小于阈值加上标签这一页的内容部分所占的比例小于阈值

```
def delete_photopage(self,item):
    raw_info = item['attr']['raw_info']
    img_box = item['attr']['img_box']
    img_area = (img_box[2] - img_box[0])*(img_box[3] - img_box[1])
    all_block_area = []
    for raw in raw_info:
        full_blocks = raw['full_blocks']
        block_area = ([full_blocks][2]-full_blocks[0])*(full_blocks[3]-full_blocks[1])
        all_block_area.append(block_area)

    if len(raw_info) <= 3 and all_block_area / img_area < 0.4:
        item['text'] = "(本页删除)此页的内容部分所占的比例小于0.4"+item['text']

    return item
```

- 参考文献加入条件关于一些电话号的描述（已解决）



- \#American Heart
   Association
   Learn And Live,













## 多于换行问题分析

- 之前的代码换行这里使用的韩瑞的代码，代码中有一个条件.*[a-z0-9-,:"]$，我在重新写多于换行的时候没有加此类情况，但是他有不合理的地方,下面例子中加粗的地方是一个标题的特征，但是在这里这句话不是标题只是一行正文内容，

  ```
  elif "#" not in nums[slow] and "*" not in nums[slow] and re.match(r'.*[a-z0-9-,:"]$', nums[slow]) and (
          re.match(r'^[a-z-,]', nums[fast])):
  ```

​	例：

​	Despite these setbacks, Stanley did find two useful tape databases at the National\nArchives that had been listed in the Rand index: the Combat Activities File had details about missions flown in Southeast\nAsia from October 1965 through Decembase documented missions flown between删除换行January 1970 and August 1975. These intact databases were created on IBM System 360 and System 370 mainframe computers using software called the National\n**Military Command System Information**\nProcessing System 360 Formatted File System, or NIPS. Developed for the government by IBM in the 1960s, NIPS did what database software does: it created, structured, maintained and revised data files.\





- 符合正确的特征的阅读特征

  例：In 1973, the AHA first endorsed training of the lay public in CPR.删除6:<u> 82 </u>Subsequently, Advanced Cardiac\nLife Support (ACLS) was introduced in 删除2:<u>1974,83.84</u> followed by Pediatric Advanced Life Support (PALS) in 删除2:<u>1988.85</u>

​	 Advanced Cardiac\nLife Support   这种情况符合前面是标题后面是正文开头的特征

​	或者是两个句子本来同属于一段，但是中间有个换行，属于正常的文章特征。

​	例：Could that be why, several generations ago, asthmatics were often sent \"to the desert\" or \"to the mountains\" to gain a respite from their symptoms?\nWas the relocation no more than a move to an area free of dust mite allergen?

- 缺少考略的情况，重新整理多于换行的代码，又添加了集中情况 

  ```
      def step2_more_linefeed(self, context):
          # print("Before processing:", context)
          index = 0
          while index < len(context):
              item = context[index]
              # 定义一个介词列表
              preposition_list = ['of', 'in', 'and', 'or', 'not', 'the', 'a', 'any', 'for', 'is', 'The', 'A']
  
              # 将 item 按 "\n" 分割
              item_sections = re.split(r'\n', item)
              section_index = 0
  
              while section_index < len(item_sections) - 1:  # 确保不会越界
  
                  if re.search(r'\s\d+\.$', item_sections[section_index]):  # 匹配段落结尾是数字和句点
                      item_sections[section_index] += " 段内删除换行-1 " + item_sections[section_index + 1].lstrip()
                      del item_sections[section_index + 1]
  
                  elif re.search(r'^(\d+[\.,]){1,3}$', item_sections[section_index]) and \
                          item_sections[section_index + 1].lstrip()[0].isupper():  # 匹配段落中只有序号且下一段是大写开头的情况
                      item_sections[section_index] += " 段内删除换行-2 " + item_sections[section_index + 1].lstrip()
                      del item_sections[section_index + 1]
  
                  elif any(item_sections[section_index].rstrip().endswith(" " + prep) for prep in
                           preposition_list):  # 匹配同一段中介词结尾的
                      item_sections[section_index] += " 段内删除换行-3 " + item_sections[section_index + 1].lstrip()
                      del item_sections[section_index + 1]
  
                  elif item_sections[section_index].rstrip()[-1] in ['-']:
                      item_sections[section_index] += " 段内删除换行-4 " + item_sections[section_index + 1].lstrip()
                      del item_sections[section_index + 1]
  
                  elif "#" not in item_sections[section_index] and "*" not in item_sections[section_index] and re.search(
                          r'[^\.?!]$', item_sections[section_index]) and re.match(r'^[a-z]', item_sections[
                      section_index + 1].lstrip()):
                      item_sections[section_index] += " 段内删除换行-5 " + item_sections[section_index + 1].lstrip()
                      del item_sections[section_index + 1]
  
                  elif re.search(r'\([^\)]*$|\[[^\]]*$', item_sections[section_index]) and re.match(r'^[^\(\[]*[\)\]]',
                                                                                                    item_sections[
                                                                                                        section_index + 1]):  # 前一个段落有一个未对应的左括号，下一段前面有一个与之对应的右括号
                      item_sections[section_index] += " 段内删除换行-6 " + item_sections[section_index + 1].lstrip()
                      del item_sections[section_index + 1]
  
                  else:
                      section_index += 1  # 只有在不合并时才自增
  
              # 更新 item 以反映合并的段落
              item = '\n'.join(item_sections)
              context[index] = item
  
              # 合并以小写字母或特定标点符号开头的段落
              stripped_item = item.strip()
              # print(stripped_item)
              if index > 0:
                  if stripped_item and (
                          stripped_item[0].islower() or stripped_item[0] in ["(", "[", ")", "]", "."]):
                      # 合并到前一个 item
                      context[index - 1] = context[index - 1].rstrip() + " 整段删除换行-1 " + item.lstrip()
                      # 删除当前 item
                      del context[index]
                      # 继续检查当前索引位置的元素
                      index = index - 1
                      continue
  
                  # 新增条件: 如果 stripped_item 结尾的单词在 preposition_list 中
                  elif any(stripped_item.rstrip().endswith(" " + prep) for prep in preposition_list):
                      if index + 1 < len(context):
                          # 合并到下一个 item
                          context[index] = item.rstrip() + " 整段删除换行-2 " + context[index + 1].lstrip()
                          # 删除下一个 item
                          del context[index + 1]
                          # 不增加 index, 继续检查当前索引位置的元素
                          index = index - 1
                          continue
  
                  elif stripped_item[-1] == '-':
                      if index + 1 < len(context):
                          # 合并到下一个 item
                          context[index] = item.rstrip() + " 整段删除换行-3 " + context[index + 1].lstrip()
                          # 删除下一个 item
                          del context[index + 1]
                          # 不增加 index, 继续检查当前索引位置的元素
                          index = index - 1
                          continue
  
                  elif "#" not in item and re.search(r'[^\.?!]$', item.strip()):
  
                      if index + 1 < len(context):
                          # 合并到下一个 item
                          context[index] = item.rstrip() + " 整段删除换行-4 " + context[index + 1].lstrip()
                          # 删除下一个 item
                          del context[index + 1]
                          # 不增加 index, 继续检查当前索引位置的元素
                          index = index-1
                          continue
  
              index += 1
          # print("After processing:", context)
          return context
  ```

## 无关文本问题分析

- 无关文本中大多数还是序号的问题，序号的问题不断地在补充，reclean5上传的时候把之前一条关于序号的正则给删掉了，也没有去补充新的

  

- 页眉页脚的问题，已经有新写的代码去解决



## 关于无关文本中的数字问题加入了复数判定的规则（测试一下好不好用）

#### 数字处理总结：

```
['million','mm','cm','m','km','mg','g','kg','billion','percent','ratio']
```

数字是  1:2 的形式不能删除

前面是 ><= 的不能删除

#### 换行处理总结：

整段换行-4  :结尾的不能换上来  （解决）

整段换行-1 如果当前段落有#证明为标题   不能将下一行换上来 （已解决）



段内   前面小写结尾，后面大写开头怎么半



#### 其他:

参考删除-2

## guidelines问题分析

```
# 带[]为guidelines写的
[r'([^\d])(\[\s?\d{1,4}(\s{0,3}[\-–—,\.]\s{0,3}\d{1,4}){0,20}\s?\])',r'\1'],
 # 给guidelines补充
[r'([^\d][\.,]\s?)(\d{1,4}(\s{0,3}[\-–,\.]\s{0,3}[1-9][0-9]{1,4}){1,20})(\n|\s?[A-Z])',r'\1\4'],
# 结尾句号后面为数字和序号区别开序号后面还有一个.
[r'([^\d]\.)(\s?[1-9][0-9]{1,4}(\s{0,3}[\-–,\.]\s{0,3}[1-9][0-9]{1,4}){0,20})(\n)',r'\1\4'],
```



![image-20240620153822655](C:\Users\Administrator\AppData\Roaming\Typora\typora-user-images\image-20240620153822655.png)

参考删除2只有个名字数量>5





```
et\u00A0al
```
