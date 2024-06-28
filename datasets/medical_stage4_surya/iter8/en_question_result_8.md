#### 无关文本

模型判断数字是否合理

需要不断地补充情况

```
 def step6_ngram_deletenum(self, context):
        # print(context)
        """
        循环 context 里面每个 item, 切分 item, 切分后每个最小单位就是一行内容，使用 ngram 判定数字
        :param context:
        :return: new_context
        """
        new_context = []

        for item in context:
            item_sections = re.split(r'\n', item)
            new_item_sections = []
            for section in item_sections:
                # print(section)

                section = section.strip()
                if len(section) == 0:
                    new_item_sections.append(section)
                    continue
                else:
                    pattern = r'\d+(\s?[\-–\.,]?(to|and)?\s?\d+){0,10}'
                    best_score = self.get_score(section)

                    while True:
                        matches = list(re.finditer(pattern, section))
                        if not matches:
                            break

                        # 找到所有匹配的数字及其位置
                        numbers_with_positions = [(match.group(), match.start(), match.end()) for match in matches]

                        # 标记是否更新了文本
                        updated = False

                        for num, start, end in numbers_with_positions:
                            # print(num,start,end)
                            # 如果是开头的数字，他可能是序号直接跳过
                            if start >= 0 and start < 4:
                                continue
                            # 特殊符号后面的数字也都是合理了 不用检查直接跳过
                            elif start > 0 and (section[start - 1] in ['$','>','<','='] or section[start - 2] in ['$','>','<','=']):
                                continue
                            # 使用位置进行替换
                            modified_text = section[:start] + section[end:]
                            modified_score = self.get_score(modified_text)

                            if modified_score < best_score:
                                best_score = modified_score  # 更新当前最优分数
                                section = modified_text  # 将分数低的文本重新赋给text
                                updated = True
                                break

                        # 如果没有更新文本，跳出循环
                        if not updated:
                            break
                    new_item_sections.append(section)

            new_context.append('\n'.join(new_item_sections))

        return new_context

```

补充：



#### 多余换行(已优化在一些换行出加入了ngram判断合成后的句子分数是不是低了，来确定一些换行)

加入模型（已解决）

```
def is_merge_ngram(self,text, next_text):
    """
    1.给text打分，next_text分别打分
    2.给marge_text打分
    3.判定marge_text满足分数小于text和next_text，且小于某个值 这个值可能是5000、3000、2000... 返回True
    :return:
    """
    text_score = self.get_score(text)
    next_text_score = self.get_score(next_text)
    merge_text = text + " " + next_text
    merge_text_sorce = self.get_score(merge_text)
    if merge_text_sorce < text_score or merge_text_sorce < next_text_score:
        # print(merge_text)
        return True
```





#### 多于换行新情况     3应该和1连接的但是中间穿插一个标题     （已解决）

```
示例1:

【1】CRACKING THGNOM: INSIDTHRACTO UNLOCK HUMAN DNA by Kevin Davies. Free Press, New York, 2001 ($25)

The massive effort of recent years to decode the human genome, Davies writes, “is, at the very least, an extraordinary technological achievement, and is at best perhaps the defining moment in the evolution of mankind.” Davies, founding editor of Nature Genetics and now executive editor of Current Biology, gives a clear account of the “epic battle” between the public Human Genome Project and the private Celera Genomics to be the first to sequence the genome. He examines difficult issues that arise from the program, among them the legal issue of gene patenting and the moral issue of genetic engineering. And he foresees that “the explosion in genomic information fueled by the sequence will revolutionize the diagnosis and treatment of countless diseases.”

【2】##The Turk, Chess Automaton

【3】by Gerald M. Levitt. McFarland & Company, Jefferson, N.C., 2000 ($50)

It was an impressive showpiece: a fierce-looking, turbaned puppet seated at a cabinet bearing a chessboard. Its successive owners from 1770 to 1854 would open the cabinet to display to an audience an array of gears and springs and then would invite a spectator to play a game of chess with the Turk, as the turbaned figure came to be known. The Turk usually won. Audiences and chess players were impressed. But it was a grand hoax.

Jammed uncomfortably into the cabinet, kept from the audience’s view by legerdemain, was a “director,” a human chess player who observed by candlelight the moves made by the opponent and operated the pantograph that executed the Turk’s responses.

【4】De Waal takes a different tack: “Instead of being tied to how we are unlike any animal, human identity should be built around how we are animals that have taken certain capacities a significant step farther. We and other animals are both similar and different, and the former is the only sensible framework within which to flesh out the latter.”

Sensible, yes, but ideology dies hard.

As de Waal so convincingly explains, we

##The ditors Recommend

【5】on the way to enlightenment, and this might be too scary for those invested in the supremacy of humankind. But for those ready for some self-scrutiny, and a less biased view of culture and learning in our fellow creatures, this book will be a revelation. In a sense, de Waal is our animal-behavior sushi master; look over his shoulder and learn what the animals tell us about ourselves.

Meredith Small is a writer and professor
示例2:
【2】##Prevention Of Cardiopulmonary Arrest

In Infants, The Leading Causes Of Death Are Congenital

【3】malformations, complications of prematurity, and SIDS. In children over 1 year of age, injury is the leading cause of death. Survival from traumatic cardiac arrest is rare, emphasizing the importance of injury prevention in reducing deaths.Motor vehicle crashes are the most common cause of fatal childhood injuries; targeted interventions, such as the use of child passenger safety seats, can reduce the risk of death. Resources for the prevention of motor vehicle-related injuries are detailed on the US
```

小写开头，去上一段判断是否有‘#’，如果有再往上找检查是否有‘#’，如果没有可以使用模型去判断该不该合（已完成）

```
"""
遇到小写开头的段 1.上一段没有#直接连上去 2.上一段有#但是不止一行，切上一段的最后一行和当前的第一行，使用模型判断该不该连 3.上一段有#但是只有一行，去上上段切最后一行和当前的第一行，模型判断该不该连
"""
```

#### 参考文献，以及整页参考文献的判断



#### 目录页(特征.)

如果某一页在多个context中发现多个\.判定为目录页

经观察发现有满足r'[\.\s]{15,}特征的基本就是目录页，在删除参看文献函数下加入这个特征

```
elif mulu_num > 0:
    new_context.insert(0, "(本页删除)本页发现目录的特征")
    return []
```

是不是可以从page_num字段中判定前几页，有什么其他方法拿到一些方法去判定他是不是目录页？

每个pdf的前n页后n页可以设定一个严格的判定标准



### guidelines分析