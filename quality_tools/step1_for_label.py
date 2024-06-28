import json
import os
import random

from langdetect import detect
from langdetect import detect_langs
from langdetect import DetectorFactory


# DetectorFactory.seed = 0
# base_dir = "/Users/mirli/worker/code/odps/job/"
def sample_data(file, lang_tag, save_file, append_title=False, need_special_split=False, need_line_num=True):
    global split_token
    new_dir = f"{save_dir}/sample"
    if not os.path.exists(new_dir):
        os.makedirs(new_dir)
    # fw = open(f"{new_dir}/{save_file}",'w',encoding='utf-8')
    con = []
    with open(f"{base_dir}/{file}.jsonl", "r", encoding="utf-8") as fs:
        for line in fs.readlines():
            try:
                item = json.loads(line)
            except Exception as e:
                continue

            if "text" not in item or item["text"] == None:
                print("error_happ!!!", item)
                continue
            if len(item["text"].strip(" ")) == 0:
                continue

            lang = item["lang"]
            if "tokens" in item:
                item["tokens"] = ""
            if "html" in item:
                item["html"] = ""

            if lang == lang_tag or lang_tag == "all":
                if append_title and "title" in item:
                    text = item["text"]
                    title = item["title"]
                    if title != None:
                        if title not in text:
                            item["text"] = f"{title}\n{text}"
                context = item["text"]
                if "page_num" in item["attr"]:
                    page_num = item["attr"]["page_num"]
                    if isinstance(page_num, list):
                        if len(page_num) == 0:
                            page_num = 0
                        else:
                            page_num = page_num[0]
                    else:
                        pass
                    context = "页码:{}".format(page_num) + "\n" + context


                if need_special_split:
                    if lang == "en":
                        split_token = "."
                    else:
                        split_token = "。"
                new_context = []
                # url = json.loads(item["attr"])["exta"]["url"]
                # new_context.append(f"url: {url}")
                if not need_line_num:
                    new_context = context
                else:
                    for count, line_item in enumerate(context.split(split_token)):
                        if "|" in line_item:
                            new_context.append(f"{line_item}")
                        else:
                            new_context.append(f"【{count}】{line_item}")
                    new_context = split_token.join(new_context)
                item["text"] = new_context
                line = json.dumps(item, ensure_ascii=False) + "\n"

                con.append(line)

    sample_con = random.sample(con, min(len(con), 600))
    print(len(sample_con))
    fw_label = open(f"{new_dir}/{save_file}", 'w', encoding='utf-8')
    for item in sample_con:
        fw_label.write(item)


file_name = "medicalpdf"
base_dir = f"../../full_data/{file_name}/"
save_dir = f"../datasets/{file_name}/iter2/"
file = f"{file_name}_clean_en"
# save_file_en = "reclean4_dingxiangyisheng_en_label.jsonl"
save_file_zh = f"reclean2_{file_name}_en_label.jsonl"
split_token = "\n\n"
# 指定参数:
#   need_special_split=False # 是否需要特殊换行，解决无换行问题
#   need_line_num=True  #是否需要行前索引
#   append_title=rue # 是否添加title

# en/zh, 还是不区分，大家根据需要自取
sample_data(f"{file}", "all", save_file_zh, append_title=True, need_special_split=False, need_line_num=True)
# sample_data(f"{file}","en",save_file_en,append_title=True,need_special_split=False,need_line_num=True)
# sample_data(f"{file}","all",save_file_en,append_title=True,need_special_split=False,need_line_num=True)
