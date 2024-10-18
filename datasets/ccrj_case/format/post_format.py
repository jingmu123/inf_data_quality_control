# -*- coding: utf-8 -*-
import json

file="ccrj_case"
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
                        "clean_iters":"1",
                        "quality_score":"100",
                        "binary_score": "100%",
                        "class_ratio_doc": {},
                        "class_ratio_tokenize": {},
                        "item_tokens": tokenizer_lens(item["text"]),
                        "dataset_tokens": sum_lens,
                        "bia_class": "临床案例"
                        }

        item = json.dumps(item,ensure_ascii=False)
        fw.write(item+"\n")
