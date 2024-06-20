import json
import re
from tqdm import tqdm
import math
import spacy
import random
from nltk.corpus import wordnet
import inflect
inflect = inflect.engine()
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
    [r'([^\d][\.,]\s?)([1-9][0-9]{1,4}(\s{0,3}[\-–,\.]\s{0,3}[1-9][0-9]{1,4}){1,20})(\n|\s?[A-Z])',r'\1\4'],
    # 结尾句号后面为数字和序号区别开序号后面还有一个.
    [r'\.(\s?\d+)\n',r''],
    [r'(#{1,3})\n',r'\1']
 ]

context_pattern = [
    [r'(¬\s*)', r''],
    [r'(\(\s*\))', r'']
]

# nlp = spacy.load("en_core_web_trf")
nlp = spacy.load("en_core_web_sm")

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
        if img_box[2] - least_bbox[0] <= 80:
            return True
        # 检测下面边角
        elif img_box[3] - least_bbox[1] <= 80:
            return True
        # 检测左侧边角
        elif least_bbox[2] - img_box[0] <= 80:
            return True
        # 上边角会遇到标题这个问题，要不要解决？
        elif least_bbox[3] - img_box[1] <= 80:
            return True
        else:
            return False


    def step1_drop_Pagefooter(self, item):
        # print(json.dumps(item, ensure_ascii=False))
        """
        1.遍历最小的块判断是否为页边角
        2.在text中找到内容给删掉
        """
        raw_info = item['attr']['raw_info']
        img_box = item['attr']['img_box']
        for raw in raw_info:
            raw_context = raw['raw_context']
            for least_block in raw_context:
                least_bbox = least_block['bbox']
                if self.is_page_foot(least_bbox,img_box):
                    least_text = least_block['text']
                    # print(least_text)
                    # 对 least_text 进行正则转义
                    escaped_least_text = re.escape(least_text)

                    # 构建正则模式，匹配可能的前后空格、换行符和连字符
                    pattern = re.compile(escaped_least_text + r'[\s\n-]{0,5}')

                    # 使用正则表达式替换匹配的文本
                    item['text'] = re.sub(pattern, '', item['text'])

        # print(item)

        return item

    def delete_photopage(self,item):
        raw_info = item['attr']['raw_info']
        img_box = item['attr']['img_box']
        img_area = (img_box[2] - img_box[0])*(img_box[3] - img_box[1])
        all_block_area = []
        for raw in raw_info:
            full_blocks = raw['full_blocks']
            block_area = (full_blocks[2]-full_blocks[0])*(full_blocks[3]-full_blocks[1])
            all_block_area.append(block_area)

        if len(raw_info) <= 3 and sum(all_block_area) < img_area * 0.2:
            item['text'] = "(本页删除)此页的内容部分所占的比例小于0.2"+item['text']

        return item

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
                    item_sections[section_index] += " " + item_sections[section_index + 1].lstrip()
                    del item_sections[section_index + 1]

                elif re.search(r'^([\d+A-Z][\.,]){1,3}$', item_sections[section_index]) and \
                        item_sections[section_index + 1].lstrip()[0].isupper():  # 匹配段落中只有序号且下一段是大写开头的情况
                    item_sections[section_index] += " " + item_sections[section_index + 1].lstrip()
                    del item_sections[section_index + 1]

                elif any(item_sections[section_index].rstrip().endswith(" " + prep) for prep in
                         preposition_list):  # 匹配同一段中介词结尾的
                    item_sections[section_index] += " " + item_sections[section_index + 1].lstrip()
                    del item_sections[section_index + 1]

                elif item_sections[section_index].rstrip()[-1] in ['-']:
                    item_sections[section_index] += " " + item_sections[section_index + 1].lstrip()
                    del item_sections[section_index + 1]

                elif "#" not in item_sections[section_index] and "*" not in item_sections[section_index] and re.search(
                        r'[^\.?!]$', item_sections[section_index]) and re.match(r'^[a-z]', item_sections[
                    section_index + 1].lstrip()):
                    item_sections[section_index] += " 段内删除换行-5 " + item_sections[section_index + 1].lstrip()
                    del item_sections[section_index + 1]

                elif re.search(r'\([^\)]*$|\[[^\]]*$', item_sections[section_index]) and re.match(r'^[^\(\[]*[\)\]]',
                                                                                                  item_sections[
                                                                                                      section_index + 1]):  # 前一个段落有一个未对应的左括号，下一段前面有一个与之对应的右括号
                    item_sections[section_index] += " " + item_sections[section_index + 1].lstrip()
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
                if stripped_item and (stripped_item[0].islower() or stripped_item[0] in ["(", "[", ")", "]", "."]):
                    # 上一段不能出现#，出现#证明是标题段
                    if not re.search(r'#',context[index - 1]):
                        # 合并到前一个 item
                        context[index - 1] = context[index - 1].rstrip() + " " + item.lstrip()
                        # 删除当前 item
                        del context[index]
                        # 继续检查当前索引位置的元素
                        index = index - 1
                        continue

                # 新增条件: 如果 stripped_item 结尾的单词在 preposition_list 中
                elif any(stripped_item.rstrip().endswith(" " + prep) for prep in preposition_list):
                    if index + 1 < len(context):
                        # 合并到下一个 item
                        context[index] = item.rstrip() + " " + context[index + 1].lstrip()
                        # 删除下一个 item
                        del context[index + 1]
                        # 不增加 index, 继续检查当前索引位置的元素
                        index = index - 1
                        continue

                elif stripped_item[-1] == '-':
                    if index + 1 < len(context):
                        # 合并到下一个 item
                        context[index] = item.rstrip() + " " + context[index + 1].lstrip()
                        # 删除下一个 item
                        del context[index + 1]
                        # 不增加 index, 继续检查当前索引位置的元素
                        index = index - 1
                        continue

                elif "#" not in item and re.search(r'[^\.?!:：”"]$', item.strip()):

                    if index + 1 < len(context) and "#" not in context[index + 1]:
                        # 合并到下一个 item
                        context[index] = item.rstrip() + " " + context[index + 1].lstrip()
                        # 删除下一个 item
                        del context[index + 1]
                        # 不增加 index, 继续检查当前索引位置的元素
                        index = index-1
                        continue

            index += 1
        # print("After processing:", context)
        return context

    def step3_lack_linefeed(self,context):
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
                # 如果是一个网站怎么办  www.sadadssa.com
                # elif re.search(r'([\.?!]\s)([a-z])',part):
                #     # 在句末标点符号（。？！...）后面接小写字母的情况进行换行
                #     part = re.sub(r'([\.?!]\s)([a-z])', r'\1\n增加换行\2', part)
                #     new_parts.append(part.strip() + '\n')

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

    def step4_rm_cite(self, item):
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
        cite_year = 1 if len(re.findall(r'\[\d\d\d\d\]', item) or re.findall(r'\.\s?\b\d{4}\b',item) or re.findall(r'\b\d{4}\b\s?;',item)) else 0      # 年份，比如 . 2010 、 2010;
        cite_page = 1 if len(re.findall(r'\d+\s?:\d+\s?[–-]\s?\d+',item)) else 0
        cite_J = 1 if len(re.findall(r'\[[Jj]\]', item)) else 0
        cite_doi = 1 if " doi " in item else 0
        cite_etal = 1 if " et al" in item else 0
        cite_vol = 1 if " vol. " in item else 0
        # cite_page = 1 if len(re.search(r'\.\s?\b\d{4}\b',item)) else 0
        cite_phonenum = 1 if re.search(r" [Pp]hone:|Fax:", item) else 0
        cite_tag = [cite_index, cite_year, cite_J, cite_doi, cite_etal, cite_page, cite_vol, cite_phonenum]
        if sum(cite_tag) > 1:
            return "参考删除-0:<u>{}</u>".format(item)

        person_block, person_num = self.get_person_idx(item)
        # 超过5个人名
        person_block_lens = [block_item[1] - block_item[0] for block_item in person_block]
        person_lens = sum(person_block_lens)
        if person_lens / len(item) > 0.5 and len(item) > 100:
            return "参考删除-1:<u>{}</u>".format(item)
        if person_num > 5:
            return "参考删除-2:<u>{}</u>".format(item)
        # elif cite_index and person_num > 0:
        #     return "参考删除-3:<u>{}</u>".format(item)
        else:
            return item


    def is_plural(self, word):
        # 统一为小写进行比较
        word = word.strip().lower()

        # 如果是特定的单位，且不在单数列表中，则认为是复数
        if word in ['million','mm','cm','m','km','mg','g','kg','billion','Percent','percent','ratio','light-years','million', 'billion', 'cm', 'm', 'km', 'mg', 'g', 'kg', 'percent', 'ratio',
                    'dollar', 'yen', 'pound', 'peso', 'rand','baht', 'meter', 'metre', 'decimeter', 'liter', 'litre', 'gallon','dozen', 'score', 'series', 'species', 'headquarters', 'works',
                    'information', 'rice', 'money', 'advice', 'equipment', 'machinery','cannon', 'graffiti', 'pollen', 'offspring', 'bream', 'herring','shears', 'decade', 'century', 'year',
                    'month', 'hair', 'debris','research', 'piano', 'trombone','horse','day']:
            return True

        # 尝试获取单词的单数形式
        singular_form = inflect.singular_noun(word)

        # 如果没有单数形式，或者单数形式与原单词不同，则认为是复数
        if singular_form == False:
           return False
        elif singular_form != word:
            return True

        return False

    def check_number(self,context):
        new_context = []
        for item in context:
            # 正则表达式匹配数字或数字范围及其后面的单词
            pattern = re.compile(r'[^\d](\b[\d]{1,3}(?:[,\.]\d{1,3})*(\s*(?:or|and|to|:|：|with|of|-)\s*[\d]{1,3}(?:[,\.]\d{1,3})*){0,3}\b)\s+(\w+)')

            matches = pattern.findall(item)

            for number,kongbuhuozu,word in matches:
                # print(number,word)
                # 复数不做处理，否则做处理
                if not self.is_plural(word):
                    # print(number,word)
                    item = re.sub(rf'\b({re.escape(number)})(\s+{re.escape(word)})\b', r'检查复数删除:<u>\1</u>\2',item)
            new_context.append(item)
        return new_context

    def step4_removepage(self, context):
        # context 是一个列表，每个 item 是一段内容
        context_lens = len(context)
        # 用于统计有多少个段落中出现了人名
        num = 0
        new_context = []
        for item in context:
            # 返回的item是已经被重写过的item
            item = self.step4_rm_cite(item)
            # 新的item重新加入一个新的列表
            new_context.append(item)
            # 判断item是否被判定未参考文献
            if re.search(r'参考删除',item):
                # 如果当前段落中有人名且符合参考文献的特征
                num += 1
        # 对整页的一个判断
        if context_lens >= 4 and num >= context_lens * 0.5:
            new_context.insert(0, "(本页删除)本页在超过一半的段落中发现人名且符合参考文献的特征")
        return new_context


    def step5_is_shortpage(self,context):
        duanluo_num = len(context)
        short_duanluo_num = 0
        if duanluo_num <= 3:
            for item in context:
                if len(item.strip()) < 100:
                    short_duanluo_num += 1
            if short_duanluo_num > 1:
                context.insert(0, "(本页删除)本页的段落数量小于等于3且至少段落长度有2条以上在100以下")
        elif duanluo_num <= 5:
            for item in context:
                if len(item.strip()) < 80:
                    short_duanluo_num += 1
            if short_duanluo_num > 3:
                context.insert(0, "(本页删除)本页的段落数量小于等于5且至少段落长度有4条以上80以下")
        else:
            # 段落短
            for item in context:
                if len(item.strip()) < 50:
                    short_duanluo_num+=1
            if short_duanluo_num > duanluo_num * 0.7:
                context.insert(0, "(本页删除)本页有超过一半的段落长度小于50字符")   # 如果有很多标题怎么办，一个标题一段文字
        return context


def clean_text(context, lang):
    split_token = "\n\n"

    # if lang == 'en':
    #     pattern_list = pattern_list_en

    result = []

    sp = speicalProces()
    """
    目前的顺序
    1.删除页脚
    新加 根据块的面积来判断此页内容为图片的描述  删除此页
    2.解决换行的问题包括多于换行、缺少换行
    3.判定参考文献
    4.正则替换
    5.判断整页长短问题
    """
    context = sp.step1_drop_Pagefooter(context)

    context = sp.delete_photopage(context)

    context = post_process(context["text"])
    # context是一个以两个换行符为切割条件的列表
    context = context.split(split_token)
    # 多余换行
    context = sp.step2_more_linefeed(context)
    # 缺少换行
    context = sp.step3_lack_linefeed(context)

    # 判定参考文献
    context = sp.step4_removepage(context)
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
    # 使用NLP模型判断参考文献

    # 判断整页短路长短
    context = sp.step5_is_shortpage(result)

    # 数字判定
    # context = sp.check_number(context)

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



fw = open("C:\pycharm\orc识别pdf清洗数据\pdf\clean_json\medical_stage4_surya_preformat_6.jsonl", "w",encoding="utf-8")
with open("C:\pycharm\orc识别pdf清洗数据\pdf\clean_json\medical_stage4_surya_preformat.jsonl", "r",encoding="utf-8") as fs:
    for items in tqdm(fs.readlines()):
        item = json.loads(items.strip())
        # if item["seq_id"] == "c2f61d69-f1e9-4016-981a-60737def4dbe":

        context = item
        # lang = item["lang"]

        context = clean_text(context, "en")
        context = post_process(context)
        if len(context) < 100:
            continue
        item["text"] = context
        item = json.dumps(item, ensure_ascii=False)
        # print(item)
        fw.write(item + "\n")
#



# # 文件路径
# input_file_path = "C:\\pycharm\\orc识别pdf清洗数据\\pdf\\clean_json\\guidelines_liangyong_surya_preformat_en.jsonl"
# output_file_path = "C:\\pycharm\\orc识别pdf清洗数据\\pdf\\clean_json\\guidelines_liangyong_surya_preformat_en_2_5000.jsonl"
#
# # 读取所有记录
# with open(input_file_path, "r", encoding="utf-8") as fs:
#     lines = fs.readlines()
#     # 随机抽取5000条记录
#     sampled_lines = random.sample(lines, 5000)
# # 处理并保存抽取的记录
# with open(output_file_path, "w", encoding="utf-8") as fw:
#     for items in tqdm(sampled_lines):
#         item = json.loads(items.strip())
#         # if item["seq_id"] == "f7afd344-b77a-4e73-92f1-65eb9910689a":
#         context = item
#
#         # 清洗和处理文本
#         context = clean_text(context, "en")
#         context = post_process(context)
#
#         if len(context) < 100:
#             continue
#
#         item["text"] = context
#         item = json.dumps(item, ensure_ascii=False)
#         # print(item)
#         fw.write(item + "\n")



