# coding:utf-8
from common_re import clean_pattern
import json
from tqdm import tqdm
import re

pattern_list_en = [
    [r'([\u4e00-\u9fff])', r''],# 汉字删除
    [r'(?:\n|^)(Case \d+:.*\n+)((?:\d+\n+)(?:Case \d+: .*))',r'\1'],
    [r'(\n|[^\d]\.|\?|!|\)|”)( *(?:<sup>)?[0-9 ]+(?:<\/sup>)? *)(?:\n)',r'\1'],#单行数字  需要修改
    [r'([0-9 ]+ Cases in[^\n.]*)(?:\n)',r''],#100 cases...
    [r'((?:Section *\d+\n+)?(?:ETHICS AND LAW IN[^a-z\n]*\n+)(?:[^a-z\n]*\n+)+)',r''],
    [r'((?:ETHICS AND LAW IN CLINICAL|Ethics and Law in Clinical) *\n*(?:PRACTICE|Practice):.*)',r''],
    [r'(VARICOSE VEIN AND VENOUS ULCER \d+|SWELLINGS IN THE NECK \d+|\d+ A TEXTBOOK ON SURGICAL SHORT CASES|TESTIS, EPIDIDYMIS AND SCROTUM *\d+ *|\d* *SWOLLEN LEG *\d*|SYNDROME AND CERVICAL RIB *\d+|DISEASE, THORACIC OUTLET *\d+|\d* *A TEXTBOOK OF SURGICAL SHORT CASES)',r''],
    [r'(?:\n)(\** *_*[A-Z]\.)(\\\])',r'\1'],
    [r'(?:\n|^)((?:\([a-z]\) ?\d*)+)(?:\n)',r''],


    # [r'([\u4e00-\u9fff])', r'删除17：<u>\1</u>'],  # 汉字删除
    # [r'(\n|[^\d]\.|\?|!|\))( *(?:<sup>)?[0-9]+(?:<\/sup>)? *)(?:\n)', r'\1删除5：<u>\2</u>'],  # 单行数字  需要修改
    # [r'([0-9 ]+ Cases in[^\n.]*)(?:\n)', r'删除7：<u>\1</u>'],  # 100 cases...
    # [r'((?:ETHICS AND LAW IN CLINICAL|Ethics and Law in Clinical) *\n*(?:PRACTICE|Practice):.*)', r'删除22：<u>\1</u>'],
    # [r'(VARICOSE VEIN AND VENOUS ULCER \d+|SWELLINGS IN THE NECK \d+|\d+ A TEXTBOOK ON SURGICAL SHORT CASES|TESTIS, EPIDIDYMIS AND SCROTUM *\d+ *|\d* *SWOLLEN LEG *\d*|SYNDROME AND CERVICAL RIB *\d+|DISEASE, THORACIC OUTLET *\d+)',r'删除27：<u>\1</u>'],
    # [r'(?:\n)(\** *_*[A-Z]\.)(\\\])', r'\1删除28：<u>\2</u>'],
    #


    # [r'([a-z，,0-9’:：;()/] ?)(\n+)([a-z0-9‘)][^.][^.])',r'\1 删除换行 \3'],
    [r'([a-z，,0-9’;()/] *(?:>|<|\+|\–|%|\'|≥|=|≤|-)* *)(\n+)( *(?:>|<|\+|:|%|\'|≥|=|≤|-)* *([“,，./a-z‘)][^.]|\d+[^.][^.])|\(.{3,}\))',r'\1 删除换行1 \3'],
    [r'((?:i\.e\. *)|(?:e\.g\. *)|F[iI][gG][sS]?(?:ures?|URES?)?\. *)(\n+)( *(?:>|<|\+)* *[./a-zA-Z0-9‘()])',r'\1 删除换行2 \3'],
    [r'((?:>|<|\+)* *[./a-zA-Z0-9‘(),] *)(\n+)( *(?:i\.e\. *)|(?:e\.g\. *))',r'\1 删除换行2 \3'],
    [r'(?<=\n)(.*\([^\n()]*)(\n+)([^\n()]*\).*)',r'\1 删除换行3 \3'],



    [r'(=+\n+)((?:.*\n+)(?:.*USA_?\n+)+)',r'\1删除30：<u>\2</u>\n'],
    [r'(?:\n|^)((?:©.*\d{4}\n*)(?:.*(?:https?:\/\/(?:www\.)?|www\.)?[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9]{2,})+(?:\/[^ \n\u4e00-\u9fa5]*)?))',r'删除1：<u>\1</u>'],#版权介绍
    [r'(?:\n|^)((.*(?:https?:\/\/(?:www\.)?|www\.)?[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9]{2,})+(?:\/[^ \n\u4e00-\u9fa5]*)?\n*)(©.*\d{4}))',r'删除1：<u>\1</u>'],


    [r'(?:\n|^)((?:.*class="ContactIcon">.*\n+)(?:.*\n)*?)(#* *Keywords|#* *Abstract)',r'删除2：<u>\1</u>\n\2'],
    [r'(?:\n|^)((?:.*class="ContactIcon">.*\n+)(?:.*\n)*)(Email:.*)',r'\n删除2：<u>\1\2</u>'],

    [r'(?:[^\n])(\*\*Fig(?:ures?|\.) ?\d+[.-]\d+[^\n*]*\*+)',r'删除3：<u>\1</u>'],
    # [r'(?<=\n)(\**F[iI][gG][sS]?(?:ures?|URES?|\.) ?[0-9A-Z]+([.-]\d+)*[:：.]?(?:\n+(?:[^\n ]{1,} ){4,}.*[^\n.?!](?=\n)|.*))',r'删除3：<u>\1</u>'],#图
    [r'(?<=\n)( *F[iI][gG][sS]?(?:ures?|URES?|\.) ?[0-9A-Z]+([.-]\d+)*[:：.]?(?:\n+ *(?:[^\n ]{1,} ){3,}.*|.*))',r'删除3：<u>\1</u>'],#图
    [r'(?:\n)(Table [0-9.]+ \. .*\n+)(\n<sup>(<em>)?[a-z ]+(<\/em>)?<\/sup>.*\n)+',r'删除4：<u>\1</u>'],#表
    [r'(?:\n|^)(Table \d+[-–.]\d+ • .*)',r'删除4：<u>\1</u>'],
    [r'(?:\n|^)(Table \d+[-–]\d+ [^\n•]*)(\n+[^\n|])',r'删除4：<u>\1</u>\2'],
    [r'(?<=\n)(Tablee? *\d+[：:].*)',r'删除4：<u>\1</u>'],


    [r'([_*]*This page intentionally left blank *(?:\d+|to match pagination of print book)?[_*]*)',r'删除6：<u>\1</u>'],


    [r'(￾|◻|||◆|†|￥\d*||\(●|■\(?)',r''],#特殊符号
    [r'(?:\n|^)( *&+ *)(?:\n)',r'删除8：<u>\1</u>\n'],

    [r'(?:\n)((?:In \d{4}.*(?:\n|$)+){2,})',r''],
    [r'([(（][^\d\n\(][^()（）\n]+(?:\(.{2,6}\))?[^()（）\n]*\d{4}[^()（）\n]*(?:\(.{2,6}\))?[^()（）\n]*[)）])',r'删除10：<u>\1</u>'],#（人物+年份）
    [r'(?:\n|^)(By [A-Z].*[^\n.])',r'删除11：<u>\1</u>'],#作者介绍
    [r'(?:\n|^)((?:Key Points[0-9]+\n+)(?:Case [0-9]+:.*)?)',r'删除12：<u>\1</u>'],#空标题
    [r'(?:\n|^)([*| ]*CASE CORRELATES[*| ]*\n*[*| -]*\n*[*| -●·]*See.*\n{0,2}[| -]*)',r'删除13：<u>\1</u>'],#案例例子删除
    [r'(?:\n|^)( *\'?[A-Z](?: ?[A-Z]){0,2})(?:\n|$)',r'删除14：<u>\1</u>'],#单行的单独字母
    # [r'[^\n*#][^\n*#](\\?[\[［(] *[0-9０-９ ]{1,3}(?:[-—–－,，、][0-9０-９ ]+)*\\?[)］\]])',r'删除15：<u>\1</u>'],#序号
    [r'(?:\n|^)(#* *(?:Recommended Reading|Bibllography|Bibliography|REFERENCES?|Further [Rr]eading|(?:CLINICAL)? *CASE CORRELATION|Suggested Reading|Disclosure Statement)\n*(?:.*\n*)*)(?:\n|$)',r'删除16：<u>\1</u>'],#推荐阅读删除
    [r'(?:\n|^|\()( *(?:Reproduced，?|Adapted) (?:with permission|from|by).*)(?:\n|\))',r'删除21：<u>\1</u>'],

    [r'(?:\n|^|\()( *Data from\D[^\n()（）]*\d{4}\D[^\n()（）\[\]]{0,20})(?:\n|\))',r'删除23：<u>\1</u>'],#数据来源类

    [r'(?:\n|^)( *Please refer to.*?)(?:\n)',r'删除24：<u>\1</u>'],
    [r'(\.)( *Please refer to.*?(?:\(p\. \d+\)\.\d+)?)(\D\.|\n)',r'\1删除24：<u>\2\3</u>'],

    [r'(?:\n|^)(See.*(?:page|Table|Case|text).*)',r'删除25：<u>\1</u>'],
    [r'(\([^()\n]*see[^()\n]*(?:page|Table|Case|text|Plate)[^()\n]*\))',r'删除25：<u>\1</u>'],

    [r'(?:\n|^)(Table \d+\.\d+)(\n+)(.*[^.?!])',r'\1 删除换行 \3'],
    [r'(?<=\n)((?:Case *\d+[:：].*\n*)|Duties of a Doctor *\n*| *Rheumatology *\n*|ORTHOPAEDIC *\n*|Anaesthesia *\n*|ANAESTHESIA *\n*|Neurology *\n*)(?:$)',r'\n删除29：<u>\1</u>'],
    [r'(?<=\n)( *Source *[：:].*)',r'删除31：<u>\1</u>'],
    [r'(?<=\n)(\(([A-Z][^A-Z\n\d]+ )+[A-Z][^A-Z\n\d]+\) *\n*)(?:$)',r'删除32：<u>\1</u>'],
    [r'(\([^()\n]*F[iI][gG][sS]?(?:ures?|URES?|\.)?[^()\n]*\))',r'删除33：<u>\1</u>'],
    [r'(?:\n)([●·])( *[。(])',r'\1'],
    [r'(\([^()\n]*EPA *\d+(?:[ ，]+\d+)*\))',r'删除34：<u>\1</u>'],


    #个例
    [r'(●+)(?:\n|$)',r'删除31：<u>\1</u>'],
    [r'(?:\n|^)(> Courtesy of Dr. Mae Melvin, Centers for Disease Control and Prevention\.?|> Reproduced, with permission, from USMLERx.com\.?|FAITH, VALUES AND CULTURE|Faith, Values and Culture|Kimberly L. DiMaria|Children’s Hospital Colorado, Aurora, CO, USA|QaQ一?|Type V|Type IV|Typel|[\.■]*m+|Orthopaedics?|TRAUMA AND ORTHOPAEDICS|Ty\.|RAYNAUD’S SYNDROME, BUERGER’S|Ists|Ce Wang|Red dot)(?:\n|$)',r'删除个例：<u>\1</u>'],
    [r'(?:\n|^)(Clinical Case Studies for the Family Nurse Practitioner， First Edition. Edited by Leslie Neal-Boylan|@ 2011 John Wiley & Sons， Inc. Published 2011 by John Wiley & Sons， Inc.*|Rigler’s double wall sign229)',r'删除个例：<u>\1</u>'],
    [r'(?:\n|^)([-\']? *(?:!|\.|;|【|。|\}|\)))', r'删除26：<u>\1</u>'],
    [r'(?:\n|^)( *CCFC\d{4} *)',r'删除18：<u>\1</u>'],
    [r'(?:\n|^)(References?\n*(?:\d+\..*\n*)+)',r'删除19：<u>\1</u>'],
    [r'(?:\n)((?:(?:.*((?:\d{4}(?: *.{0,9} *\d*)?[;；:：])|(?:[:：;；,，] *\d{4}))\d*(\([0-9A-Z]+\))?[:：]?[0-9A-Za-z]*(?:-\d+)*)[^\n)\]]{0,15}(\n{1,}|$)){2,})',r'删除20：<u>\1</u>'],
    [r'((.*website： *)?(?:https?[:：]\/\/(?:www\.)?|www\.)[ a-zA-Z0-9-]+(?:\.[a-zA-Z0-9]{2,})+(?:\/[^ \n\u4e00-\u9fa5]*)?)',r'删除9：<u>\1</u>'],#需要补充

    [r'([a-z，,0-9’:：;()/] *)(\n+)(删除\d+：<u>.*<\/u>\n*)+(\n*)( *(?:[“./a-z‘)][^.]|\d+[^.][^.]|\d+\.\d).*|\(.{3,}\).*)',r'\1 删除换行4 \5\n\3'],

    [r'(?:\n|^)((?:[^#\n•●©>·:： ]{1,} +){10,}[^\n ]*[a-z，,0-9’;(/] *)(\n+)( *[A-Z][^. ] *(?:[^#\n•●©>·:： ]{1,} +){10,}[^\n :：]*)',r'\1 删除换行5 \3'],
    [r'(?:\n|^)((?:[^#\n•●©>·:： ]{1,} +){10,}[^\n ]*[A-Z] *)(\n+)( *[a-z，,0-9’;)/][^. ] *(?:[^#\n•●©>·:： ]{1,} +){10,}[^\n :：]*)',r'\1 删除换行5 \3'],





]




class speicalProces:
    def __init__(self):
        pass
    def step0_common_clean(self,context,cp,lang):
        result = []

        ending_starts = cp.ending_starts()
        for ending_start in ending_starts:
            start = ending_start[0]
            context = cp.delete_page_ending(context, start)

        pattern_en = cp.clean_pattern_en()
        pattern_zh = cp.clean_pattern_zh()
        for item in context:
            # 1.正则
            if lang == "en":
                for pattern_item in pattern_en:
                    src = pattern_item[0]
                    tgt = pattern_item[1]
                    # print(pattern_item)
                    item = re.sub(src, tgt, item)
            else:
                for pattern_item in pattern_zh:
                    src = pattern_item[0]
                    tgt = pattern_item[1]
                    item = re.sub(src, tgt, item)
            result.append(item)
        return result






def clean_text(context, lang):
    split_token = "\n\n"
    if split_token not in context:
        split_token = "\n"
    sp = speicalProces()
    cp = clean_pattern()

    pattern_list = pattern_list_en
    for pattern_item in pattern_list:
        context = re.sub(pattern_item[0], pattern_item[1], context)




    context = context.split(split_token)
    result = sp.step0_common_clean(context,cp,lang)
    # result=sp.rm_lid_piece(result)
    # for item in result:
    #     print(item)

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
    # 对多标点进行替换
    context = re.sub(r'[。，](\s?[。，：；]){1,5}',r'。',context)
    context = re.sub(r'([,\.?])(\s?[?,\.]){1,5}',r'\1',context)
    return context




fw = open(r"C:\Users\Administrator\PycharmProjects\untitled\medical_case_handled\reclean4_medical_case_handled.jsonl", "a", encoding="utf-8")
# with open(r"C:\Users\Administrator\PycharmProjects\untitled\medical_case_handled\test.jsonl", "r", encoding="utf-8") as fs:
with open(r"C:\Users\Administrator\PycharmProjects\untitled\medical_case_handled\medical_case_handled_preformat.jsonl", "r",encoding="utf-8") as fs:

    lines = fs.readlines()
    for items in tqdm(lines):
        item = json.loads(items.strip())
        # if item["seq_id"] == "5a9815c6-c389-410a-884d-86bd79e6dc56":
        context = item["text"]
        lang = item["lang"]
        title = item["title"]
        context = re.sub(r'\xa0',r' ',context)
        context=re.sub(r'[\*\_]]{0,}',r'',context)
        context = clean_text(context, lang)
        context = post_process(context)
        # print(context)
        item["text"] = context
        item = json.dumps(item, ensure_ascii=False)
        # print(item)
        fw.write(item + "\n")
#
