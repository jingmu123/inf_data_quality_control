import json
import uuid
from langdetect import detect
from tqdm import tqdm
import hashlib

import concurrent.futures
from tqdm import tqdm
import sys


def detect_language(content):
    #print("context",content)
    lang = detect(content)
    if lang == "zh-cn":
        return "zh"
    if lang == "en":
        return "en"
    return "None"

file = "medicalstage5v2"
batch_name="20240730"
version="version0"

base_dir = f"../../../../full_data/{file}/"
base_file = f"{base_dir}/{file}_all.jsonl"
save_file = f"{base_dir}/{file}_preformat.jsonl"

fw = open(save_file, "w",encoding="utf-8")
def update_progress():
    progress_bar.update(1)
progress_bar = tqdm(total=12000, desc='Processing file')
with open(base_file, "r",encoding="utf-8") as fs:
    data_dict = []
    count = 0
    jishu_count = 0
    items = fs.readline()
    while items:
        update_progress()
        jishu_count += 1
        try:
            item = json.loads(items)
        except Exception as e:
            count += 1
            continue
        if "seq_id" not in item:
            uid = str(uuid.uuid4())
        else:
            uid = item["seq_id"]
        assert len(item["text"]) == 1
        context = item["text"][0]["text"]
        if len(context) == 0:
            jishu_count += 1
            if jishu_count % 1000 == 0:
                print(jishu_count)
            items = fs.readline()
            continue
        if "lang" in item and item["lang"] != "":
            lang = item["lang"]
        else:
            try:
                lang = detect_language(context)
            except:
                lang = "None"

        # md5 = hashlib.md5(context.encode(encoding='UTF-8')).hexdigest()
        if True: # or md5 not in data_dict:
            attr = {}
            attr["page_num"] = item["page"] + 1
            attr["obj_key"] = "oss://inf-beta/home/medical/pdf_stage5/zhongyi/pdf/{}".format(item["obj_key"])
            title = item["obj_key"].split("/")[-1].replace(".pdf","")
            new_data = {
                "seq_id": uid,
                "title": title,
                "text": context,
                "tags": {},
                "lang": lang,
                "attr": attr,
                "ext": None,
                "dataset": file,
                "batch_name":batch_name,
                "version": version,
            }
        else:
            pass
        # data_dict[md5] = new_data
        # data_dict.append(md5)
        jishu_count += 1
        if jishu_count % 1000 ==0:
            print(jishu_count)
        data = json.dumps(new_data, ensure_ascii=False)
        fw.write(data + "\n")
        items = fs.readline()

