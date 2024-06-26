## reclean3标注结果分析

数字引用这里会把误删掉序号    需要修正

删除3 问题很大可不要或者重新写

删除2 会误判一些一千以上的数字例如（100,000、20,000）

删除8：会误删正文的内容

总结：无关文本这里的问题基本为序号问题，个别条件会误删正文

#### 无关文本新问题

- 括号里面是英文，可能是序号(a)

例：

无关文本#1#1#b)
无关文本#2#2#c)
无关文本#4#4#(Mara)

- 图片描述信息    关键词Figure

  例：Figure 1. PALS Pulseless Arrest Algorithm.

- 页脚（正在解决）

- 序号问题用换行解决

## 页边角的检测（这个是对块处理，不能写入当前的clean文件）

统一单位   一个full_blocks叫一个块   里面的最小单位叫一行   一列下去叫一栏

1. 怎么判定边角

   - 边界坐标 ＋ 块的大小（上下边界考略块的高度，左右边界考虑块的宽度）【疑问】
     左右边角，宽度差值小block[2]-block[0]<=20，且更靠近盒子左右边界
     上下边角，高度差值小block[3]-block[1]<=20，且更靠近盒子上下边界

   - 

   - ```
     def is_page_foot(img_box,index,block):
         """
         边界坐标 ＋ 盒子的大小（上下边界考略盒子的高度，左右边界考虑盒子的宽度）
         左右边角，宽度差值小block[2]-block[0]<=20，且更靠近盒子左右边界
         上下边角，高度差值小block[3]-block[1]<=20，且更靠近盒子上下边界
         """
         # 检测右测边角
         if img_box[2]-block[0] <= 100:
             return True
         # 检测下面边角
         elif img_box[3]-block[1] <= 100:
             return True
         # 检测左侧边角 盒子的右边的边界小于100
         elif block[2]-img_box[0] <= 100:
             return True
         # 上边角会遇到标题这个问题，要不要解决？ 先添加上
         elif block[3]-img_box[1] <= 100:
             return True
         else:
             return False
     ```

2. 怎么删除边角

   - 直接删除块

3. 怎么判定侧边栏

   - 

4. 怎么删除侧边栏

扩展

1. 如果有一页内是多栏，其中有一个块他的宽度大于img_box宽度的二分之一，可能会有问题，即使是双栏他的宽度也是小于二分之一的，需要观察这一特征
2. 如果说这一特征再放大是否能检测侧栏

## 重写检测参考文献的方法代替之前的正则看是否会好点降低误删

如果新的方法不行再换回去

```
def step5_2_isreference(item, person_num, names_start2stop):
    # 定义正则表达式模式来匹配参考文献中的常见元素
    patterns = [
        r'\.\s?\b\d{4}\b',  # 年份，比如 2010
        r'\b\d{4}\b\s?;',   # 年份，比如 2010;
        r'(?:Journal|Proceedings|Conference|Studies|Review|BMJ|JAMA|Pediatrics|Crit Care Med|Nurs Crit Care|Acad Emerg Med|Health Serv Res)',
        # 期刊或会议名的关键词
        r'(?:doi:\s*\S+)',  # DOI
        r'(?:vol\.?\s*\d+)',  # 卷号
        r'(?:no\.?\s*\d+)',  # 期号
        r'(?:pp\.?\s*\d+\s*-\s*\d+)',  # 页码范围
        r'\d+\s?:\d+\s?[–-]\s?\d+',  # 页码范围格式
        r'\set al\.' # et al
    ]
    matched = any(re.search(pattern, item, re.IGNORECASE) for pattern in patterns)
    # 至少有三个人名且有上述特征
    if person_num > 2 and matched:
        return True
    return False
    
    
if step5_2_isreference(item,person_num,names_start2stop):
    # item重写
    item = fr'整段删除参考文献:<u>{item}</u>'
```

## 序号问题用换行解决

从每个item上

```
def step4_linefeed(self, context):
    index = 0
    while index < len(context):
        if index > 0:
            item = context[index]
			
		   # v5 新加入
            # 对item内进行以"\n"的切分
            item_sections = re.split('\n', item)
            section_index = 0
            while section_index < len(item_sections) - 1:  # 确保不会越界
                if re.search(r'\s\d\.$', item_sections[section_index]):  # 匹配段落结尾是数字和句点
                    item_sections[section_index] = item_sections[section_index] + item_sections[section_index + 1]
                    del item_sections[section_index + 1]
                else:
                    section_index += 1  # 只有在不合并时才自增



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

reclean4部分总结

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



step1侧栏的删除会误删正文不合适，要删掉

例：'seq_id': 'df7b3bd2-6031-457a-803d-70bb78568153'











## 多余换行逻辑添加



介词相连  已完成



