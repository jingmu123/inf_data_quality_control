import json
import uuid
from langdetect import detect
from tqdm import tqdm

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
save_file = f"{base_dir}/all_data_format.json"
fw = open(save_file, "w",encoding="utf-8")

with open(base_file, "r",encoding="utf-8") as fs:
    for items in tqdm(fs.readlines()):
        item = json.loads(items)
        if "attr" not in item:
            print(items)
        attr = json.loads(item["attr"])

        uid = str(uuid.uuid4())
        context = item["text"]
        lang = detect_language(context)

        data_dict = {}
        src_url = attr["src_url"]
        if src_url not in data_dict:
            new_data = {
                "seq_id": uid,
                "title": item["title"],
                "text": context,
                "tags": {},
                "lang": lang,
                "attr": {
                    "category": [attr["category"]],
                    "src_url": attr["src_url"],
                    "summary": attr["summary"],
                    "create_time": attr["create_time"],
                },
                "ext": None,
                "dataset": "dingxiangyisheng",
                "batch_name": "20240312",
                "version": "version0",
            }
        else:
            new_data = data_dict[src_url]
            new_data["attr"]["category"].append(src_url)
        data_dict[src_url] =new_data

    print("saving data....")
    for key,val in data_dict.items():
        data = json.dumps(val, ensure_ascii=False)
        fw.write(data + "\n")