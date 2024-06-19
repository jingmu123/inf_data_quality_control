import json
import re
from tqdm import tqdm

# 规则必须以列表形式存储，分别是要替换的内容，以及替换成什么内容
pattern_list = [
    [r'(?:词条作者|审核专家)\n\n[^\n]+\n\n', ''],
    [r'(?:发布时间|最后修订时间)[^\n]+\n\n', ''],
    [r'((?:\n\n.{2,4})+\n\n更多)', ''],
    [r'参考资料\n[\s\S]*', ''],
    [r'<sup>.*?</sup>', ''],
    [r'\*[\u4e00-\u9fa5\w\.\d ]* 就诊', ''],
    [r'\\*.*(?:\d{3}-\d{3,4}-\d{3,4}|\d{3,4}[-－]\d{8}|1{8}|联系办法供参考).*', ''],
    [r'(?:https?://|网站：|[^\n]*(?:图 \d\，)?图片来源：?:?\xa0?|图 1，来源：)(?:www)?[^\n]*|www.g6pd.*org', ''],
    [r'\*\*.*?(?:高能预警 ?↓?)\*\*|高能预警↓', ''],
    [r'(?:(?:（?图 ?\d .*)?来源：自?|多余毛发的去除 )UpToDate(?: ?临床顾问）?)?', ''],
    [r'\n.*(?:图 ?\d\.|图源|图 [\d\w].*来源：?|图 \d：|图\W\.|皮肤性病诊断图谱|图片：).*\n', ''],
    [r'（图 ? ?\d ?）', ''],
    [r'\\\\\[.*?\\\\\]', ''],
    [r'\\\[.*?\\\]', ''],
    [r'\\\\\[', ''],
    [r'\n.*(?:[^种的个叶染]来源：|表格来源).*\n', ''],
    [r'（如?上?下?面?左?[^（]*图[ ，示]*?片? ?[\d\w]?\d? ?）', ''],
    [r'(?:(?:心脏传导系统)?[（(?:具体)见如]|主要的表现如)+下图(?:所示)?：? ?(?:位置)?。?）?', ''],
    [r'[（如见]*?图 \d[^\n；）]*[），]?', ''],
    # new2
    ['（[^（）人海以]*(?:[参详]|点击|见[下])[^（）加]*）', ''],
    ['关于[^。！？]*?详见[^。！？]*?内容。?', ''],
    ['(?:[^。？(?:\n\n)]|(?:可点击))*详情[^。\n\*]*[\n。]?|（详见「三角软骨盘复合体（TFCC）损伤」（链接）', ''],
    ['[^。\n]*(?:详见|参阅：|相关专题|下面图片)[^。\*\n]*。*', ''],
    ['(?:\*\*\d\\\\\.)? (头部控制|腹部悬吊|垂直悬吊)试验，?(?:\*\*)?', ''],
    ['[^\n。，]*[^配]可参考[^这自血美][^\n：。，]*.', ''],
    ['动作链接：[\u4e00-\u9fa5\w\.\d ]*', ''],
    ['[^。]*\n\n\*', '\n\n\*'],
    ['［\d］', ''],
    [r'[\d-]*\\(\])?', ''],
    [r'[^。]*-[\n ]*$', ''],
    [r'[（\(]?可以?点击.*?词条.*?更多内容[）\)]?', ''],
    [r'.*更多内容.*?。', ''],
    ['(具体)?如图：', ''],
    ['图中：[\u4e00-\u9fa5，]*', ''],
]

# （可以点击「早泄」词条查看更多内容）
context_pattern = [
    ['丁香医生审稿专业委员会同行评议通过\n\n', ''],
    ['Gerald W Smetana, MD. Evaluation of the patient with night sweats or generalized hyperhidrosis.', ''],
    ['Hung K So1, Albert M Li1, Chun T Au1, etc. Night sweats in children: prevalence and associated factors.', ''],
    ['Noreen Iftikhar. Why Is My Child Sweating at Night and What Can I Do?', ''],
    ['Jennifer Shu. Baby and Child Health: The Essential Guide From Birth to 11 Years.', ''],
    ['**特别提醒：** 图片仅为个案展示，不能作为诊断依据。如果怀疑得了疾病，还请尽早在线问诊或去线下医院寻求诊疗帮助。', ''],
    ['**特别提醒：**', ''],
    ['可以在本 App 里搜索「丘疹性荨麻疹」或者「皮肤科」咨询相关的医生。', ''],
    ['点击上方图片可以预约流感疫苗接种', ''],
    ['具体可见上文图片。', ''],
    ['具体可以参考下面这张图。', ''],
    ['图片参考：见水印', ''],
    ['（具体可参考图片）', ''],
    ['如上图，', ''],
    ['（草莓状血管瘤）', ''],
    ['参见下文。', ''],
    ['具体的治疗方法可参见治疗版块。', ''],
    ['参见「不同类型的荨麻疹的临床表现有哪些不同？」', ''],
    ['（表 1）', ''],
    ['**抗病毒治疗**：以', ''],
    ['。；', '。'],
    ['。。', '。'],
    ['，，', '，'],
    ['？？', '？'],
    ['。，', '，'],
    ['，。', '。'],
    ['（\n', '\n']
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

    def step1_strip(self, context):
        split_token = "\n\n"
        new_context = []
        context = context.split(split_token)
        for item in context:
            item = item.rstrip()
            if "* " not in item:
                item = item.lstrip()
            else:
                pass
            new_context.append(item)
        return split_token.join(new_context)

    def step2_rmless(self, context):
        split_token = "\n\n"
        new_context = []
        new_context = context.split(split_token)
        try:
            if "*   内容" in new_context[3] and new_context[2][-1] not in ["。", "?", "？", "!", "！", "~"]:
                temp_sent = new_context[2].split("。")
                if temp_sent[-1] in "".join(new_context[3:]):
                    del new_context[2]
                    # print("has in ",new_context)
                else:
                    temp_sent = temp_sent[:-1]
                    temp_sent = "。".join(temp_sent)
                    # print(f"rm operation:\n{new_context[2]}\n{temp_sent}")
                    new_context[2] = temp_sent
        except:
            pass
        return split_token.join(new_context)

    def step3_replace_space(self, context):
        while True:
            try:
                context = re.sub(r'就诊科室：[^科]*科 [^科]*科',
                                 str(re.search('就诊科室：[^科]*科 [^科]*科', context)[0]).replace(' ', '，'), context,
                                 count=1)
            except Exception as e:
                break
        while True:
            try:
                context = re.sub(r'[\u4e00-\u9fa5] [\u4e00-\u9fa5]',
                                 str(re.search('[\u4e00-\u9fa5] [\u4e00-\u9fa5]', context)[0]).replace(' ', ''), context,
                                 count=1)
                print(re.search('[\u4e00-\u9fa5] [\u4e00-\u9fa5]', context)[0])
            except Exception as e:
                break
        return context


def clean_text(context, lang="zh"):
    # 如果存在特殊处理，以类的方式整合，初始化类；
    sp = speicalProces()
    # 1.正则
    for pattern_item in pattern_list:
        if pattern_item[0] == '[\u4e00-\u9fa5] [\u4e00-\u9fa5]' and re.findall(pattern_item[0], context) != []:
            print(re.findall(pattern_item[0], context))
        context = re.sub(pattern_item[0], pattern_item[1], context)

    # 2.替换 固定内容（非泛化）
    for replace_item in context_pattern:
        # context = re.sub(replace_item[0], replace_item[1], context)
        context = context.replace(replace_item[0], replace_item[1])

    # 2. 整合
    context = post_process(context)
    context = sp.step1_strip(context)
    context = sp.step2_rmless(context)
    context = sp.step3_replace_space(context)
    # print("final",context.split("\n\n"))
    # exit(0)
    return context


fw = open("../../../../full_data/dingxiangyisheng/dingxiangyisheng_clean.jsonl", "w", encoding="utf-8")
with open("../../../../full_data/dingxiangyisheng/dingxiangyisheng_preformat.jsonl", "r", encoding="utf-8") as fs:
    for items in tqdm(fs.readlines()):
        item = json.loads(items.strip())
        context = item["text"]
        context = clean_text(context)
        context = post_process(context)
        item["text"] = context

        item = json.dumps(item, ensure_ascii=False)
        fw.write(item + "\n")
