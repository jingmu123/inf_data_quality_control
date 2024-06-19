import json
import re
from pprint import pprint

from tqdm import tqdm

log_dict = {}
# 规则必须以列表形式存储，分别是要替换的内容，以及替换成什么内容
pattern_list = [
    [r'（[^（）]*(?:[参详][细照见与考阅看加情]|点击|见[下])[^（）]*）', ''],  # 清除带（）参考详见信息
    [r'\([^\(）为]*(?:[参详][细照见与考阅看加情]|点击|见[下])[^\)\(列]*\)', ''],  # 清除带()参考详见信息
    [r'（[^（）]*图[^（）]*示[^（）]*）', ''],  # 清除图示内容
    [r'\([^\(\)\n]*详见[^\)\(\n]*\)', ''],  # 清除详见内容 括号为英文
    [r'\(?[\u4e00-\u9fa5\d\.【】]*参阅[\u4e00-\u9fa5：， \d\w\/【】]*\)', ''],  # 清除带(参阅) 文本的信息
    [r'\|', ''],  # 删除|
    [' {2,}', ' '] , # 删除多个空格
    [r'\\?\"?target=\\?\"?_blank>?',''],#删除带target的无关文本
    [r'\[\d+\]',''],#删除[02]文本
    [r'（如?上?下?面?左?[^（，电意]*(图|表\d)[ ，示]*?片? ?[\d\w]?\d? ?）',''], #删除带图表关键字样的内容
    [r'（见\[[^）]*?\]）',''],#删除（见[注意事项]）的类似文本
]

# （可以点击「早泄」词条查看更多内容）
context_pattern = [
    # ['', ''],
    # ['。。', ''],
    # ['，，', ''],
    # ['。，', ''],
    # ['，。', ''],
    # ['、、', '、'],
    # ['、。', '。'],
    # ['。.2。。', '。']
    ['（见\\u6CE8意事项\\uFF09', ''],
    [' ',''],

]


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


class speicalProces:
    def __init__(self):
        pass


def clean_text(context, lang="zh"):
    # 如果存在特殊处理，以类的方式整合，初始化类；
    sp = speicalProces()
    split_token = "\n\n"
    if split_token not in context:
        split_token = "\n"
    result = []
    for item in context.split(split_token):
        # 1.正则
        for pattern_item in pattern_list:
            if re.findall(pattern_item[0], item) != []:
                if str(pattern_item[0]) not in log_dict:
                    log_dict[str(pattern_item[0])] = re.findall(pattern_item[0], item)
                else:
                    log_dict[str(pattern_item[0])] = log_dict[str(pattern_item[0])] + re.findall(pattern_item[0], item)
            item = re.sub(pattern_item[0], pattern_item[1], item)

        for replace_item in context_pattern:
            item = item.replace(replace_item[0], replace_item[1])
        result.append(item)
    context = split_token.join(result)
    # 2.替换 固定内容（非泛化）


    return context


fw = open("../../../../full_data/drug_detail_zh/drug_detail_zh_clean.jsonl", "w", encoding="utf-8")
with open("../../../../full_data/drug_detail_zh/drug_detail_zh_preformat.jsonl", "r", encoding="utf-8") as fs:
    for items in tqdm(fs.readlines()):
        item = json.loads(items.strip())
        context = item["text"]
        context = clean_text(context)
        # context = post_process(context)
        item["text"] = context

        item = json.dumps(item, ensure_ascii=False)
        fw.write(item + "\n")
    print(log_dict.keys())
    for i in log_dict.keys():
        pprint(log_dict[i])
