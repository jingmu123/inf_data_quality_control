import json
import re
from tqdm import tqdm
import math


pattern_list_en = [

    # 去除带有网址的句子
    [r'([^\n\.]*(([Ww]{2,3}\.)|(\.[Cc][Oo][Mm])|(\d+\.html))[^\n]*)', r'删除10:<u>\1</u>'],
    [r'([^\.?\n]*\(?\s*https?://[^\s]+\s*\)?[^\.?\n]*)', r'删除12:<u>\1</u>'],
    [r'([^\.\n]*\b(?:[Ww]{2,3}\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b[^\n\.]*)', r'删除13:<u>\1</u>'],
    [r'(\n\s*[a-zA-Z\.]\s*\n)', r'删除15:<u>\1</u>'],
    [r'([^\n]*Copyright[^\n]*)', r'删除18:<u>\1</u>'],

    # 参考文献
    [r'(Circulation\s*\d{4},\s*\d+:[A-Z0-9-]*\s*[Dd]oi:\s*[A-Z0-9-.//]*\s*^([A-Z][a-z]*))', r'删除14:<u>\1</u>'],
    [r'([^\n]*([A-Z]+\w+)\s*[A-Z]*\w*\.?(\s*\d+?\s*(?:-\d+)*,?)?(\d+;)?\s*\d{4}\s*[,;]\s*(((\d+\s*(\(\d+\))?:)|(\s*\b[Pp]p\b\s*[:.]?))\s*\d+(?:[-;–]\d+)+)?[^\n]*)',r'删除8:<u>\1</u>'],
    [r'([^\n]*[A-Z]\w+,\s*[A-Z]\.\s*[A-Za-z()\.&,]*[^\\n]*\d{4}[^\n]*)', r'删除7:<u>\1</u>'],
    [r'([^\[\.]*[Pp]age[s]?\s*\d+(-\d+)?.*?[\.\]])', r'删除9:<u>\1</u>'],
    [r'(ISBN\s*[A-Z0-9-]*)', r'删除19:<u>\1</u>'],

    # 带特殊符号的无关内容
    [r'(👍|▶|●|©|®|([^\n]*↑[^\n]*)|†|¶|║|§|∧|™|■|❏|□|✓|✔)', r'删除0:<u>\1</u>'],

    # 句末数字引用
    ##1.带括号 book (1，2).
    # [r'[^0-9]\.']
    [r'([^0-9]\.)(\s*\(\d+\s*(?:[-,;–.]\d+)*\)\s*)([\n.A-Z])', r'删除1:<u>\2</u>'],
    ##2.不带括号但是数字前是句号. 数字后是换行或者大写字母
    [r'([^0-9]\.)(\s*\d+\s*(?:[-,;–.]\d+)*)(?=$)', r'删除2:<u>\2</u>'],
    ##3.带括号(30° downward approximately).(5.19)
    [r'((\.)(\s*\(\s*\d+\s*(?:[-,;–.]\s*\d+\s*)*\))([A-Z\n.]))', r'删除3:<u>\2</u>'],

    # 无关图片引用
    [r'((\()\b([F|f]igure[s]?|Section|diagram|Appendix|Box|[Ss]ource[s]?|Fig|p)\b:?\.?\s*(\d+)?\.?.*?(\)))',
     r'删除5:<u>\1</u>'],
    [r'([^\n\.]*\b(Fig[s]?[ure]?[s]?)\b\.?[\s* ](\d+)?\.?[^\n]*)', r'删除4:<u>\1</u>'],

    # 句首无关数字
    [r'(([^0-9]\.)(\s*\d+(?:\s*[-;,–.]\s*\d+\s*)*\s*)([A-Z]))', r'删除6:<u>\2</u>'],

 ]

context_pattern = [
    [r'(¬\s*)', r'删除16:<u>\1</u>'],
    [r'(\(\s*\))', r'删除17:<u>\1</u>']
]


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
                #print(down_max)

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
            if len(nums[fast]) ==0:
                fast = fast + 1
                continue
            try:
                if (nums[slow].endswith("and") or nums[slow].endswith("of") or nums[slow].endswith("any") or nums[
                    slow].endswith("a") or nums[slow].endswith("is") or nums[slow].endswith("for") or nums[slow].endswith(
                    "the") or nums[slow].endswith("or") or nums[slow].endswith(",")) and self.is_not_upper(nums[fast][0]):

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
                print(nums[slow],"|{}|".format(nums[fast]))
                raise Exception
        for idx,item in enumerate(nums[0:slow + 1]):
            if item.count("|") > 5:
                item = item.replace("--huan hang ti huan fu hao--", "\n")
            item = re.sub(r'([\.?!:]"?)--huan hang ti huan fu hao--', r'\1\n', item)
            nums[idx] = item.replace("--huan hang ti huan fu hao--", " ")
        return nums[0:slow + 1]


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

    context = split_token.join(result)
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


fw = open("../../../../full_data/medical_stage4_surya/medical_stage4_surya_clean.jsonl", "w", encoding="utf-8")
with open("../../../../full_data/medical_stage4_surya/medical_stage4_surya_preformat.jsonl", "r", encoding="utf-8") as fs:
    for items in tqdm(fs.readlines()):
        item = json.loads(items.strip())
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




