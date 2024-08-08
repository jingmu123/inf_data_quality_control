# -*- coding: utf-8 -*-
import json


file="guidelines_wx"
save_file = f"../../../../full_data/{file}/{file}.jsonl"
fw = open(save_file, 'w',encoding="utf-8")

from transformers import AutoTokenizer
tokenizer = AutoTokenizer.from_pretrained("../../../basic_tools/tokenizer")
def tokenizer_lens(context):
    ids = tokenizer.encode(context)
    return len(ids)
sum_lens = 0
class_ratio_token = {}
class_ratio_doc = {}
with open(f"../../../../full_data/{file}/{file}_clean.jsonl", "r",encoding="utf-8") as fs:
    for item in fs.readlines():
        item = json.loads(item)
        context = item["text"]
        lens = tokenizer_lens(context)
        sum_lens += lens

with open(f"../../../../full_data/{file}/{file}_clean.jsonl", "r",encoding="utf-8") as fs:
    for item in fs.readlines():
        item = json.loads(item)
        item["tags"] = {
                        "id": item["seq_id"],
                        "clean_iters":0,
                        "quality_score":"",
                        "class_ratio_doc": class_ratio_doc,
                        "class_ratio_tokenize": class_ratio_token,
                        "item_tokens": tokenizer_lens(item["text"]),
                        "dataset_tokens": sum_lens,
                        "bia_class": "诊疗指南"
                        }

        item = json.dumps(item,ensure_ascii=False)
        fw.write(item+"\n")
