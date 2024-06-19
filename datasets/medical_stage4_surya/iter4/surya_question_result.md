## 无关文本

### 参考文献

加入nlp模型之后结合之前写的参考文献的正则，可以对整页的参考文献进行识别

```
def step5_1_removepage(self, context):
    # context 是一个列表，每个 item 是一段内容
    context_lens = len(context)
    # 用于统计有多少个段落中出现了人名
    num = 0
    for item in context:
        person_num, names_start2stop = NIL_tool(nlp,item)

        # 判断句子中人名占句子总体比例来判断句子是否为参考文献
        if step5_2_isreference(item,person_num,names_start2stop):
            item = f'删除参考文献:<u>{item}</u>'

        if re.search(r'删除参考文献',item) and person_num >= 1:
            # 如果当前段落中有人名且符合参考文献的特征
            num += 1
    if num >= context_lens * 0.5:
        context.insert(0, "本页在超过一半的段落中发现人名且符合参考文献的特征")
    return context
def step5_2_isreference(item,person_num,names_start2stop):
    len_item = len(item)
    len_names = 0
    for name in names_start2stop:
        len_name = name[1] - name[0]
        # 求出每个名字开头结尾的差值，拿到所有名字所占的总长度
        len_names += len_name
    # 如果一段话中名字的数量大于3且名字所占的长度大于总长度的30%认为是参考文献
    if person_num >= 3 and len_names > len_item * 0.3:
        return True
    return False
```



### 页内内容较少，考虑删除（四种情况，多短、多长、少短、少长，多且长排除）【难处理，段落长度的选择上可能有问题】

- 段落少，段落长（段落数量小于3）

- 段落少，段落短

- 段落多，段落短

  少、短、少且短（有多短？）

  ```
  def step6_is_shortpage(self,context):
      duanluo_num = len(context)
      short_duanluo_num = 0
      if duanluo_num <= 3:
          for item in context:
              if len(item.strip()) < 100:
                  short_duanluo_num += 1
          if short_duanluo_num > 1:
              context.insert(0, "本页的段落数量小于等于3且至少段落长度有2条以上在100以下")
      elif duanluo_num <= 5:
          for item in context:
              if len(item.strip()) < 80:
                  short_duanluo_num += 1
          if short_duanluo_num > 3:
              context.insert(0, "本页的段落数量小于等于5且至少段落长度有4条以上80以下")
      elif duanluo_num > 5:
          # 段落短
          for item in context:
              if len(item.strip()) < 50:
                  short_duanluo_num+=1
          if short_duanluo_num > duanluo_num * 0.5:
              context.insert(0, "本页有超过一半的段落长度小于50字符")   # 如果有很多标题怎么办，一个标题一段文字
      return context
  ```

### 页眉页脚的处理

step2_drop_Pagefooter的方法不太行   感觉还是需要从坐标去下手

## 多余换行

新加入了换行的判定

```
    def step4_linefeed(self, context):
        index = 0
        while index < len(context):
            if index > 0:
                item = context[index]
                # 小写、括号开头合并到前一个item
                # todo 后续看标注的情况补充条件多的话可以单独写一个判定方法
                if item[0].strip().islower() or item[0].strip() in ["(", "[", ")", "]", "."]:
                    # print(item)
                    # 合并到前一个item
                    context[index - 1] = context[index - 1].rstrip() + " " + item.lstrip()
                    # 删除当前item
                    del context[index]
                    # 继续检查当前索引位置的元素
                    continue
            index += 1
        # print(context)
        return context
```

# v4: 有用性（参考文献，整页较短）+ 多余换行
# v5: 无关文本，有用性，多余换行； 缺少换行（怎么解）
# v6: v4版本结果出来，去分析；可能要关注错误删除；其他问题看v4的结果；

'''
  if "无关文本" in type_info:
      continue
  if "有用性" in type_info: # version4 版本有做
      continue
  if "多余换行" in type_info: # version4: 缺少： 不该换的地方换了
      continue
  if "缺少换行" in type_info: # (## 换行)
      continue
  if "错误删除" in type_info:
      continue

'''
