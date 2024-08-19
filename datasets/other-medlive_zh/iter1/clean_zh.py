# coding:utf-8
# https://github.com/shibing624/pycorrector?tab=readme-ov-file
import json
import re
from collections import defaultdict

from tqdm import tqdm
import sys

import transformers
sys.path.append("../../../")

import spacy
import jieba

# import torch.nn.functional as F
# from transformers import AutoModelForSequenceClassification, AutoTokenizer


pattern_list_zh = [
    # [r'(（?\[([\u4e00-\u9fa5A-Za-z]+)<sup><img><\/sup>\]\(https?:\/\/[a-zA-Z0-9-]+\/\d*\)([\u4e00-\u9fa5A-Za-z]*)）?)',r'\2\3 删除1：<u>\1</u>'],
    [r'(([(（])?\[(.*?)<sup><img><\/sup>\]\(https?:\/\/[a-zA-Z0-9-]+\/\d*\))',r'\2\3删除1：<u>\1</u>'],
    [r'(?:^ * * *|\n * * *)((\*\*)?(图片|资料)?来源[:：].*(\*\*)?)',r'删除2：<u>\1</u>'],
    [r'(<sup>(<span>)? *\[?.*?\]? *(<\/span>)?<\/sup>)',r'删除3：<u>\1</u>'],
    [r'(?<=\n)( *(?:\*\*)?(?:原标题 *[:：]|（?摘要号 *[:：]|(?:英文|中文|原文)?标题 *[:：]|文献链接 *[:：]|本？内容节？选自|本文整理自).*(?:\*\*)?)|(?<=^)( *(?:\*\*)?(?:原标题 *[:：]|（?摘要号 *[:：]|(?:英文|中文|原文)?标题 *[:：]|文献链接 *[:：]|内容选自|本文整理自).*(?:\*\*)?)',r'删除4：<u>\1\2</u>'],
    [r'(\\?[\[［][0-9０-９]+[-—,，、]?\d*\\?[］\]])',r'删除5：<u>\1</u>'],#文中的数字索引：\[5\]，\[16-17\]，\[7,8\]，［９］
    [r'(?<=\n)( *(\*\*)?[图表] *\d+.*(\*\*)?)(?=\n|$)|(?<=^)( *(\*\*)?[图表] *\d+.*(\*\*)?)(?=\n|$)',r'删除6：<u>\1\4</u>'],#单独一行的图表索引
    [r'((\*\*)?[(（] *见?[图表] *\d+.*?[）)](\*\*)?)',r'删除7：<u>\1</u>'],#文中的图表索引
    [r'((\*\*)?(第一作者|编辑|本文作者|作者|撰稿人)[：:].*(\*\*)?)',r'删除8：<u>\1</u>'],
    [r'(?<=\n)( * *责编 *[:：]?.*)|(?<=^)( * *责编 *[:：]?.*)',r'删除9：<u>\1\2</u>'],#单独一行的责编删除
    [r'(?<=\n)((\\\*|…|参考文献略。|↓|▼)+)(?=\n|$)|(?<=^)((\\\*|…|参考文献略。|↓|▼)+)(?=\n|$)',r'删除10：<u>\1\3</u>'],#单独一行\*或...的删除
    [r'(?<=^)(\**完整版指南下载链接.*)(?=\n|$)|(?<=\n)(\**完整版指南下载链接.*)(?=\n|$)',r'删除11：<u>\1\2</u>'],#单行的完整版指南下载 删除
    [r'(\**[（(][^）)\n]*完整版指南下载链接[^(（\n]*[）)] *(\*|\n\*)*)',r'删除12：<u>\1</u>'],#括号内的指南下载 删除
    [r'(?<=\n)((\*\*)?(参考文献[：\n]|参考来源：|参考资料：|资料来源：|医脉通编译整?理?自：|文献索引：|文源：|医脉通综合整理|论文链接：)(.*\n.*)*)',r'删除13：<u>\1</u>'],#6530a851-7287-43a1-80c8-e2ec518b668d
    [r'(.*\**图源 *[:：|].*)',r'删除14：<u>\1</u>'],
    # [r'(?<=\n)(\**(点击阅读|专题报道|点击查看更多|敬请关注)(?:>>>|☞)[  ]*\**[  ]*(\[.*\]\(.*\) *(\n\n)?)*\**)(\n?\n?)',r'删除15：<u>\1</u>\4'],
    # [r'(?<=\n)((\**（?(?:.*：|点击阅?读?|专题报道|点击查看更多|敬请关注|往期(?:回顾|推荐)|见《|✎)?(?:>>>|☞| |\*|↓|| )*(?:\n *)*(?:\[.*\]\((?:https?:\/\/)?(?:www\.)?[a-zA-Z0-9-]+(?:\.[a-zA-Z]{2,})+(?:\/[^ \n\u4e00-\u9fa5]*)?\))(?:》?）)?)+.*)',r'删除15：<u>\1</u>'],
    [r'(?<=\n)((\**（?(?:.*：|.{0,8}点击.*|.*专题报道.*|.*敬请关注.*|.*往期.*|.*回顾.*|.*推荐.*|✎)?[\n ]*(?:>>>|☞| |\*|↓|| |☟)*(?:\n *)*\**(?:(\[.*\])?\(?(?:https?:\/\/)(?:www\.)?[a-zA-Z0-9-]+(?:\.[a-zA-Z]{2,})+(?:\/[^ \n\u4e00-\u9fa5]*)?\)?)(?:》?）)?)+.*)',r'删除15：<u>\1</u>'],
    [r'(.*(点击|戳|扫码).*?看.*?视频.*)|(.*看.*?视频.*?(点击|戳|扫码).*)',r'删除16：<u>\1\3</u>'],
    [r'(以上为.*?的简要概括。.*)',r'删除17：<u>\1</u>'],
    [r'([《（，\u4e00-\u9fa5“])(\[(.*)\](\((?:https?:\/\/)?(?:www\.)?[a-zA-Z0-9-]+(?:\.[a-zA-Z]{2,})+(?:\/[^ \n\u4e00-\u9fa5]*)?\)))',r'\1\3删除18：<u>\4</u>'],
    # [r'([(（][^\n()（）\\]*?参见[^\n()（）\\]*?[）)])',r'删除参见内容：<u>\1</u>']
    [r'(\**（[^(（）)\n]*扫描?(?:下方|上方|文末)?(?:二维)?码[^（()）\n]*）\**)|([^(（\n]*(?:（.*）)?[^(（\n]*扫描?(?:下方|上方|文末)?(?:二维)码[^)）\n]*(?:（?.*）)?[^)）\n]*)',r'删除18：<u>\1\2</u>']


]

context_pattern = [
    [r"[。，?!,]([。，?!,])", r"\1"],

]


# ner_pipeline = pipeline(Tasks.named_entity_recognition, 'damo/nlp_raner_named-entity-recognition_chinese-base-generic')
class speicalProces:
    def __init__(self):
        pass
        # self.sc = sentence_correct.SentenceCorrector()

        # self.en_nlp = spacy.load("zh_core_web_trf")
        # self.zh_nlp = spacy.load("zh_core_web_sm")
        # self.zh_nlp = spacy.load("zh_core_web_sm")
        # self.ner_pipeline = pipeline(Tasks.named_entity_recognition, 'damo/nlp_raner_named-entity-recognition_chinese-base-generic')
        # self.zeroshot_classifier = transformers.pipeline("zero-shot-classification", model="deberta-v3-large-zeroshot-v2.0")
        #
        # self.model = AutoModelForSequenceClassification.from_pretrained("autonlp-Gibberish-Detector-492513457",
        #                                                            use_auth_token=True)
        # self.tokenizer = AutoTokenizer.from_pretrained("autonlp-Gibberish-Detector-492513457", use_auth_token=True)

    # def step1_rm_reference(self,context):
    #     if re.findall(r'((?:　)*(?: *  )+\d{4}年\d+月\d+日)',context) != 0:
    #         if '附件' in context or '公告' in context:
    #             return '本页判断为公告或附件，整页删除\n\n'+context
    #     else:
    #         return context
    #
    # def step2_Characte_introduction(self,context):
    #     if re.findall(r'(\*\*.*[  ](副?教授|博士|主任)\*\*)(?=\n)((\n\n)*(.{3,51}))+',context) !=0:
    #         pass
    #     else:
    #         return context

    # def step10_Irrelevant_long_text(self,context):
    #     split_token = "\n\n"
    #     if split_token not in context:
    #         split_token = "\n"
    #
    #     count= 0
    #     result,suspected = [],False
    #     key_words=['教材编写','前言','作者简介','作者介绍','版权所有','主编介绍','附录','参考文献']
    #     for word in key_words:
    #         if word in context:
    #             suspected=True
    #             break
    #     if suspected:
    #         # print(context)
    #         context_lis = context.split('\n')
    #         # print(context_lis)
    #         for paragraph in context_lis:
    #             if not paragraph:
    #                 result.append(paragraph)
    #                 continue
    #             # print(paragraph)
    #             hypothesis_template = "The type of this text is {}"
    #             classes_verbalized = ["Text content", "reference", "acknowledgments", 'personage introduction',
    #                                   'Guide book', ]
    #             output = self.zeroshot_classifier(paragraph, classes_verbalized, hypothesis_template=hypothesis_template,
    #                                          multi_label=False)
    #             # print(output["labels"][0], output['scores'][0])
    #             if output["labels"][0] != 'Text content':
    #                 paragraph = "参考删除-3:<u>{}</u>".format(paragraph)
    #                 count += 1
    #             result.append(paragraph)
    #         context_lis=set(context_lis)
    #         context_lis.discard('')
    #
    #         if count >= len(context_lis) / 2:
    #             # return ''
    #             return '(本页删除)本页一半的段落中发现符合参考文献的特征' + '\n' + context
    #         else:
    #             return '\n'.join(result)
    #     else:
    #         return context


def clean_text(context, lang, sp):
    # print("-"*10)
    split_token = "\n\n"
    if split_token not in context:
        split_token = "\n"
    pattern_list = pattern_list_zh


    for pattern_item in pattern_list:
        # context = context.lstrip(" ").rstrip(" ")
        context = re.sub(pattern_item[0], pattern_item[1], context)
    # context=sp.step1_rm_reference(context)
    # 分解处理
    # result = []
    # for idx, item in enumerate(context.split(split_token)):
    #     print(item)
    #
    #
    #     for pattern_item in pattern_list:
    #         item = item.lstrip(" ").rstrip(" ")
    #         item = re.sub(pattern_item[0], pattern_item[1], item)
    #
    #     for replace_item in context_pattern:
    #         item = re.sub(replace_item[0], replace_item[1], item)
    #     print(item)
    #     result.append(item)

    # 整合

    # print(context)
    # context = split_token.join(result)
    # print(context)

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


def process_line(items, sp):
    try:
        item = json.loads(items.strip())
        # item=sp.step1_drop_Pagefooter(item)

        context = item["text"]
        lang = item["lang"]

        context = clean_text(context, lang, sp)
        context = post_process(context)
        item["text"] = context
    except:
        print("error")
        exit(0)
    item = json.dumps(item, ensure_ascii=False)
    return item

sp=speicalProces()
fw = open(r'F:\zeroshots\other-medlive_zh\reclean1_other-medlive_zh_label.jsonl', 'a', encoding='utf-8')
# with open(r'C:\Users\Administrator\PycharmProjects\untitled\other-medlive_zh_preformat\test.jsonl', "r", encoding="utf-8") as file:
with open(r'F:\zeroshots\other-medlive_zh\other-medlive_zh_preformat.jsonl', "r", encoding="utf-8") as file:

    for item in tqdm(file.readlines()):

        item=process_line(item,sp)
        # with open(r'F:\zeroshots\reclean7_medicalpdfv2__preformat_zh.jsonl', 'a', encoding='utf-8') as f:
        fw.write(item+'\n')


