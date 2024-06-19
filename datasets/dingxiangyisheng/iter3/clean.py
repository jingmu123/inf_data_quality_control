import json
import os
import re
from langdetect import detect
from tqdm import tqdm
import sys

sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf8', buffering=1)
pattern_list = [
    r'(?:词条作者|审核专家)\n\n[^\n]+\n\n',
    r'(?:发布时间|最后修订时间)[^\n]+\n\n',
    r'((?:\n\n.{2,4})+\n\n更多)',
    r'参考资料\n[\s\S]*',
    r'<sup>.*?</sup>',
    '\n    \n\*   就诊$',
    # 下面为新加内容
    '\\*.*(?:\d{3}-\d{3,4}-\d{3,4}|\d{3,4}[-－]\d{8}|1{8}|联系办法供参考).*',
    '(?:https?://|网站：|[^\n]*(?:图 \d\，)?图片来源：?:?\xa0?|图 1，来源：)(?:www)?[^\n]*|www.g6pd.*org',
    '\*\*.*?(?:高能预警 ?↓?)\*\*|高能预警↓',
    '(?:(?:（?图 ?\d .*)?来源：自?|多余毛发的去除 )UpToDate(?: ?临床顾问）?)?',
    '\n.*(?:图 ?\d\.|图源|图 [\d\w].*来源：?|图 \d：|图\W\.|皮肤性病诊断图谱|图片：).*\n',
    '（图 ? ?\d ?）',
    '\\\\\[.*?\\\\\]',r'\\\[.*?\\\]',
    '\n.*(?:[^种的个叶染]来源：|表格来源).*\n',
    '（如?上?下?面?左?[^（]*图[ ，示]*?片? ?[\d\w]?\d? ?）',
    '(?:[（(?:具体)见如]|主要的表现如)+下图(?:所示)?：? ?(?:位置)?。?）?',
    '[（如见]*?图 \d[^\n；）]*[），]?',
    # new2
    '（[^（）人海以]*(?:[参详]|点击|见[下])[^（）加]*）',
    '(?:[^。？(?:\n\n)]|(?:可点击))*详情[^。\n\*]*[\n。]?|（详见「三角软骨盘复合体（TFCC）损伤」（链接）',
    '[^，。\n]*(?:详见|参阅：|相关专题|下面图片)[^。\*\n]*。*',
    '(?:\*\*\d\\\\\.)? (头部控制|腹部悬吊|垂直悬吊)试验，?(?:\*\*)?',
    '[^\n。，]*[^配]可参考[^这自血美][^\n：。，]*.'

]


def detect_language(content):
    # print("context",content)
    lang = detect(content)
    if lang == "zh-cn":
        return "zh"
    if lang == "en":
        return "en"
    return "None"


def content_replace(content):
    replace_text_list = ['丁香医生审稿专业委员会同行评议通过\n\n',
                         'Gerald W Smetana, MD. Evaluation of the patient with night sweats or generalized hyperhidrosis.',
                         'Hung K So1, Albert M Li1, Chun T Au1, etc. Night sweats in children: prevalence and associated factors.',
                         'Noreen Iftikhar. Why Is My Child Sweating at Night and What Can I Do?',
                         'Jennifer Shu. Baby and Child Health: The Essential Guide From Birth to 11 Years.',
                         '**特别提醒：** 图片仅为个案展示，不能作为诊断依据。如果怀疑得了疾病，还请尽早在线问诊或去线下医院寻求诊疗帮助。',
                         '**特别提醒：**'
                         '可以在本 App 里搜索「丘疹性荨麻疹」或者「皮肤科」咨询相关的医生。',
                         '点击上方图片可以预约流感疫苗接种', '具体可见上文图片。', '具体可以参考下面这张图。',
                         '图片参考：见水印', '（具体可参考图片）', '如上图，', '（草莓状血管瘤）', '参见下文。',
                         '具体的治疗方法可参见治疗版块。', '参见「不同类型的荨麻疹的临床表现有哪些不同？」', '（表 1）',
                         '**抗病毒治疗**：以']
    for replace_text in replace_text_list:
        content = content.replace(replace_text, '')
    return content


def clean_text(context):
    for pattern in pattern_list:
        with open('../work_code/log.txt', 'a+', encoding='utf-8') as f:
            if re.findall(pattern, context) != [] and pattern in [
                # r'(?:词条作者|审核专家)\n\n[^\n]+\n\n',
                # r'(?:发布时间|最后修订时间)[^\n]+\n\n',
                # r'((?:\n\n.{2,4})+\n\n更多)',
                # r'参考资料\n[\s\S]*',
                # r'<sup>.*?</sup>',
                # '\n    \n\*   就诊$',
                # # 下面为新加内容
                # '\\*.*(?:\d{3}-\d{3,4}-\d{3,4}|\d{3,4}[-－]\d{8}|1{8}|联系办法供参考).*',
                # '(?:https?://|网站：|[^\n]*(?:图 \d\，)?图片来源：?:?\xa0?|图 1，来源：)(?:www)?[^\n]*|www.g6pd.*org',
                # '\*\*.*?(?:高能预警 ?↓?)\*\*|高能预警↓',
                # '(?:(?:（?图 ?\d .*)?来源：自?|多余毛发的去除 )UpToDate(?: ?临床顾问）?)?',
                # '\n.*(?:图 ?\d\.|图源|图 [\d\w].*来源：?|图 \d：|图\W\.|皮肤性病诊断图谱|图片：).*\n',
                # '（图 ? ?\d ?）',
                '\\\\\[.*?\\\\\]',r'\\\[.*?\\\]',
                # '\n.*(?:[^种的个叶染]来源：|表格来源).*\n',
                # '（如?上?下?面?左?[^（]*图[ ，示]*?片? ?[\d\w]?\d? ?）',
                # '(?:[（(?:具体)见如]|主要的表现如)+下图(?:所示)?：? ?(?:位置)?。?）?',
                # '[（如见]*?图 \d[^\n；）]*[），]?',
                # # new2
                # '（[^（）人海以]*(?:[参详]|点击|见[下])[^（）加]*）',
                # '(?:[^。？(?:\n\n)]|(?:可点击))*详情[^。\n\*]*[\n。]?|（详见「三角软骨盘复合体（TFCC）损伤」（链接）',
                # '[^，。\n]*(?:详见|参阅：|相关专题|下面图片)[^。\*\n]*。*',
                # '(?:\*\*\d\\\\\.)? (头部控制|腹部悬吊|垂直悬吊)试验，?(?:\*\*)?',
                # '[^\n。，]*[^配]可参考[^这自血美][^\n：。，]*.'

            ]:
                f.write(str(re.findall(pattern, context)) + '\n')
        context = re.sub(pattern, '', context)
        context = content_replace(context)
        context = context.replace('。；', '。')
        context = context.replace('。。', '。')
        context = context.replace('，，', '，')
        context = context.replace('？？', '？')
        context = context.replace('。，', '，')
        context = context.replace('，。', '。')
        context = re.sub(r'\n +\n', "\n\n", context)
        context = re.sub('\n    -', "\n\n    -", context)  # new
        context = re.sub("\n{2,}", "\n\n", context)

    split_token = "\n\n"
    new_context = []
    context = context.split(split_token)
    for item in context:
        if "* " not in item:
            item = item.strip(" ")
        else:
            pass
        new_context.append(item)

    return split_token.join(new_context)


def test():
    with open("./data_result/dingxiangyisheng.jsonl", "r", encoding="utf-8") as fr:
        with open('../work_code/test.md', 'w', encoding='utf-8') as f:
            for i in tqdm(fr.readlines()):
                f.write((json.loads(i))['text'] + '\n')


def main():
    fr = open("data_result/dingxiangyisheng.jsonl", "w", encoding="utf-8")
    with open('../work_code/log.txt', 'w') as f:
        f.close()
    with open("./data_source/dingxiangyisheng_preformat.jsonl", "r", encoding="utf-8") as fs:
        for data in tqdm(fs.readlines()):
            item = json.loads(data.strip())
            item["text"] = clean_text(item["text"])
            item = json.dumps(item, ensure_ascii=False)
            fr.write(item + "\n")


if __name__ == '__main__':
    main()
    test()
