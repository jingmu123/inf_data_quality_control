import json
import re
from tqdm import tqdm
import math
import spacy
import random
from nltk.corpus import wordnet
import inflect
inflect = inflect.engine()
import kenlm
from nltk.tokenize import word_tokenize



pattern_list = [

    # 去除带有网址的句子,关键词   www、com、html、http
    # todo www,http放一起考虑，右边界的准确性需要考虑
    # todo com,html放一起考虑，左边界需要考虑
    [r'([^\d][^\.\n]*(([Ww]{2,3}\.)|(\.[Cc][Oo][Mm])|(http)|(\.html))[^\n]*)',r''],

    [r'(\n\s*[a-zA-Z\.]\s*\n)', r''],
    [r'([^\n]*Copyright[^\n]*)', r''],
    [r'(ISBN\s*[A-Z0-9-]*)', r''],
    # 带特殊符号的无关内容
    [r'(👍|▶|●|©|®|([^\n]*↑[^\n]*)|†|¶|║|§|∧|™|■|❏|□|✓|✔|❍)', r''],
    # 无关文本
    # 无关图片引用
    [r'((\()\b([Ff]igure[s]?|Section|diagram|Appendix|Box|[Ss]ource[s]?|Fig|p)\b:?\.?\s*(\d+)?\.?.*?(\)))',r''],
    [r'([^\n\.]*\b(Fig[s]?[ure]?[s]?)\b\.?[\s* ](\d+)?\.?[^\n]*)', r''],
    [r'((\([^\(]{0,20})\s[Ff]igures?[^\.\(\)]*.)',r''],
    [r'([\(\[]([Tt]able|[sS]ee)[^\)\]]*?[\)\]])',r''],

    # 数字引用
    #1.带括号 book (1，2).
    [r'(\([\d\s,\.\-–]{1,50}\))',r''],
    #2.不带括号但是数字前是句号. 数字后是换行或者大写字母
    # 带[]为guidelines写的
    [r'([^\d])(\[\s?\d{1,4}(\s{0,3}[\-–—,\.]\s{0,3}\d{1,4}){0,20}\s?\])',r'\1'],
    # [r'([^\d])([1-9]{1,3}(\s{1,3}[\-–,\.]\s{1,3}[1-9]{1,3}){1,20})([^\d]?)', r'\1删除2:<u>\2</u>\4'],
    # # 不带括号
    [r'([^\d])([1-9][0-9]{1,4}(\s{1,3}[\-–,\.]\s{1,3}[1-9][0-9]{1,4}){1,20})([^\d]?)', r''],
    # 不带括号数字或数字加点（容易误删）
    [r'(\[\s?(\d{1,3}\s?[-,，]?\s?)+\d?\s?\]\s?\*?)', r""],
    # 参考引用：数字类型，加入空格做泛华[1,2 - 3, 4, 5]
    [r'(\[\s?(\d{1,3}\s?[-,，]?\s?)+\d?\s?\]\s?\*?)', r""],
    # # 参考应用的复杂格式：字母(Ia,\nb)
    [r'(\(\s?[IⅡⅢⅣⅤⅥⅦⅧⅨⅩⅪⅫa-zA-Z]?\s?[a-zA-Z]?\s?,\s?[a-zA-Z]\s?\)\s?)[。\.]', r""],
    # 上一句的句号\d中间没有点[大写]，这里的\d后面没有点不是序号可能是上一句的引用数字
    [r'([^\d][\.,])((\s{1,3}\d+[\s\n]{1,3}){1,5}\.?)(\s?[A-Z])',r'\1\4'],
    # 介词前面有数字会有问题
    # [r'((\d+[\.,]?){1,5})(\s(and|or|the|:)\s)',r'删除7:<u>\1</u>\3'],
    # 给guidelines补充
    # [r'([^\d][\.,]\s?)(\d{1,4}(\s{0,3}[\-–,\.\s]\s{0,3}[1-9][0-9]{1,4}){0,20})(\n|\s?[A-Z])',r'\1\4'],
    [r'([^\d][\.,]\s?)(\d{1,4}(\s{0,3}[\-–,\.\s]\s{0,3}\d{1,4}){0,20})(\n|\s?[A-Z]|$)',r'\1\4'],
    # 结尾句号后面为数字和序号区别开序号后面还有一个.
    # [r'([^\d]\.)(\s?\d{1,4}(\s{0,3}[\-–,\.]\s{0,3}[1-9][0-9]{1,4}){0,20})(\n)',r'\1\4'],
    [r'(#{1,3})\n',r'\1']
 ]

context_pattern = [
    [r'(¬\s*)', r''],
    [r'(\(\s*\))', r'']
]

# nlp = spacy.load("en_core_web_trf")
nlp = spacy.load("en_core_web_sm")
model = kenlm.LanguageModel(r"/Users/mirli/worker/code/code_work/pythonProject1/ngram/4k_gram.klm")
class speicalProces:
    def __init__(self):
        pass

    def is_not_upper(self, char):
        return not char.isupper()


    def is_page_foot(self,least_bbox,img_box):
        """
        左右边角，宽度差值小block[2]-block[0]<=20，且更靠近盒子左右边界
        上下边角，高度差值小block[3]-block[1]<=20，且更靠近盒子上下边界
        """
        # 检测右测边角
        if img_box[2] - least_bbox[0] <= 100:
            return True
        # 检测下面边角
        elif img_box[3] - least_bbox[1] <= 100:
            return True
        # 检测左侧边角
        elif least_bbox[2] - img_box[0] <= 100:
            return True
        # 上边角会遇到标题这个问题，要不要解决？
        elif least_bbox[3] - img_box[1] <= 100:
            return True
        else:
            return False

    def step1_drop_Pagefooter(self, item):
        # print(json.dumps(item, ensure_ascii=False))
        """
        1.遍历full_blocks判断是否为页边角
        2.在text中找到内容给删掉
        """
        raw_info = item['attr']['raw_info']
        img_box = item['attr']['img_box']
        for raw in raw_info:
            full_blocks = raw['full_blocks']
            if self.is_page_foot(full_blocks, img_box):
                # 如果大块被删掉整段内容
                block_text = raw['block_text'].strip()
                # 对 least_text 进行正则转义
                escaped_least_text = re.escape(block_text)

                # 构建正则模式，匹配可能的前后空格、换行符和连字符
                pattern = re.compile(escaped_least_text + r'[\s\n-]{0,5}')

                # 使用正则表达式替换匹配的文本
                item['text'] = re.sub(pattern, '', item['text'])
        # print(item)

        return item

    def step2_delete_photopage(self, item):
        raw_info = item['attr']['raw_info']
        img_box = item['attr']['img_box']
        img_area = (img_box[2] - img_box[0]) * (img_box[3] - img_box[1])
        all_block_area = []
        for raw in raw_info:
            full_blocks = raw['full_blocks']
            block_area = (full_blocks[2] - full_blocks[0]) * (full_blocks[3] - full_blocks[1])
            all_block_area.append(block_area)

        if len(raw_info) <= 3 and sum(all_block_area) < img_area * 0.2:
            item['text'] = "(本页删除)此页的内容部分所占的比例小于0.2" + item['text']
            # 返回空的text
            item['text'] = ""
        return item
    def get_score(self, sentence):
        tokenize_text = word_tokenize(sentence)
        final_text = " ".join(tokenize_text)
        if len(tokenize_text) == 0:  # 检查分词后是否为空
            return float('inf')  # 或者返回其他适当的值，如 0 或者某个高分
        score = model.score(final_text, bos=False, eos=False)
        length = len(tokenize_text)
        score = (10 ** (-score / length))
        return score
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

    def is_merge_duannei(self, text, next_text):
        # 定义一个介词列表
        preposition_list = ['of', 'in', 'and', 'or', 'not', 'the', 'a', 'any', 'for', 'is', 'The', 'A']
        if re.search(r'\s\d+\.$', text): #
            return True
        elif re.search(r'^([\d+A-Z][\.,]){1,3}$', text) and next_text.lstrip()[0].isupper():  # 匹配段落中只有序号且下一段是大写开头的情况
            return True
        elif any(text.rstrip().endswith(" " + prep) for prep in preposition_list):  # 匹配同一段中介词结尾的
            return True
        elif text.rstrip()[-1] in ['-']:
            return True
        elif "#" not in text and "*" not in text and re.search(r'[^\.?!]$', text) and re.match(r'^[a-z]', next_text.lstrip()):
            return True
        elif re.search(r'\([^\)]*$|\[[^\]]*$', text) and re.match(r'^[^\(\[]*[\)\]]',next_text):  # 前一行有一个未对应的左括号，下一行前面有一个与之对应的右括号
            return True
        elif (text.rstrip()[-1].islower() and next_text.lstrip()[0].isupper() and "#" not in text and "#" not in next_text and self.is_merge_ngram(text, next_text)):   # 前一行小写结尾，下一行大写开头，且与标题无关，加入ngram判断
            return True
        return False
    def is_merge_duan(self,stripped_item):
        # 定义一个介词列表
        preposition_list = ['of', 'in', 'and', 'or', 'not', 'the', 'a', 'any', 'for', 'is', 'The', 'A']
         # 新增条件: 如果 stripped_item 结尾的单词在 preposition_list 中
        if any(stripped_item.rstrip().endswith(" " + prep) for prep in preposition_list):
            return True
        elif stripped_item[-1] == '-':
            return True

        return False

    def step3_more_linefeed(self, context):
        # print(context)
        index = 0
        while index < len(context):
            item = context[index]


            # 将 item 按 "\n" 分割
            item_sections = re.split(r'\n', item)
            section_index = 0

            while section_index < len(item_sections) - 1:  # 确保不会越界
                if self.is_merge_duannei(item_sections[section_index],item_sections[section_index + 1]):
                    item_sections[section_index] += " " + item_sections[section_index + 1].lstrip()
                    del item_sections[section_index + 1]
                else:
                    section_index += 1  # 只有在不合并时才自增

            # 更新 item 以反映合并的段落
            item = '\n'.join(item_sections)
            context[index] = item
            # 合并以小写字母或特定标点符号开头的段落
            stripped_item = context[index].strip()

            if index > 0:
                if stripped_item and (stripped_item[0].islower() or stripped_item[0] in ["(", "[", ")", "]", "."]):
                    """
                    遇到小写开头的段 1.上一段没有#直接连上去 2.上一段有#但是不止一行，切上一段的最后一行和当前的第一行，使用模型判断该不该连 3.上一段有#但是只有一行，去上上段切最后一行和当前的第一行，模型判断该不该连
                    """
                    # 上一段不能出现#，出现#证明是标题段
                    if not re.search(r'#',context[index - 1]):
                        # 合并到前一个 item
                        context[index - 1] = context[index - 1].rstrip() + " " + item.lstrip()
                        # 删除当前 item
                        del context[index]
                        # 继续检查当前索引位置的元素
                        index = index - 1
                        continue
                    elif len(re.split(r'\n', context[index - 1])) >= 2:
                        # 上一段有标题也有正文，分割context[index-1]最后一行，分割stripped_item的第一行
                        previous_paragraph_lines = re.split(r'\n', context[index - 1])
                        last_line_of_previous = previous_paragraph_lines[-1].strip()
                        first_line_of_current = stripped_item.splitlines()[0].strip()
                        if self.is_merge_ngram(last_line_of_previous, first_line_of_current):
                            # 合并到前一个 item
                            context[index - 1] = context[index - 1].rstrip() + " " + item.lstrip()
                            # 删除当前 item
                            del context[index]
                            # 继续检查当前索引位置的元素
                            index = index - 1
                            continue
                    # elif len(re.split(r'\n', context[index - 1])) >= 2:
                    #     # 上一段有标题也有正文，分割context[index-1]最后一行，分割stripped_item的第一行，如果标题在最后一行看倒数第二行
                    #     previous_paragraph_lines = re.split(r'\n', context[index - 1])
                    #     last_line_of_previous = previous_paragraph_lines[-1].strip()
                    #     first_line_of_current = stripped_item.splitlines()[0].strip()
                    #
                    #     if '#' in last_line_of_previous:  # 如果最后一行中发现有#
                    #         last_line_of_previous = previous_paragraph_lines[-2].strip()
                    #         if self.is_merge_ngram(last_line_of_previous, first_line_of_current):
                    #             # 合并到倒数第二行后
                    #             previous_paragraph_lines[-2] = previous_paragraph_lines[-2].rstrip() + " " + item.lstrip()
                    #             # 移除最后一行
                    #             previous_paragraph_lines.pop(-1)
                    #             # 重新合并 context[index - 1] 的内容
                    #             context[index - 1] = '\n'.join(previous_paragraph_lines)
                    #             # 删除当前 item
                    #             del context[index]
                    #             # 继续检查当前索引位置的元素
                    #             index = index - 1
                    #             continue
                    #     else:
                    #         if self.is_merge_ngram(last_line_of_previous, first_line_of_current):
                    #             # 合并到前一个 item
                    #             context[index - 1] = context[index - 1].rstrip() + " " + item.lstrip()
                    #             # 删除当前 item
                    #             del context[index]
                    #             # 继续检查当前索引位置的元素
                    #             index = index - 1
                    #             continue
                    elif len(re.split(r'\n',context[index-1])) == 1:
                        if index - 2:
                            previous_paragraph_lines = re.split(r'\n', context[index - 2])
                            last_line_of_previous = previous_paragraph_lines[-1].strip()
                            first_line_of_current = stripped_item.splitlines()[0].strip()
                            if self.is_merge_ngram(last_line_of_previous, first_line_of_current):
                                # 合并context[index - 2]
                                context[index - 2] = context[index - 2].rstrip() + " " + item.lstrip()
                                # 删除当前 item
                                del context[index]
                                # 继续检查当前索引位置的元素
                                index = index - 1
                                continue
                elif self.is_merge_duan(stripped_item):
                    if index + 1 < len(context) and "#" not in context[index + 1]:
                        # 合并到下一个 item
                        context[index] = item.rstrip() + " " + context[index + 1].lstrip()
                        # 删除下一个 item
                        del context[index + 1]
                        # 不增加 index, 继续检查当前索引位置的元素
                        index = index - 1
                        continue
                # 当前段不是标题没有结尾标点，切片还是用模型判断一下
                elif "#" not in stripped_item and re.search(r'[^\.?!:：”"]$', stripped_item.strip()):
                    if index + 1 < len(context):
                        previous_paragraph_lines = re.split(r'\n', stripped_item)
                        last_line_of_current = previous_paragraph_lines[-1].strip()
                        first_line_of_next = context[index + 1].splitlines()[0].strip()
                        if index + 1 < len(context) and "#" not in context[index + 1] and self.is_merge_ngram(last_line_of_current,first_line_of_next):
                            # 合并到下一个 item
                            context[index] = item.rstrip() + " " + context[index + 1].lstrip()
                            # 删除下一个 item
                            del context[index + 1]
                            # 不增加 index, 继续检查当前索引位置的元素
                            index = index-1
                            continue

            index += 1
        # print(context)
        return context

    def step4_lack_linefeed(self,context):
        new_context = []
        for item in context:
            # 查找 #•，并在其前后加换行符
            # parts = re.split(r'(?<=\s)([#•]{1,3}\s?[A-Z][^#•]*)', item)
            # 定义多个分隔符并用竖线连接
            splitchar = r'([#•]{1,3}\s)'
            # 使用连接后的正则表达式拆分
            parts = re.split(splitchar, item)
            new_parts = []
            for part in parts:
                if re.search(splitchar, part):
                    new_parts.append(part.strip())
                elif re.search(r'([\.\)])(\s\d{1,2}\.\s?[A-Z])',part):
                    part = re.sub(r'([\.\)])(\s\d{1,2}\.\s?[A-Z])',r'\1\n\2',part)
                    new_parts.append(part.strip() + '\n')
                else:
                    new_parts.append(part.strip() + '\n')

            item = "".join(new_parts)
            # print(item)
            new_context.append(item)
        return new_context

    def get_person_idx(self, item):
        doc = nlp(item)
        person_block = []
        person_num = 0
        # print(doc.ents)
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                if len(person_block) == 0:
                    person_block.append([ent.start_char, ent.end_char])
                elif ent.end_char - person_block[-1][-1] > 5:
                    person_block.append([ent.start_char, ent.end_char])
                else:
                    person_block[-1][-1] = ent.end_char
                person_num += 1
        return person_block, person_num

    def step5_rm_cite(self, item):
        # patterns = [
        #     r'\.\s?\b\d{4}\b',  # 年份，比如 . 2010
        #     r'\b\d{4}\b\s?;',  # 年份，比如 2010;
        #     r'(?:Journal|Proceedings|Conference|Studies|Review|BMJ|JAMA|Pediatrics|Crit Care Med|Nurs Crit Care|Acad Emerg Med|Health Serv Res)',
        #     # 期刊或会议名的关键词
        #     r'(?:doi:\s*\S+)',  # DOI
        #     r'(?:vol\.?\s*\d+)',  # 卷号
        #     r'(?:no\.?\s*\d+)',  # 期号
        #     r'(?:pp\.?\s*\d+\s*-\s*\d+)',  # 页码范围
        #     r'\d+\s?:\d+\s?[–-]\s?\d+',  # 页码范围格式
        #     r'\set al\.'  # et al
        # ]
        cite_tag = []
        cite_index = 1 if len(re.findall(r'\[\d+\]', item)) > 0 else 0
        cite_year = 1 if len(
            re.findall(r'\[\d\d\d\d\]', item) or re.findall(r'\.\s?\b\d{4}\b', item) or re.findall(r'\b\d{4}\b\s?;',
                                                                                                   item)) else 0  # 年份，比如 . 2010 、 2010;
        cite_page = 1 if len(re.findall(r'\d+\s?:\d+\s?[–-]\s?\d+', item)) else 0
        cite_J = 1 if len(re.findall(r'\[[Jj]\]', item)) else 0
        cite_doi = 1 if " doi " in item else 0
        cite_etal = 1 if (" et al" in item or 'et\u00A0al' in item) else 0
        cite_vol = 1 if " vol. " in item else 0
        cite_pp= 1 if " Pp " or " pp " in item else 0
        # cite_page = 1 if len(re.search(r'\.\s?\b\d{4}\b',item)) else 0
        cite_phonenum = 1 if re.search(r" [Pp]hone:|Fax:", item) else 0
        mulu = 1 if re.search(r'[\.\s]{15,}',item) else 0
        cite_tag = [cite_index, cite_year, cite_J, cite_doi, cite_etal, cite_page, cite_vol, cite_phonenum,cite_pp]
        if sum(cite_tag) > 1 and '|' not in item:
            return "参考删除-0:<u>{}</u>".format(item)
        person_block, person_num = self.get_person_idx(item)
        # 超过5个人名
        person_block_lens = [block_item[1] - block_item[0] for block_item in person_block]
        person_lens = sum(person_block_lens)
        if person_lens / len(item) > 0.5 and len(item) > 100:
            return "参考删除-1:<u>{}</u>".format(item)
        # 只有个名字数量
        elif person_num > 5 and '|' not in item and len(item) < 200:
            return "参考删除-2:<u>{}</u>".format(item)
        # elif cite_index and person_num > 0:
        #     return "参考删除-3:<u>{}</u>".format(item)
        elif mulu:
            return "目录删除:<u>{}</u>".format(item)
        else:
            return item

    def step5_removepage(self, context):
        # context 是一个列表，每个 item 是一段内容
        context_lens = len(context)
        # 用于统计有多少个段落中出现了人名
        num = 0
        mulu_num = 0
        new_context = []
        for item in context:
            # 返回的item是已经被重写过的item
            item = self.step5_rm_cite(item)
            # 新的item重新加入一个新的列表
            new_context.append(item)
            # 判断item是否被判定未参考文献
            if re.search(r'参考删除',item):
                # 如果当前段落中有人名且符合参考文献的特征
                num += 1
            elif re.search(r'目录删除',item):
                mulu_num += 1
        # print(new_context)
        # 对整页的一个判断
        if context_lens >= 4 and num >= context_lens * 0.5:
            new_context.insert(0, "(本页删除)本页在超过一半的段落中发现人名且符合参考文献的特征")
            return []
        elif mulu_num > 0:
            new_context.insert(0, "(本页删除)本页发现目录的特征")
            return []
        else:
            # 删除 new_context 中被标记为参考删除的 item
            new_context = [item for item in new_context if not re.search(r'参考删除', item)]
            return new_context

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


    def step7_is_shortpage(self,context):
        duanluo_num = len(context)
        short_duanluo_num = 0
        if duanluo_num <= 3:
            for item in context:
                if len(item.strip()) < 100:
                    short_duanluo_num += 1
            if short_duanluo_num > 1:
                context.insert(0, "(本页删除)本页的段落数量小于等于3且至少段落长度有2条以上在100以下")
                return []
        elif duanluo_num <= 5:
            for item in context:
                if len(item.strip()) < 80:
                    short_duanluo_num += 1
            if short_duanluo_num > 3:
                context.insert(0, "(本页删除)本页的段落数量小于等于5且至少段落长度有4条以上80以下")
                return []
        else:
            # 段落短
            for item in context:
                if len(item.strip()) < 50:
                    short_duanluo_num+=1
            if short_duanluo_num > duanluo_num * 0.7:
                context.insert(0, "(本页删除)本页有超过一半的段落长度小于50字符")   # 如果有很多标题怎么办，一个标题一段文字
                return []
        return context


def clean_text(context):
    split_token = "\n\n"

    # if lang == 'en':
    #     pattern_list = pattern_list_en

    result = []
    sp = speicalProces()
    """
    目前的顺序
    step1:删除页边角
    step2:删除图片页
    step3:解决多于换行
    step4:解决缺少换行
    step5:解决参考文献以及参考文献页
    正则替换  
    step6:ngram删除未替换的数字
    step7:删除短页
    """
    context = sp.step1_drop_Pagefooter(context)

    context = sp.step2_delete_photopage(context)

    context = post_process(context["text"])
    # context是一个以两个换行符为切割条件的列表
    context = context.split(split_token)
    # 多余换行
    context = sp.step3_more_linefeed(context)
    # 缺少换行
    context = sp.step4_lack_linefeed(context)

    # 判定参考文献
    context = sp.step5_removepage(context)
    # print(context)
    for item in context:
        item = item.strip(split_token).strip()

        if "## References" in item:
            continue
        for pattern_item in pattern_list:
            item = re.sub(pattern_item[0], pattern_item[1], item)
            item = item.strip()
        for pattern_item in context_pattern:
            item = re.sub(pattern_item[0], pattern_item[1], item)
        result.append(item)

    # print(result)
    # 使用NLP模型判断参考文献
    context = sp.step6_ngram_deletenum(result)
    # print(context)
    # 判断整页短路长短
    context = sp.step7_is_shortpage(context)

    # 数字判定


    context = split_token.join(context)
    return context


def post_process(context):
    context = context.strip(" ").strip("\n").strip(" ").strip("\n")
    # 消除分界符失效  --*- 前面需要有连续两个\n;
    context = re.sub('\n    --', "\n\n    --", context)
    # 消除空格问题
    context = re.sub(r'\n +\n', "\n\n", context)
    context = re.sub(r'\n +\n', "\n\n", context)
    # 去掉过多\n的情况
    context = re.sub("\n{2,}", "\n\n", context)

    # context = re.sub("[li][\.,]" , '1.' ,context)
    return context

def process_line(items, sp):
    item = json.loads(items.strip())
    context = clean_text(item, "en", sp)
    context = post_process(context)
    if len(context) < 100:
        return
    item["text"] = context
    item = json.dumps(item, ensure_ascii=False)
    return item




fw = open("C:/pycharm/orc识别pdf清洗数据/pdf/clean_json/medical_stage4_surya_preformat_8.jsonl", "w", encoding="utf-8")
with open("C:/pycharm/orc识别pdf清洗数据/pdf/clean_json/medical_stage4_surya_preformat.jsonl", "r", encoding="utf-8") as fs:
    for items in tqdm(fs.readlines()):
        item = json.loads(items.strip())
        # if item["seq_id"] == "bbad3368-6598-45ca-a478-adcae38d6af2":

        context = item
        # lang = item["lang"]

        context = clean_text(context)
        context = post_process(context)
        if len(context) < 100:
            continue
        item["text"] = context
        item = json.dumps(item, ensure_ascii=False)
        # print(item)
        fw.write(item + "\n")




# 文件路径
# input_file_path = "C:\\pycharm\\orc识别pdf清洗数据\\pdf\\clean_json\\guidelines_liangyong_surya_preformat_en.jsonl"
# output_file_path = "C:\\pycharm\\orc识别pdf清洗数据\\pdf\\clean_json\\guidelines_liangyong_surya_preformat_en_4.jsonl"
#
# # 读取所有记录
# with open(input_file_path, "r", encoding="utf-8") as fs:
#     lines = fs.readlines()
#     # # 随机抽取5000条记录
#     # sampled_lines = random.sample(lines, 5000)
# # 处理并保存抽取的记录
# with open(output_file_path, "w", encoding="utf-8") as fw:
#     for items in tqdm(lines):
#         item = json.loads(items.strip())
#         # if item["seq_id"] == "f7afd344-b77a-4e73-92f1-65eb9910689a":
#         context = item
#
#         # 清洗和处理文本
#         context = clean_text(context)
#         context = post_process(context)
#
#         if len(context) < 100:
#             continue
#
#         item["text"] = context
#         item = json.dumps(item, ensure_ascii=False)
#         # print(item)
#         fw.write(item + "\n")
