# -*- coding: utf-8 -*-
import json

file="aiaiyi_zhenliaozhinan"
save_file = f"C:/Program Files/lk/projects/pdf/{file}/{file}.jsonl"
fw = open(save_file, 'w',encoding="utf-8")

from transformers import AutoTokenizer
tokenizer = AutoTokenizer.from_pretrained("../../../basic_tools/tokenizer")
def tokenizer_lens(context):
    ids = tokenizer.encode(context)
    return len(ids)
sum_lens = 0

with open(f"C:/Program Files/lk/projects/pdf/{file}/{file}_clean.jsonl", "r",encoding="utf-8") as fs:
    for item in fs.readlines():
        item = json.loads(item)
        context = item["text"]
        lens = tokenizer_lens(context)
        sum_lens += lens

with open(f"C:/Program Files/lk/projects/pdf/{file}/{file}_clean.jsonl", "r",encoding="utf-8") as fs:
    for item in fs.readlines():
        item = json.loads(item)
        item["tags"] = {
                        "id": item["seq_id"],
                        "clean_iters":"zh:5, en:3",
                        "quality_score":"zh:95.91, en:95.86",
                        "binary_score": "zh:90.00%, en:88.07%",
                        "class_ratio_doc": {},
                        "class_ratio_tokenize": {},
                        "item_tokens": tokenizer_lens(item["text"]),
                        "dataset_tokens": sum_lens,
                        "bia_class": "指南"
                        }

        item = json.dumps(item,ensure_ascii=False)
        fw.write(item+"\n")
