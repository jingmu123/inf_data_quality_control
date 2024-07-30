import itertools
import json
import math
import re

import numpy as np
# import pdfplumber


def sorted_layout_tolanmu(text_blocks,pixel_tolerance=100):
    # 1. 对layout先按纵坐标排序，然后按照横坐标排序，归并栏
    sorted_blocks = sorted(text_blocks, key=lambda x: (x["full_bbox"][1], x["full_bbox"][0]))

    # 每个元素是一个栏,为一个列表，列表中的元素是上述定义的layout元素
    block_lanmu = []
    # 根据**左上角**的横坐标将文本块放入对应的列,sorted_text：分栏的结果
    for block_item in sorted_blocks:
        placed = False
        # 存放已有的基准
        for block_lanmu_item in block_lanmu:
            # pixel_tolerance横向像素的冗余，暂定100，横向像素左右差100仍然算同一列
            if not block_lanmu_item or abs(block_lanmu_item[-1]["full_bbox"][0] - block_item["full_bbox"][0]) <= pixel_tolerance:
                block_lanmu_item.append(block_item)
                placed = True
                break
        if not placed:
            # 如果没有找到合适的列（栏），创建新的一列
            block_lanmu.append([block_item])
    return block_lanmu


def fix_title_position(block_item):
    # 3.排列栏目内的顺序
    # 初步排序后再次进行排序，本次排序同一列中的排序以基本有序，主要是针对有序号的出现
    new_sort = []
    for block_lanmu_item in block_item:
        # 拿出来了当前栏的所有block
        # columns.append(column.get('block'))
        new_block_lanmu_item = []
        # 标题与正文之间的高度基本差不多允许有5以内的偏差，对比谁的横坐标像素小谁在前面，这样大体的排序不会变
        for block_item in block_lanmu_item:
            if new_block_lanmu_item and abs(new_block_lanmu_item[-1]["full_bbox"][1] - block_item["full_bbox"][1]) <= 5:
                # 根据横坐标，判断加入顺序
                if block_item["full_bbox"][0] < new_block_lanmu_item[-1]["full_bbox"][0]:
                    new_block_lanmu_item.insert(-1, block_item)
                else:
                    new_block_lanmu_item.append(block_item)
            else:
                new_block_lanmu_item.append(block_item)
        new_sort.append(new_block_lanmu_item)
    return new_sort


def sort_mini_block_text(raw_item):
    # todo: 对最小块进行排序  2024/7/19补充
    """
    :param text:raw_item是一个大块信息，
    先拿到小块的raw_context列表，小块重新排序，重写回每个大块的raw_context，
    :return:raw_item
    """

    raw_context = raw_item['raw_context']

    # 按照纵坐标中心点 (bbox[1] + bbox[3]) / 2 从小到大排序
    sorted_raw_context = sorted(raw_context,
                                key=lambda small_block: (small_block['bbox'][1] + small_block['bbox'][3]) / 2)

    # print(sorted_raw_context)
    # 对于纵坐标中心点相差较小的小块，再按照横坐标中心点 (bbox[0] + bbox[2]) / 2 从小到大排序
    def custom_sort(small_block):
        return (small_block['bbox'][0] + small_block['bbox'][2]) / 2

    final_sorted_raw_context = []  # 最终排序后的小块列表
    current_group = []  # 当前相邻纵坐标差异较小的小块组
    previous_item = None  # 上一个处理的小块

    for small_block in sorted_raw_context:
        if previous_item and abs(small_block['bbox'][1] - previous_item['bbox'][1]) <= 10:
            # 如果当前小块与上一个小块的纵坐标差异小于等于5，则放入同一组
            current_group.append(small_block)
        else:
            # 添加一个小块，
            if current_group:
                # 对当前组按照横坐标中心点排序并加入最终排序列表
                current_group = sorted(current_group, key=custom_sort)
                final_sorted_raw_context.extend(current_group)
                current_group = []

            current_group.append(small_block)
        previous_item = small_block
    # 处理最后一组小块
    if current_group:
        current_group = sorted(current_group, key=custom_sort)
        final_sorted_raw_context.extend(current_group)

        # 比较排序前后的raw_context，找出发生变化的位置
    changes = [(i, raw_context[i], final_sorted_raw_context[i]) for i in range(len(raw_context)) if
               raw_context[i] != final_sorted_raw_context[i]]

    # print(final_sorted_raw_context)
    # 更新big_block中的raw_context
    raw_item['raw_context'] = final_sorted_raw_context

    return raw_item


def calculate_xy(origin_lis, x_or_y):
    locate_lis, index_lis, = [], []

    if x_or_y == 'x':
        index_locate, index_index, index_def, index_sum = 1, 4, 0, 2
    elif x_or_y == 'y':
        index_locate, index_index, index_def, index_sum = -1, 0, 1, 3

    for index, single in enumerate(origin_lis):
        if index == 0:
            locate_lis.append([single[index_locate]])
            index_lis.append([single[index_index]])
            temple_index = 0
            continue

        def_x_or_y = abs(origin_lis[temple_index][index_def] - origin_lis[index][index_def])#分别两个框的 x中间值/y中间值 的之间的差
        sum_half = origin_lis[temple_index][index_sum] / 2 + origin_lis[index][index_sum] / 2#分别两个框的 宽/长 的一半的和

        if def_x_or_y < sum_half:
            #判断为 同列/同行
            locate_lis[-1].append(single[index_locate])
            index_lis[-1].append(single[index_index])

        else:
            temple_index = index
            locate_lis.append([single[index_locate]])
            index_lis.append([single[index_index]])

    return locate_lis, index_lis


def repair_headline_locate(raw_info):  # 对大块的排序7/19新加
    origin_lis= []
    for index, part in enumerate(raw_info):
        locate = part['full_bbox']
        x_center, y_center, w, h = int((locate[0] + locate[2]) / 2), int((locate[1] + locate[3]) / 2), int(
            (locate[2] - locate[0])), int((locate[3] - locate[1]))
        origin_lis.append([x_center, y_center, w, h, index, part['text']])

    origin_lis.sort(key=lambda x: x[0])#按x轴中间值排序，计算同列
    locate_lis,index_lis=calculate_xy(origin_lis,'x')

    count = 0
    if len(locate_lis)>1:
        origin_lis.sort(key=lambda x: x[1])  # 按y轴中间值排序，当上一条判断为多列时计算同行个数来再次判断是否为多列
        height_lis, _ = calculate_xy(origin_lis, 'y')

        for text_lis in height_lis:
            if len(text_lis)>1:
                for words in text_lis:
                    if not isinstance(words,str):
                        continue
                    word=words.replace('\n','')
                    word=word.replace('#','')
                    if len(word)<15:#去除换行符与#字符，计算这行的字数，来去除小标题与序号单独识别为单列的情况
                        count-=1
                        break
                count+=1
        len_lis=sorted([len(i) for i in locate_lis])
        sec_num=len_lis[-2]
        if count >= (sec_num / 2):#count:文本框存在同行的个数，min_num:第二长的列的长度，当去除了小标题与序号后，仍然有同行文本，并且超过第二长的列一半的长度时：
            pass #（再次判断为多列）
        else:
            # （再次判断为单列）
            locate_lis = [list(itertools.chain(*locate_lis))]
            index_lis = [list(itertools.chain(*index_lis))]

    for index, lis in enumerate(locate_lis):#对每一个full_block排序
        index_array = np.array(index_lis[index])
        sorted_indices = np.argsort(lis)
        index_lis[index] = list(index_array[sorted_indices])

    index_lis = [list(itertools.chain(*index_lis))]
    final_lis = np.array(raw_info)
    final_lis = list(final_lis[index_lis])

    return final_lis


def sort_text_by_pix(raw_info_list):
    text_blocks = []
    for idx,item in enumerate(raw_info_list):
        item["index"] = idx
        # 对最小块进行排序  2024/7/19补充
        item = sort_mini_block_text(item)
        text_blocks.append(item)
        
    # 1. 对layout先按纵坐标排序，然后按照横坐标排序，归并栏
    # block_lanmu = sorted_layout_tolanmu(text_blocks)

    # 2. 按照横坐标做了排序, 排列栏的顺序
    # block_lanmu_sorted = sorted(block_lanmu, key=lambda x: x[0]["full_bbox"][0])

    # 3.排列栏目内的顺序
    # new_sort = fix_title_position(block_lanmu_sorted)

    # 7/19 大块的排序 代替之前 的排序
    block_lanmu_sorted = repair_headline_locate(text_blocks)
    # 输出：排序后的block列表
    return block_lanmu_sorted


def is_index(item):
    if isinstance(item, str):
        return False  # 如果是字符串，返回 False 或者你需要的其他值
    for block_item in item['raw_context']:
        # 判断 item 是否是字符串
        if isinstance(block_item, str):
            return False  # 如果是字符串，返回 False 或者你需要的其他值
        else:
            text = block_item['text'].strip()
            # 发现有item中text里面不全是索引就不全是索引，返回False
            if not re.match(r'^(\d+\.|[a-z]\.|\s){1,3}$', text):
                return False
    return True


def find_next_block(column, current_block):
    for block_item in column:
        if current_block["full_bbox"][1] >= block_item["full_bbox"][1] and current_block["full_bbox"][3] <= block_item["full_bbox"][3] and current_block != block_item:
            return block_item
    return None


def merge_block(block_item,next_block):
    raw_context = block_item["raw_context"]
    next_context = next_block["raw_context"]
    for raw_item in raw_context:
        index_bbox =raw_item.get("bbox")
        # 去遍历next_context找对应的行:
        for next_raw_item in next_context:
            next_index_bbox = next_raw_item.get("bbox")
            # todo :如果不符合连接条件，就直接删除了？
            if abs(index_bbox[1] - next_index_bbox[1]) <= 5:
                next_raw_item['text'] = raw_item['text'] + " "+ "{}".format(next_raw_item['text'])
                #print(next_raw_item['text'])
                # print("----"*20)
                return next_block
            
        
def reorder_context(new_sort):
    new_raw_info = []
    for index, block_lanmu in enumerate(new_sort):
        # print(block)
        for block_index,block_item in enumerate(block_lanmu):
            if is_index(block_item):
                next_block = find_next_block(block_lanmu,block_item)
                if next_block:
                    next_block = merge_block(block_item,next_block)
                else:
                    if block_index+1 < len(block_lanmu):
                        next_block = block_lanmu[block_index+1]
                        next_block = merge_block(block_item,next_block)
                    else:
                        break
            else:
                new_raw_info.append(block_item)
    return new_raw_info


def block_surround(text, block_type):
    if block_type == "Section-header":
        if not text.startswith("#"):
            text = "\n## " + text.strip().title() + "\n"
    elif block_type == "Title":
        if not text.startswith("#"):
            text = "# " + text.strip().title() + "\n"
    elif block_type == "Table":
        text = "\n" + text + "\n"
    elif block_type == "List-item":
        pass
    elif block_type == "Code":
        text = "\n" + text + "\n"
    return text


def block_separator(line, block_type):
    sep = "\n"
    if block_type == "Text":
        sep = "\n\n"
    return sep + line


def final_post_process_zh(sorted_raw_info, lang):
    for block_item in sorted_raw_info:
        raw_context = block_item['raw_context']
        full_blocks = block_item['full_bbox']
        flag_x1 = full_blocks[0]
        flag_x2 = full_blocks[2]
        new_text = ''
        block_type = block_item["type"]
        if block_type == "Table":
            block_item["old_text"] = "this is table."
            continue
        #print(block_item["block_text"])
        sp_list = ['-','–']

        # 判断new_text结尾是否为\n
        def flag_n(text):
            if not text:
                return True
            else:
                return True if text[-1] == '\n' else False

        for item in raw_context:
            bbox = item["bbox"]
            b_text = item['text']
            x1 = bbox[0]
            x2 = bbox[2]
            limit = (x2 - x1) / len(b_text) * 2 if len(b_text) else 999
            # print(x1 - flag_x1, flag_x2 - x2, limit)

            # 判断左缩进确定句首是否要加\n
            if x1 - flag_x1 >= limit:
                new_text += '' if flag_n(new_text) else '\n'

            # 判断右缩进确定句末是否要加\n
            if lang == 'zh':
                new_text += b_text + '\n' if flag_x2 - x2 >= limit else b_text
            else:  # 英文需特殊处理连字符和空格
                if flag_x2 - x2 >= limit:
                    new_text += b_text + '\n' if flag_n(new_text) else ' ' + b_text + '\n'
                else:
                    if new_text and new_text[-1] in sp_list:
                        new_text = new_text[:-1] + b_text
                    else:
                        new_text += b_text if flag_n(new_text) else ' ' + b_text

        new_text = block_surround(new_text, block_type)
        block_item["old_text"] = block_item["text"]
        block_item["text"] = new_text

    return sorted_raw_info
