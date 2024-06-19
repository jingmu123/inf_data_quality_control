import json
import re
from pprint import pprint

from tqdm import tqdm

log_dict = {}
# 规则必须以列表形式存储，分别是要替换的内容，以及替换成什么内容
pattern_list = [
    [r'（[^（）]*(?:[参详]|点击|见[下])[^（）]*）', ''],
    [r'（[^（）]*图[^（）]*示[^（）]*）', ''],
    [r'\([^\(\)\n]*详见[^\)\(\n]*\)', ''],
    [r'\(?[\u4e00-\u9fa5\d\.【】]*参阅[\u4e00-\u9fa5：， \d\w\/【】]*\)', ''],
    [r'\|', ''],
    # 混乱内容删除：
    [r'。[^。]*[ㄇ][^。]*', ''],  # 删除特定内容
    [r'。[^。]*?src[^。]*', ''],
    # 中文问题 和41问题
    # 下面正则删除?  类型1 .{10}\??\/\?.{10}
    [r'\?{3,}', ''],  # 删除3个?以上
    [r'\?{2,}', r'?'],  # 连续两个?替换成一个
    [r'([\n。；] ?\d+) ?\? ?', r'\1.'],  # 将\n\d?中?替换成. 小标题开头
    [r'(35)(\?\/\?)', r'\1mg/m2'],  # 删除固定的一个
    [r'\?\/\?', 'mg/kg'],  # 11个?\?
    [r'\?(mm3)', r'\1'],  # 单个类型
    [r'(mg\/)\?', r'\1m2'],  # 单个类型
    [r'(m\d)\?', r'\1'],
    [r'(\n\d．)\?', r'\1'],
    [r'\/\?', ''],  # 单个类型
    # 类型2 \d+\?\d+    数字
    [r'(\d+)\?(\d+片)', r'\1/\2'],  # 特殊类型
    [r'(\dg)\?(；)', r'\1\2'],
    # 中文
    [r'(([\u4e00-\u9fa5]{1,}(?:\?)){2,})', lambda s=r'\1': s[0].replace('?', '、')],  # 将连续的中文+?的文本出现2次以上的?替换成、
    [r'([\u4e00-\u9fa5])\?([^\u4e00-\u9fa5])', r'\1\2'],  # 将中文\?非中文组合删除问号
    [r'(([\u4e00-\u9fa5]{1,}(?:\?+)){1,})', lambda s=r'\1': s[0].replace('?', '、')],  # 将连续的中文+?的文本出现1次以上的删除?
    [r'([\n\(\)、）\. 。：；Ⅰ,（％%+\]])\?', r'\1'],  # 清洗符号后面为?的?
    # 处理?前后为英文
    [r'g\?([md])', r'g/\1'],# 单个类型
    [r'l\?L', r'l/L'],# 单个类型
    [r'l\?K', r'l-K'],# 单个类型
    [r'([a-zA-Z])\?([a-zA-Zγα ])', r'\1、\2'],#英文连续组合
    [r'\?次', r'次'],# 单个类型
    [r'(\d+[\-]\d+)\?(Ci)', r'\1μ\2'],# 单个类型
    [r'kg\?天', r'kg/天'],# 单个类型
    [r'kg\?', r'kg'],# 单个类型
    [r'(mg)\?，', r'\1，'],# 单个类型
    [r'\?(g\/(kg|ml))', r'm\1'],# 单个类型
    [r'(\w)\?([\u4e00-\u9fa5])', r'\1\2'],
    [r'(\d+)\?(\d+天)', r'\1-\2'],
    [r'(\d+)\?(\d+)\?', r'\1,\2,'],
    [r'n\?', 'n'],
    [r'1\?2', '1-2'],
    [r'([2])\?([34])', r'\1-\2'],
    [r'1\?5支', '1.5支'],# 单个类型
    [r'1\?5', '15'],
    [r'(\d\.\d)\?(\d\.\d)', r'\1，\2'],
    [r'\?([，。,])', r'\1'],
    [r'(2.6)\?(16mg)', r'\1，\2'],
    [r'(\.\dg?)\?', r'\1，'],# 单个类型
    [r'g\?([623])', r'g。\1'],# 单个类型
    [r'\?(B\d)', r'、\1'],# 单个类型
    [r'([①②③④℃>～:12ｏ~g\d，\-\*])\?', r'\1'],#剩余开头带?的删除
    [r'\?([mh\-Kg～ \)])', r'\1'],#剩余结尾带?的删除

    [' {2,}', ' '],  # 替换多个空格为一个
    [r'(\\)+("?)', r'\2'],  # 删除多余的\

    # [r'\?',''],#检测代码

]

# （可以点击「早泄」词条查看更多内容）
context_pattern = [
    ['', ''],
    ['。。', ''],
    ['，，', ''],
    ['。，', ''],
    ['，。', ''],
    ['、、', '、'],
    ['、。', '。'],
    ['。.2。。', '。']

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
    # 1.正则
    for pattern_item in pattern_list:
        if re.findall(pattern_item[0], context) != []:
            if str(pattern_item[0]) not in log_dict:
                log_dict[str(pattern_item[0])] = re.findall(pattern_item[0], context)
            else:
                log_dict[str(pattern_item[0])] = log_dict[str(pattern_item[0])] + re.findall(pattern_item[0], context)

        context = re.sub(pattern_item[0], pattern_item[1], context)

    # 2.替换 固定内容（非泛化）
    for replace_item in context_pattern:
        # context = re.sub(replace_item[0], replace_item[1], context)
        context = context.replace(replace_item[0], replace_item[1])

    return context


fw = open("../../../../full_data/druginstruction/druginstruction_clean.jsonl", "w", encoding="utf-8")
with open("../../../../full_data/druginstruction/druginstruction_preformat.jsonl", "r", encoding="utf-8") as fs:
    for items in tqdm(fs.readlines()):
        item = json.loads(items.strip())
        context = item["text"]
        context = clean_text(context)
        # context = post_process(context)
        item["text"] = context

        item = json.dumps(item, ensure_ascii=False)
        fw.write(item + "\n")
    print(log_dict.keys())
    print(log_dict["([①②③④℃>～:12ｏ~g\\d，\\-\\*])\\?"])
