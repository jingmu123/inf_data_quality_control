import json
import uuid
from langdetect import detect
from tqdm import tqdm
import hashlib

def detect_language(content):
    #print("context",content)
    lang = detect(content)
    if lang == "zh-cn":
        return "zh"
    if lang == "en":
        return "en"
    return "None"

base_dir = "../../../../full_data/renwei_linchuangzhushou/"
base_file = f"{base_dir}/all_data.jsonl"
save_file = f"{base_dir}/all_data_preformat.jsonl"
fw = open(save_file, "w",encoding="utf-8")

with open(base_file, "r",encoding="utf-8") as fs:
    data_dict = {}
    for items in tqdm(fs.readlines()):
        item = json.loads(items)
        uid = str(uuid.uuid4())
        context = item["text"]
        lang = detect_language(context)
        md5 = hashlib.md5(context.encode(encoding='UTF-8')).hexdigest()
        if md5 not in data_dict:
            if "attr" in item:
                attr = json.loads(item["attr"])
                temp_attr = {
                    "is_clean": 2,
                    "category": attr["category"] if "category" in attr else None,
                    "src_url": attr["src_url"] if "src_url" in attr else None,
                    "summary": attr["summary"] if "summary" in attr else None,
                    "create_time": attr["create_time"] if "create_time" in attr else None,
                }
            else:
                temp_attr = {"is_clean":2,"category":None,"src_url":None,"summary":None,"create_time":None}

            new_data = {
                "seq_id": uid,
                "title": item["title"] if "title" in item else None,
                "text": context,
                "tags": {},
                "lang": lang,
                "attr": temp_attr,
                "ext": None,
                "dataset": "renwei_linchuangzhushou",
                "batch_name": "20240319",
                "version": "version4",
            }

        else:
            print("重复---",items)
        data_dict[md5] = new_data


    print("saving data....")
    for key,val in data_dict.items():
        data = json.dumps(val, ensure_ascii=False)
        fw.write(data + "\n")