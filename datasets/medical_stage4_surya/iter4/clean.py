import json
import re
from tqdm import tqdm
import math
import spacy


pattern_list_en = [


    # [r'([^\n\.]*(([Ww]{2,3}\.)|(\.[Cc][Oo][Mm])|(\d+\.html))[^\n]*)', r'删除10:<u>\1</u>'],
    # [r'([^\.?\n]*\(?\s*https?://[^\s]+\s*\)?[^\.?\n]*)', r'删除12:<u>\1</u>'],
    # [r'([^\.\n]*\b(?:[Ww]{2,3}\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b[^\n\.]*)', r'删除13:<u>\1</u>'],
    # 去除带有网址的句子,关键词   www、com、html、http
    # todo www,http放一起考虑，右边界的准确性需要考虑
    # todo com,html放一起考虑，左边界需要考虑
    [r'([^\.\n]*(([Ww]{2,3}\.)|(\.[Cc][Oo][Mm])|(http)|(\.html))[^\n]*)',r'删除10:<u>\1</u>'],

    [r'(\n\s*[a-zA-Z\.]\s*\n)', r'删除15:<u>\1</u>'],
    [r'([^\n]*Copyright[^\n]*)', r'删除18:<u>\1</u>'],

    # 参考文献

    [r'(Circulation\s*\d{4},\s*\d+:[A-Z0-9-]*\s*[Dd]oi:\s*[A-Z0-9-.//]*\s*^([A-Z][a-z]*))', r'删除参考文献:<u>\1</u>'],
    [r'([^\n]*([A-Z]+\w+)\s*[A-Z]*\w*\.?(\s*\d+?\s*(?:-\d+)*,?)?(\d+;)?\s*\d{4}\s*[,;]\s*(((\d+\s*(\(\d+\))?:)|(\s*\b[Pp]p\b\s*[:.]?))\s*\d+(?:[-;–]\d+)+)?[^\n]*)',r'删除参考文献:<u>\1</u>'],
    [r'([^\n]*[A-Z]\w+,\s*[A-Z]\.\s*[A-Za-z()\.&,]*[^\\n]*\d{4}[^\n]*)', r'删除参考文献:<u>\1</u>'],
    [r'([^\[\.]*[Pp]age[s]?\s*\d+(-\d+)?.*?[\.\]])', r'删除参考文献:<u>\1</u>'],


    [r'(ISBN\s*[A-Z0-9-]*)', r'删除19:<u>\1</u>'],



    # 带特殊符号的无关内容
    [r'(👍|▶|●|©|®|([^\n]*↑[^\n]*)|†|¶|║|§|∧|™|■|❏|□|✓|✔)', r'删除0:<u>\1</u>'],




    # 无关文本
    # 无关图片引用
    [r'((\()\b([F|f]igure[s]?|Section|diagram|Appendix|Box|[Ss]ource[s]?|Fig|p)\b:?\.?\s*(\d+)?\.?.*?(\)))',r'删除5:<u>\1</u>'],
    [r'([^\n\.]*\b(Fig[s]?[ure]?[s]?)\b\.?[\s* ](\d+)?\.?[^\n]*)', r'删除4:<u>\1</u>'],

    # 数字引用
    ##1.带括号 book (1，2).
    # [r'[^0-9]\.']
    # [r'([^0-9]\.)(\s*\(\d+\s*(?:[-,;–.]\d+)*\)\s*)([\n.A-Z])', r'删除1:<u>\2</u>'],
    [r'(\([\d\s,\.–]{1,20}\))',r'删除1:<u>\1</u>'],

    ##2.不带括号但是数字前是句号. 数字后是换行或者大写字母
    # [r'([^0-9]\.)(\s*\d+\s*(?:[-,;–.]\d+)*)(?=$)', r'删除2:<u>\2</u>'],
    # 不带括号
    [r'([^\d])(\d{1,3}(\s?[–,]\s?\d{1,3}){1,4})([^\d])',r'\1删除2:<u>\2</u>'],
    # 不带括号数字或数字加点（容易误删）
    [r'([\.,])(\s\d+([,\.]\d+){0,5})',r'\1删除3:<u>\2</u>'],




    # 句首无关数字
    # [r'([^\d]\.)([\d+\.\s–]{3,10})(\s?[A-Z])',r'\1删除6:<u>\2</u>\3']
    # 如果不是居首

 ]

context_pattern = [
    [r'(¬\s*)', r'删除16:<u>\1</u>'],
    [r'(\(\s*\))', r'删除17:<u>\1</u>']
]

nlp = spacy.load("en_core_web_sm")
def NIL_tool(nlp,item):
    """
    :param item:传入的是context中最小单位，是一段话
    :return:
    person_num这段话有多少名字
    names_start2stop二维列表[[start,stop],[start,stop]...]
    """
    doc = nlp(item)
    person_num = 0
    names_start2stop = []
    for ent in doc.ents:
        name_start2stop = []
        if ent.label_ == "PERSON":
            person_num += 1
            name_start2stop.append(ent.start_char)
            name_start2stop.append(ent.end_char)
            names_start2stop.append(name_start2stop)


    return person_num, names_start2stop

# def step5_2_isreference(item,person_num,names_start2stop):
#     len_item = len(item)
#     len_names = 0
#     for name in names_start2stop:
#         len_name = name[1] - name[0]
#         len_names += len_name
#
#     # 有人名,有\d+-\d+
#     if person_num and re.search("\d+\s?[-]{1,3}\s\d+",item):
#         return True
#     # 有人名，有年份一定是四位数字
#     elif person_num and re.search("\s\d{4}[^\d]",item) and re.search("^\d+\.",item):
#         return True
#     elif person_num >= 10:
#         return True
#     elif person_num >= 5 and len_names > len_item * 0.3:
#         return True
#     elif person_num >= 3 and len_names > len_item * 0.5:
#         return True
#     elif len_names > len_item * 0.2:
#         return True
#     else:
#         return False

class speicalProces:
    def __init__(self):
        pass

    def is_not_upper(self, char):
        return not char.isupper()

    # 去除左右侧栏
    def step1_drop_Sidebar(self, item):
        left_min, right_max = math.inf, 0
        text_boundary = []
        for dic in item["attr"]["raw_info"]:
            text_boundary.append(len(dic["raw_context"]))
        k = sorted(text_boundary)[int(len(text_boundary) // 2)]
        if k > 12:
            k = 12
        for dic in item["attr"]["raw_info"]:
            if len(dic["raw_context"]) >= k and dic["full_blocks"][2] > right_max:
                right_max = dic["full_blocks"][2]
            if len(dic["raw_context"]) >= k and dic["full_blocks"][0] < left_min:
                left_min = dic["full_blocks"][0]
        for dic in item["attr"]["raw_info"]:
            if dic["full_blocks"][0] > right_max or dic["full_blocks"][2] < left_min:
                for dic_text in dic["raw_context"]:
                    item["text"] = item["text"].replace(dic_text["text"], "")
                    item["text"] = item["text"].replace(dic_text["text"].strip("-"), "")
        return item

    # 去除页脚
    def step2_drop_Pagefooter(self, item):
        down_max = 0
        text_boundary = []

        for dic in item["attr"]["raw_info"]:
            text_boundary.append(len(dic["raw_context"]))
        k = sorted(text_boundary)[int(len(text_boundary) // 2) - 1]

        for dic in item["attr"]["raw_info"]:
            if len(dic["raw_context"]) >= k and dic["full_blocks"][3] > down_max:
                down_max = dic["full_blocks"][3]
                # print(down_max)

        for dic in item["attr"]["raw_info"]:
            # len
            if dic["full_blocks"][1] > down_max:
                for dic_text in dic["raw_context"]:
                    item["text"] = item["text"].replace(dic_text["text"], "")
                    item["text"] = item["text"].replace(dic_text["text"].strip("-"), "")

        return item

    def step3_removeLinefeed(self, nums):  # 去除多余换行
        for index in range(len(nums)):
            # print(num[index])
            nums[index] = (nums[index]).replace("\n", "--huan hang ti huan fu hao--").strip()
        slow, fast = 0, 1
        while fast < len(nums):
            nums[slow] = nums[slow].strip()
            nums[fast] = nums[fast].strip()
            if len(nums[fast]) == 0:
                fast = fast + 1
                continue
            try:
                if (nums[slow].endswith("and") or nums[slow].endswith("of") or nums[slow].endswith("any") or nums[
                    slow].endswith("a") or nums[slow].endswith("is") or nums[slow].endswith("for") or nums[
                        slow].endswith(
                    "the") or nums[slow].endswith("or") or nums[slow].endswith(",")) and self.is_not_upper(
                    nums[fast][0]):

                    nums[slow] = nums[slow] + " " + nums[fast]
                elif "#" not in nums[slow] and "*" not in nums[slow] and re.match(r'.*[a-z0-9-,:"]$', nums[slow]) and (
                        re.match(
                            r'^[a-z-,]', nums[fast])):

                    nums[slow] = nums[slow] + " " + nums[fast]
                else:
                    slow = slow + 1
                    nums[slow] = nums[fast]
                fast = fast + 1
            except:
                print(nums[slow], "|{}|".format(nums[fast]))
                raise Exception
        for idx, item in enumerate(nums[0:slow + 1]):
            if item.count("|") > 5:
                item = item.replace("--huan hang ti huan fu hao--", "\n")
            item = re.sub(r'([\.?!:]"?)--huan hang ti huan fu hao--', r'\1\n', item)
            nums[idx] = item.replace("--huan hang ti huan fu hao--", " ")
        return nums[0:slow + 1]

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


    def step5_1_removepage(self, context):
        # context 是一个列表，每个 item 是一段内容
        context_lens = len(context)
        # 用于统计有多少个段落中出现了人名
        num = 0
        # new_context = []
        for item in context:
            person_num, names_start2stop = NIL_tool(nlp,item)

            # 判断句子中人名占句子总体比例来判断句子是否为参考文献
            # if step5_2_isreference(item,person_num,names_start2stop):
            #     # item重写
            #     item = fr'整段删除参考文献:<u>{item}</u>'
            #     new_context.append(item)
            # else:
            #     new_context.append(item)

            if re.search(r'删除参考文献',item) and person_num >= 1:
                # 如果当前段落中有人名且符合参考文献的特征
                num += 1
        if num >= context_lens * 0.5:
            context.insert(0, "本页在超过一半的段落中发现人名且符合参考文献的特征")
        return context


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
        else:
            # 段落短
            for item in context:
                if len(item.strip()) < 50:
                    short_duanluo_num+=1
            if short_duanluo_num > duanluo_num * 0.5:
                context.insert(0, "本页有超过一半的段落长度小于50字符")   # 如果有很多标题怎么办，一个标题一段文字
        return context


def clean_text(context, lang):
    split_token = "\n\n"

    if lang == 'en':
        pattern_list = pattern_list_en

    result = []

    sp = speicalProces()

    context = sp.step1_drop_Sidebar(context)
    context = sp.step2_drop_Pagefooter(context)
    context = post_process(context["text"])
    context = context.split(split_token)
    # print(context)

    context = sp.step3_removeLinefeed(context)

    context = sp.step4_linefeed(context)


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
    context = sp.step5_1_removepage(result)


    context = sp.step6_is_shortpage(context)
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
    return context


fw = open("C:\pycharm\orc识别pdf清洗数据\pdf\clean_json\medical_stage4_surya_preformat_4.jsonl", "w", encoding="utf-8")
with open("C:\pycharm\orc识别pdf清洗数据\pdf\clean_json\medical_stage4_surya_preformat.jsonl", "r", encoding="utf-8") as fs:
    for items in tqdm(fs.readlines()):
        item = json.loads(items.strip())
        # if item["seq_id"] == "24adf16c-e17b-44a5-a4b9-a3a49bff444d":
            # print(item)
        context = item
        # lang = item["lang"]


        context = clean_text(context, "en")
        context = post_process(context)
        if len(context) < 100:
            continue
        item["text"] = context
        item = json.dumps(item, ensure_ascii=False)
        fw.write(item + "\n")




