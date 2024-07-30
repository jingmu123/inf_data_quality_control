import json
import re
import os
import queue
import Levenshtein
from post_order import reorder_context
from post_order import final_post_process_zh, sort_text_by_pix

lowercase_letters = "a-zà-öø-ÿа-яşćăâđêôơưþðæøå"
uppercase_letters = "A-ZÀ-ÖØ-ßА-ЯŞĆĂÂĐÊÔƠƯÞÐÆØÅ"
# Remove hyphen in current line if next line and current line appear to be joined
hyphen_pattern = re.compile(rf'.*[{lowercase_letters}][-]\s?$', re.DOTALL)
zh_pattern = re.compile(r'[\u4e00-\u9fa5]{3,}',  re.DOTALL)

class TablePostProcess:
    
    def __init__(self):
        pass
    
    def should_merge(self,prev_line, curr_line, curr_index):
        """判断是否需要合并"""
        
        # todo1: 还需要商榷，留待后面解决
        # return False
        # 第一列一般为标题，第一列为空，或者上一行item[-1]是一个·说明当前行还是在描述上一行的内容
        if not curr_line[0] or (curr_index > 0 and prev_line[0] and prev_line[0][-1] in ['.']):
            return True

        # 第一列不为空，后面的列有空的
        # elif any(not item for item in curr_line[1:]):
        #     return True

        elif any(
                # 句子中有逗号且居首不为大写或数字
                ("," in item and not item[0].isupper() and not item[0].isdigit())
                # 句中有(且居首不为大写
                or ("(" in item and not item[0].isupper() and item[0] not in ['*', '†'] and not item[0].isdigit())
                # 居首为小写
                or item[0].islower()
                # 句尾为标点，不太合适
                # or (item[-1] in ['.','?','!',','])
                for item in curr_line if item
        ):
            return True
        else:
            return False


    def merge_data(self, last_line, line):
        merged_line = []
        for last_index, last_item in enumerate(last_line):
            # 当前行不为空再加换行
            if line[last_index]:
                merged_line.append(last_item + '\\n' + line[last_index])
            else:
                merged_line.append(last_item + line[last_index])
        return merged_line
    
    def filter_extra_table(self,line,pre_text_k,post_text_k):
        extra_table = False
        max_line = ""
        max_len = 0
        for line_item in line:
            if len(line_item)> max_len:
                max_len = len(line_item)
                max_line = line_item
        # todo2: 表头和正文； 
        if len(re.findall("Part \d+:",max_line)) > 0:
            #print("filter pattern1",max_line)
            extra_table = True
            return extra_table
        for item in pre_text_k+post_text_k:
            score = Levenshtein.jaro_winkler(max_line, item)
            #print(score,max_line,"|||",item)
            if score > 0.85:
                extra_table = True
                return extra_table
        #todo3: 表格描述，是可以从表格里面拿出来的；
        return extra_table
    
    def post_process_table(self,table_data,pre_text_k,post_text_k):
        processed_data = []
        for index, line in enumerate(table_data):
            # 默认第一行是标题行，直接添加且第二行不与第一行连接
            
            extra_table = self.filter_extra_table(line,pre_text_k,post_text_k)
            if extra_table == True:
                continue
            
            if len(processed_data) == 0:
                processed_data.append(line)
            else:
                # 判断是否符合连接条件
                if self.should_merge(table_data[index - 1], line, index):
                    if index > 0:  # 确保不是第一行
                        last_line = processed_data.pop()
                        merged_line = self.merge_data(last_line, line)
                        processed_data.append(merged_line)  # 添加合并后的行
                        index -= 1  # 因为删除了一行，所以当前行的索引需要减1
                    else:
                        # 如果是第一行，就不需要合并，直接continue
                        processed_data.append(line)
                        continue
                # 否则直接添加
                else:
                    processed_data.append(line)
        return processed_data

    # 去除前后不属于表格的内容
    def clean_table_data(self,table_data):
        # todo : 句尾 this table represents the....
        for index, line in enumerate(table_data):
            if index < 1:
                try:
                    # 正常表格第一行第一列大写开头
                    if len(line[0]) == 0 or line[0].lstrip().islower() or (not line[0] and line[1].islower()):
                        del table_data[index]
                    else:
                        for item in line:
                            if 'Table' in item or re.search('Table', item):
                                del table_data[index]
                                break
                except:
                    #print(table_data)
                    print("clean_table_data error!!!",line,len(line))
                    exit(0)


        return table_data

    # 表格转md
    def to_md(self, table_data):
        md_table = ""
        for i, line in enumerate(table_data):
            new_line = []
            for item in line:
                item = re.sub(r'\n',' ',item)
                new_line.append(item)
            # new_line.append(re.sub(r'\n','\\n',item) for item in line)
            md_line = '| ' + ' | '.join(new_line) + ' |'
            md_table += md_line + '\n'
            if i == 0:
                md_table += '|' + '--------|' * len(new_line) + '\n'
        return md_table
    
    def final_pip(self,table_data,pre_text_k,post_text_k):
        new_data = self.post_process_table(table_data,pre_text_k,post_text_k)
        for i in range(3):
            new_data = self.clean_table_data(new_data)
        new_data_md = self.to_md(new_data)
        return new_data_md
        

def block_separator(line, block_type):
    sep = "\n"
    if block_type == "Text":
        sep = "\n\n"
    return sep + line


def get_context_text(content,raw_idx,k):
    pre_text_k = []
    post_text_k = []
    num = 1
    while raw_idx-num >= 0 and num <= k:
        if content[raw_idx-num]["type"] == "Table":
            break
        pre_text_k.append(content[raw_idx-num]["text"])
        num += 1
    num = 1
    while raw_idx+num < len(content) and num <= k:
        if content[raw_idx+num]["type"] == "Table":
            break
        post_text_k.append(content[raw_idx+num]["text"])
        num += 1       
    return pre_text_k,post_text_k


def post_replace(context):
    context = context.strip(" ").strip("\n").strip(" ").strip("\n")
    # 消除分界符失效  --*- 前面需要有连续两个\n;
    context = re.sub('\n    --', "\n\n    --", context)
    # 消除空格问题
    context = re.sub(r'\n +\n', "\n\n", context)
    context = re.sub(r'\n +\n', "\n\n", context)
    # 去掉过多\n的情况
    context = re.sub("\n{2,}", "\n\n", context)
    return context


def read_jsonl_file(file_path):
    with open(file_path, "r", encoding="utf-8") as fs:
        content = json.load(fs)["content"]
        return [json.loads(line) for line in content]


def process_text_language(context, zh_pattern):
    long_text = ''
    for texts in context:
        if isinstance(texts['text'], str):
            long_text += texts['text'] or ''
    return 'zh' if zh_pattern.search(long_text) else 'en'


def merge_text_blocks(page_result, fw, pdf_name):
    page = page_result["page"]
    img_box = page_result["img_box"]
    full_text = ""
    pre_block_type = None
    raw_info = []

    for idx, item in enumerate(page_result["context"]):
        # print(item)
        block_type = item["type"]
        table_info = {}

        if item["text"] == None:
            if block_type == "Table":
                continue
            else:
                print(item)
                print(file)
                exit(0)
        if block_type == "Table":
            pre_text_k, post_text_k = get_context_text(page_result["context"], idx, 3)
            raw_context = item["text"]
            new_text = "\n\n{}\n\n".format(tpp.final_pip(raw_context, pre_text_k, post_text_k))
            # print(new_text)
            table_info = {
                "raw_table_list": raw_context,
                "pre_text_k": pre_text_k,
                "post_text_k": post_text_k,
            }
        elif pre_block_type:
            new_text = block_separator(item["text"], block_type)
        else:
            new_text = item["text"]

        if full_text and hyphen_pattern.match(new_text) and re.match(rf"^[{lowercase_letters}]", new_text):
            full_text = re.split(r"[-—]\s?$", full_text)[0]
            full_text = full_text.rstrip() + new_text.lstrip()
        else:
            full_text += new_text
        pre_block_type = block_type
        raw_info.append({
            "block_text": new_text,
            "block_text_old": item["old_text"],
            "raw_context": item["raw_context"],
            "block_type": item["type"],
            "full_blocks": item["full_bbox"],
            "position": item["position"],
            "table_info": table_info,
        })
    # print(full_text)
    full_text = post_replace(full_text)
    # print(full_text)
    data = {
        "page": page,
        "text": full_text,
        "attr": {
            "raw_info": raw_info,
            "img_box": img_box,
            "obj_key":pdf_name
        },
    }
    # print(json.dumps(data,ensure_ascii=False))
    data = json.dumps(data, ensure_ascii=False)
    fw.write(data + "\n")


def save_text_file(data, file_path):
    with open(file_path, "w", encoding="utf-8") as fw:
        fw.write(json.dumps(data) + "\n")


def jsonl_to_md(file, save_dir,pdf_name):
    con = read_jsonl_file(file)
    fw = open("{}/{}.txt".format(save_dir,pdf_name.split("/")[-1].replace(".pdf","")),"w",encoding="utf-8")
    for page_result in con:
        # 判断文本语言
        lang = process_text_language(page_result["context"], zh_pattern)

        # 解决栏目混乱问题
        sorted_raw_info = sort_text_by_pix(page_result["context"])

        # 分中英文拼接文本
        sorted_raw_info = final_post_process_zh(sorted_raw_info, lang)

        page_result["context"] = sorted_raw_info

        # merge layout
        merge_text_blocks(page_result, fw, pdf_name)

    fw.close()


# with open("med_ocr_medicalpdf.json","r",encoding="utf-8") as fs:
#     data = json.load(fs)
#     path_map = {}
#     for item in data:
#         for key,val in item.items():
#             new_key = "oss://inf-beta/{}".format(key)
#             file_path = "/".join( val["output_location"].split("/")[-2:] )
#             path_map[file_path] = new_key
    
with open("med_ocr_stage5.json","r",encoding="utf-8") as fs:
    data = json.load(fs)
    path_map = {}
    for key,val in data.items():
        if len(val) == 0:
            continue
        new_key = "oss://inf-beta/{}".format(key)
        file_path = "/".join( val["output_location"].split("/")[-2:] )
        path_map[file_path] = new_key


# print(path_map)
from tqdm import tqdm
tpp = TablePostProcess()
er_f = open("error_aixi1.txt","w",encoding="utf-8")
for key,val in tqdm(path_map.items()):
    file = "/home/ma-user/work/lipengfei/data/medical_stage_5/step2_pdf_surya/{}".format(key)
    save_dir = "/home/ma-user/work/lipengfei/data/medical_stage_5/step3_aixi_parse/"
    try:
        jsonl_to_md(file,save_dir,val)
    except:
        er_f.write(key+"\n")
        continue
    # break