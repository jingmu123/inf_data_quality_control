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
# 09daedd5-d85f-4cca-b474-e195e19fc7b9  05628c74-68dd-4b75-a6e5-04b21cb24f7c       3eb5b023-260f-4c33-8319-2c1981a90de3
pattern_list_zh = [
    # [r'(（?\[([\u4e00-\u9fa5A-Za-z]+)<sup><img><\/sup>\]\(https?:\/\/[a-zA-Z0-9-]+\/\d*\)([\u4e00-\u9fa5A-Za-z]*)）?)',r'\2\3 删除1：<u>\1</u>'],
    [r'(([(（])?\[([^\n[\]]*?)<sup><img><\/sup>\]\(https?:\/\/[a-zA-Z0-9-]+\/\d*\))',r'\2\3删除1：<u>\1</u>'],#多余链接和格式的删除

    [r'(?:^[  ]*|\n[  ]*|[(（]| )((\*\*)?△*来[源自][:：].*(\*\*)?)',r'删除2：<u>\1</u>'],#来源类的整行删除
    [r'(?:^[  ]*|\n[  ]*)((\*\*)?△*.{0,15}(截?见?[图表]+片?)[来源自略0-9A-Za-z。]+[:：]?.*(\*\*)?)',r'删除20：<u>\1</u>'],#图源类的删除整行删除
    [r'(?:\n|^)([  ]*\**△?附?(?:本文)?[图表]注?解? *[A-Za-z0-9一二三四五六七八九十:：片|]+.*\**)(?=\n|$)', r'删除6：<u>\1</u>'],  # 单独一行的图表索引
    [r'((\*\*)?[(（] *(?:(?:详|流程)?见|配|如?下?|视频|网络|截|点击查看大?|作者供)*[图表] *[A-Za-z0-9一二三四五六七八九十]*[^(（）)\n]{0,5}[）)](\*\*)?)', r'删除7：<u>\1</u>'],  # 文中带括号的图表索引
    [r'(?<=\n)(△?.{0,15}(?:资料|[截配制]|流程|网络)图.{0,10})(?=\n|$)',r'删除26：<u>\1</u>'],#各式截图类的单行删除
    [r'(。| |）|，|:)([^ 。,，\n(（）)]*?[如见]?下?[图表] *(?:[A-Za-z0-9一二三四五六七八九十]|所示)+[^。,，\n(（）)]*)(?:。|\n)',r'\1删除14：<u>\2</u>'],#文中出现的有关见图见表类的小句子的删除1
    [r'(。| |）|，|:)([^ 。,，\n(（）)]*?[如见]下?[图表] *)(?:。|\n|“|”|；|;)',r'\1删除14：<u>\2</u>'],#文中出现的有关见图见表类的小句子的删除2
    [r'([(（][^\n()（）]+)([,，;；][图表] *[A-Za-z0-9一二三四五六七八九十:：]*)([)）])',r'\1删除34：<u>\2</u>\3'],#括号内有部分图片内容，只删除部分


    [r'(?:\n|^)(\**[(（]? *((?:第一|本文|文章)?作者(?:介绍|信息|贡献|简介)?|(本文)?编辑|翻译|撰稿人|分享人|撰文|统筹|策划|绘制|编译自?|利益冲突|审校.{0,2}|.{0,2}译者|资料图|Editor|联系.{0,3}|.{0,3}日期|.*邮箱|电话|手机|.{0,2}审批.{0,3}|致谢|支?持?单位|点评专家|执笔| *CRC number *| *Approved date *|病例(?:总结|提供者)|公众号(?:[Ii][Dd]))[：:│丨/ ].*\**)',r'删除8：<u>\1</u>'],
    [r'(?<=\n)( * *责编 *[:：]?.*)|(?<=^)( * *责编 *[:：]?.*)',r'删除9：<u>\1\2</u>'],#单独一行的责编删除

    [r'[\u4e00-\u9fa5](<sup>(<span>)? *\[?[^A-Za-z]*?\]? *(<\/span>)?<\/sup>)',r'删除3：<u>\1</u>'],
    [r'([^\u4e00-\u9fa5])(<su[pb]>(?:<span>)? *(\[?[^A-Za-z]*?\]?) *(?:<\/span>)?<\/su[pb]>)',r'\1\3删除3：<u>\2</u>'],



    [r'(\\?[\[［(][0-9０-９ ]+(?:[-—–⁃－,，、][0-9０-９ ]+)*\\?[)］\]])',r'删除5：<u>\1</u>'],#文中的数字索引：\[5\]，\[16-17\]，\[7,8\]，［９］
    [r'([\u00B3-\u00BA\u2070-\u2079\u00B2]+(?:[-—–⁃⁻－,，、][\u00B3-\u00BA\u2070-\u2079\u00B2]+)*)',r'删除5：<u>\1</u>'],

    [r'(?:\n|^)(\** *(?:\\\*|…|.*参考文献.*略.*|↓|—|▼|摄图网|\**.*(?:请勿|不得)转载.*\**|大会主持|。|致谢和参考文献（略）|.*内容仅[限供].*|.*以上观点系.*|本[期文]案[例件]来自.*|.{0,10}作者供图|医脉通 *)+)(?=\n|$)',r'删除10：<u>\1</u>'],#单独一行\*或...的删除
    [r'(?<=\n)((\*\*)? *(参考文献(（向下滑动）)?[:：\n]?|(?:本文)?参考.{0,3}[：:]?|(?:资料|原文|文献)(?:来源|索引|检索)[：:]|医脉通(?:编译)?整?理?(?:编译)?自[：:]|原?文献索?引?[：:]|文源[：:]|医脉通综合整理|(论文|相关摘要)链接[：:]|以上内容.{0,3}[:：]|今天你印象最深刻的新闻是？|.{0,4}互动[:：]|转载自[:：]|信源[:：]|.{0,4}综合自[:：]?|.{0,3}顾问律师[:：]|特别鸣谢[:：]|译者(?:介绍|简介)|[(（]?未完待续[)）]?)(\*\*)? *(([^\n]{3,})|(\n.*)*))',r'删除13：<u>\1</u>'],#文末互动： 今日互动：

    [r'(?:\n|^)( *\**(?:（?摘要号 *[:：]|(?:英文|中文|原文?)?标题 *[:：]|文献链接 *[:：]|文章来源 *[:：]|延伸阅读 *[:：]|.{0,8}摘自\**[：:]|.{0,8}选自|.{0,8}整理自).*\**)',r'删除4：<u>\1</u>'],#ee1a37d2-a04e-4e8a-80ca-5a16de7af2d6







    [r'(?<=^)(\**完整版指南下载链接.*)(?=\n|$)|(?<=\n)(\**完整版指南下载链接.*)(?=\n|$)',r'删除11：<u>\1\2</u>'],#单行的完整版指南下载 删除
    [r'(\**[（(][^(（）)\n]*(?:链接|摘自|附件|改编|.化名|作者[:：]|世界卫生组织|编号[:：]|来源[:：])[^(（\n]*[）)] *(\*|\n\*)*)',r'删除12：<u>\1</u>'],#括号内的指南下载 删除
    #6530a851-7287-43a1-80c8-e2ec518b668d

    [r'(?<=\n)((\**（?(?:[^\n（）()]*：|[^\n（）()]{0,8}点击.*|.*专题报?道?.*|.*敬请关注.*|.*往期.*|.*回顾.*|.{0,10}推荐.*|✎|[^\n（）()]*>>>)?[\n ]*(?:☞| |\*|↓|| |☟|✎|\d\.)*(?:\n *)*\**(?:(\[.*\n*\])?　*\(?(?:https?[:：]\/\/)(?:www\.)?[a-zA-Z0-9-]+(?:\.[a-zA-Z]{2,})+(?:\/[^ \n\u4e00-\u9fa5]*)?\)?)(?:》?）)?)+.*)',r'删除15：<u>\1</u>'],#后面有链接，标题符合的删除
    # [r'(.*(点击|戳|扫码).*?看.*?(?:视频|内容).*)|(.*看.*?视频.*?(点击|戳|扫码).*)',r'删除16：<u>\1\3</u>'],
    [r'((?:\n|\(|（)[^()（）\n]*(点击|戳|扫码).*?看.*?(?:视频|内容).{0,15}(?:\[.*\]\(.*\))?(?:\)|）|\n|$))|(.*看.*?视频.*?(点击|戳|扫码).*)',r'删除16：<u>\1\3</u>'],

    [r'(以上为.*?的简要概括。.*)',r'删除17：<u>\1</u>'],
    [r'([《（，\u4e00-\u9fa5“])(\[(.*)\](\((?:https?:\/\/)?(?:www\.)?[a-zA-Z0-9-]+(?:\.[a-zA-Z]{2,})+(?:\/[^ \n\u4e00-\u9fa5]*)?\)))',r'\1\3删除18：<u>\4</u>'],#提取书名或报道名（正文）
    [r'([(（][^\n()（）\\]*?参见[^\n()（）\\]*?(?:图|表|https?|建议)[^\n()（）\\]*?[）)])',r'删除参见内容：<u>\1</u>'],
    [r'(\**（[^(（）)\n]*扫描?(?:下方|上方|文末)?(?:二维)?码[^（()）\n]*）\**)|([^(（\n]*(?:（.*）)?[^(（\n]*扫描?(?:下方|上方|文末)?(?:二维)码[^)）\n]*(?:（?.*）)?[^)）\n]*)',r'删除19：<u>\1\2</u>'],
    [r'(\[(?:https?:\/\/)(?:www\.)?[a-zA-Z0-9-]+(?:\.[a-zA-Z]{2,})+(?:\/[^ \n\u4e00-\u9fa5]*)\]\(.*参考文献：.*\))',r'删除32：<u>\1</u>'],
    [r'(【生产企业】(?:.|\n)*?)(?:\n *\n *\n|$)',r'删除21：<u>\1</u>'],
    [r'(?<=\n)(\\\[[\u4e00-\u9fa5]+\\\] *)(?=\n)(\n\n)(?!\d)',r'删除22：<u>\1</u>\2'],
    [r'([\（(][^\n(（）)]*?(网站|国FDA)[^\n(（）)]*?[\）)])',r'删除23：<u>\1</u>'],

    [r'(?<=\n)(((?:.{4,11})(?:(?:作|进行|做).{0,4}报告|.{0,4}分享|开场致辞|开幕辞|会?议?总结|(开幕式)?主持(会议)?)[\n ]*(?:\n|$)){2,})',r'删除24：<u>\1</u>'],
    [r'(?<=\n)([A-Za-z]+号 *[A-Za-z0-9,]+ *有效期 *\d{4}-\d{2}-\d{2}.*(\n\n)?(资料过期，视同作废。)?)',r'删除25：<u>\1</u>'],
    [r'(?<=\n)((?:\**.*专家组\**)\n*\( *按姓氏笔画排序 *\)(?:.|\n)*?)(?:\n *\n *\n|$)',r'删除27：<u>\1</u>'],
    [r'(.*(?:欢迎(在?评论区)?留言|评论区见).*)',r'删除28：<u>\1</u>'],
    [r'(?<=)((?:[\u4e00-\u9fa5]{2,3} )+译)(?:\n)',r'删除29：<u>\1</u>'],
    [r'([(（][A-Za-z .]+\d{4}[,，;]\d+(?:\(\d+\))?[:：,，]\d+[-–—]\d+[^\u4e00-\u9fa5\n]+[)）])',r'删除30：<u>\1</u>'],
    [r'(?:^|\n)(.*期待在?您的?参与.*)',r'删除33：<u>\1</u>'],
    [r'(?:\n)([(（][^\n()（）]*\D[.，,；;] *\d{4} *[)）])',r'删除35：<u>\1</u>'],
    [r'(?:\n|^|。)(\**[^。\n()（）]{0,10}(?:本[文篇]|小编|汇总|指南)[^。\n()（）]*下载[^。\n]*(?:\n|$|。))',r'删除38：<u>\1</u>'],

    #特殊case
    [r'(\**(?:(?:欲知后事如何，请听下周日分解！|今天的医疗圈|发生了哪些与你有关的大事？|更新、更全的医学动态|更新、更全的医学动态|3分钟一网打尽|新旧版本更换期|新补充！可参考的2条建议|作者dr huangg)\n*)+\**)',r'删除31：<u>\1</u>'],
    [r'[\u4e00-\u9fa5](?<!分|为|图|表|日|在|是|或|于|一|和)([0-9０-９]{1,2}[-—，,][0-9０-９]{1,2})。',r'删除32：<u>\1</u>'],
    [r'((\** *[\u4e00-\u9fa5]{0,8} *[:：] *\**)?\[[^\]\n]*\n\]\(.*\))',r'删除36：<u>\1</u>'],
    [r'([⑴-⑾])(?:。)',r'删除37：<u>\1</u>'],
    [r'(?:\n|^)( *[\u4e00-\u9fa5]{1,5} *\|[ A-Za-z.]+)(?=\n|$)',r'删除39：<u>\1</u>']




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

    def step1_Irrelevant_long_text(self,context):
        if re.findall(r'(?<=\n)(\**.*名单\**)\n*\(按姓氏笔画排序\)',context) !=[]:
            return '本页判断为公告，整页删除\n\n'+context
        else:
            return context

    def step2_rm_short_context(self,context):
        split_token = "\n\n"
        if split_token not in context:
            split_token = "\n"
        count=0
        context_lis=context.split(split_token)
        for text in context_lis:
            if text.strip():
                count+=1

        if count>3:
            return context
        else:
            # return '本页判断为无关文本，整页删除\n\n'+context
            return ''



def clean_text(context, lang, sp):
    # print("-"*10)
    # split_token = "\n\n"
    # if split_token not in context:
    #     split_token = "\n"
    pattern_list = pattern_list_zh
    context = re.sub(r'\xa0', r' ', context)

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
    context=sp.step1_Irrelevant_long_text(context)
    context=sp.step2_rm_short_context(context)
    print(context)

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
fw = open(r'C:\Users\Administrator\PycharmProjects\untitled\other-medlive_zh_preformat\826.jsonl', 'a', encoding='utf-8')
# with open(r'C:\Users\Administrator\PycharmProjects\untitled\other-medlive_zh_preformat\other-medlive_zh_preformat.jsonl', "r", encoding="utf-8") as file:
with open(r'C:\Users\Administrator\PycharmProjects\untitled\other-medlive_zh_preformat\test.jsonl', "r", encoding="utf-8") as file:

    for item in tqdm(file.readlines()):

        item=process_line(item,sp)
        # with open(r'F:\zeroshots\reclean7_medicalpdfv2__preformat_zh.jsonl', 'a', encoding='utf-8') as f:
        fw.write(item+'\n')


