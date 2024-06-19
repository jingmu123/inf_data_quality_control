import json
import uuid
from langdetect import detect
from tqdm import tqdm
import hashlib

file = "kepuyixia"
batch_name="20240321"
version="version1"
base_dir = f"../../../../full_data/{file}/"
base_file = f"{base_dir}/{file}_preformat.jsonl"
save_file = f"{base_dir}/{file}_esformat.jsonl"
fw = open(save_file, "w",encoding="utf-8")

with open(base_file, "r",encoding="utf-8") as fs:
    data_dict = {}
    count = 0
    for item in tqdm(fs.readlines()):
        item = json.loads(item)

        context = item["text"]
        title = item["title"]
        attr = {}
        attr["poster"] = item["attr"]["poster"]
        attr["text"] = context
        attr["title"] = title
        attr["video"] = item["attr"]["video"]
        attr["duration"] = None
        attr = json.dumps(attr,ensure_ascii=False)
        md5 = hashlib.md5(context.encode(encoding='UTF-8')).hexdigest()

        new_data = {
            "doc_id": count,
            "chunk_seq": 0,
            "title": title,
            "content": context,
            "type": "科普",
            "department": None,
            "year": "2022",
            "reference": {
               "url": item["attr"]["src_url"],
                "source":"kepuyixia",
                "attr_ext":attr,
            },
            "video_id": md5,
        }
        count += 1
        new_data = json.dumps(new_data,ensure_ascii=False)
        fw.write(new_data + "\n")


