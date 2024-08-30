reclean3_dovepress_preformat_sample

reclean2_dovepress_preformat_sample报告

从reclean1和reclean2的结果来看，此次reclean2解决了无关文本80%的无关文本，以及80%的无关链接问题

目前主要问题在无关数字和误删上

无关数字已经添加了风险较小的解决方法但是示例显著增多，相比之前应该是少才对

错误删除中有80%都是已解决的问题，删除2和删除5关联，在去标签之后删除2先执行后删除5就匹配不到，还有少量的数字误删

其余的问题都较少，全部解决基本只能提升1分左右

无关文本预计能解决80%提升1分

无关数字预计能解决70%-80%这个不太确定，提升17-19分

误删去除标签后可以恢复80%，其他的误删都是个例不做处理，预计提升5分

此次处理清除标签，预计分数提升到85分左右

无关文本

带有括号的编号 NCT\d+|N[oO]\.

作者贡献以下都删
Author contributions|Supporting Documents|Registration|Data sharing statement等一些文章末的描述

无关数字，添加新方法加入ngram模型，对某一块出现的数字进行删除前后比较判断要不要删除这个数字

```
def step3_ngram_deletenum(self, context):
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
            section = section.strip()
            if len(section) == 0:
                new_item_sections.append(section)
                continue
            else:
                pattern = r'\s\d+(\s?[\-–\.,]?(to|and)?\s?\d+){0,10}\s'
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
                        elif start > 0 and (
                                section[start - 1] in ['$', '>', '<', '='] or section[start - 2] in ['$', '>', '<','=']):
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

