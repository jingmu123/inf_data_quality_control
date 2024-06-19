import json
import re
from pprint import pprint
from tqdm import tqdm
import Levenshtein

log_dict = {}#[^_\\a-zA-Z: \.,*\d~®\-><}&@=\]' !;\)\(\?\+%\/"#]\\n
# 规则必须以列表形式存储，分别是要替换的内容，以及替换成什么内容
pattern_list = [
    [r'\n(\w+)\n',r'\1'],#删除\n+英文+\n组合

    [r'\[.\]', ''],  # 删除[]和里面的内容
    [r'(:) *\n(_+)', r'\1\2'],  # 去除: \n___这种中间空格
    [r'([a-zA-Z] *?)\n( *?[a-zA-Z\(\)\"{\-},\^\/\+\(\): @×\]\[`±½\$\*;<=>\?\&¯´\#%°\'~!·\]\|])', r'\1 \2'],  # 对两个英文中间\n去除
    [r'([a-zA-Z] *?)\n( *?\d+[^\.])', r'\1\2'],  # 对英文\n非序号组合去除换行
    [r'(\d+ *)\n( *\d+)',r'\1\2'], #删除数字中间的空格
    [r'( *?\d+[^\.])\n([a-zA-Z] ?)', r'\1\2'],
    # [r'(\n *\.+ *\n)+', r'\n'],  # 清洗标点符号
    [r'\n\?', ' '],  # 删除开头的?
    [r'It was a pleasure[^\.!]*[\.!]', ''],  # 删除无关文本
    [r'oMore information can be found at ___', ''],  # 删除无关文本
    [r' {2,}', ' '],  # 将多个空格替换成一个
    [r"([^:.])[\"{\-}\^\., \/\+@×\]\[`±½\$\*;<=>\?\&¯´\#%°'~!·\]\|]\n([^\d\n])",r'\1\2'],#删除\n带特殊标点符号的组合
    # [r'(_+ *)\n([^_])',r'\1\2'],#
    # [r'([^_])\n(_+ *)',r'\1\2'],#
    # [r"[^\w\s\"_{\-} ,\^\. \/\+\(\): @×\]\[`±\\n½\$\*;<=>\?\&¯´\#%°'~!·\]\|]",''] 检测代码
    # [r'(.{2,8}( )\n([^\d+\n]).{2,8})',r'\1']  检测代码

]

# 单个的无关文本替换
context_pattern = [
    ['. .', '. '],
]


def post_process(context):
    context = context.strip(" ").strip("\n").strip(" ").strip("\n")
    # 消除分界符失效  --*- 前面需要有连续两个\n;
    context = re.sub('\n    --', "\n\n    --", context)
    # 消除空格问题
    context = re.sub(r'\n +\n', "\n\n", context)
    # 去掉过多\n的情况
    context = re.sub("\n{2,}", "\n\n", context)
    return context


class speicalProces:
    def __init__(self):
        pass

    def clean_n_pre(self, context):  # \n\n为数据分割符号,对数据进行预处理
        pattern_list = [
            [r'\n +\n', r'\n\n'],  # 删除空格
            [r'\n+ *(?:<br>)?\n+', r'\n\n'],  # 数据分割
            # [r' *\. *\n *\. *\n',r'.\n\n'],# 清洗标点符号

            [r'(\.* *)\n+[~=\. *]+\n+',r'.\n\n'],#删除多余的符号
            ['[\x80-\x9e¢®¿£¬©¨¸\xad¶¡¦§]+','']
        ]
        for pattern_item in pattern_list:
            context = re.sub(pattern_item[0], pattern_item[1], context)
        return context


def clean_text(context, lang="zh"):
    # 如果存在特殊处理，以类的方式整合，初始化类；
    sp = speicalProces()
    context = sp.clean_n_pre(context)
    split_token = "\n\n"
    if split_token not in context:
        split_token = "\n"
    result = []
    for item in context.split(split_token):

        # 1.正则
        for pattern_item in pattern_list:
            # if re.findall(pattern_item[0], item) != []:  # 检测模块，会消耗较多时间
            #     if str(pattern_item[0]) not in log_dict:
            #         log_dict[str(pattern_item[0])] = re.findall(pattern_item[0], item)
            #     else:
            #         log_dict[str(pattern_item[0])] = log_dict[str(pattern_item[0])] + re.findall(pattern_item[0], item)
            item = re.sub(pattern_item[0], pattern_item[1], item)
        # 2.文本替换
        for replace_item in context_pattern:
            item = item.replace(replace_item[0], replace_item[1])

        result.append(item)
    context = split_token.join(result)
    return context


clean_number = 0  # 清洗量
fw = open(f"../../../../full_data/mimic_iv_discharge/mimic_iv_discharge" + "_clean.jsonl", "w", encoding="utf-8")
with open("../../../../full_data/mimic_iv_discharge/mimic_iv_discharge" + "_preformat.jsonl", "r",
          encoding="utf-8") as fs:
    for items in tqdm(fs.readlines()):
        item = json.loads(items.strip())
        context = item["text"]
        context = clean_text(context)
        # context = post_process(context)
        item["text"] = context
        clean_number += 1
        if clean_number > 1000000:
            break

        item = json.dumps(item, ensure_ascii=False)
        fw.write(item + "\n")
    # print(log_dict.keys())  # 打印log等内容
    # for i in log_dict.keys():
    #     if i in [r'(:) *\n(_+)',r'(:) *(\n_+)', r'\[.\]', r'( )\n([^\d+\n])', r'\1\2',r'oMore information can be found at ___',r'It was a pleasure[^\.!]*[\.!]',r'(\n *\.+ *\n)+',r'([a-zA-Z] *?)\n( *?[a-zA-Z])',r'\n\?',r'([a-zA-Z] )\n( *?\d+[^\.])',r' {2,}',r'( *?\d+[^\.])\n([a-zA-Z] ?)']:
    #         pass
    #     else:
    #         pprint(log_dict[i])
