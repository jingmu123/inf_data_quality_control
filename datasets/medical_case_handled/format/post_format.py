# -*- coding: utf-8 -*-
import json

file="medical_case_handled"  # 任务名称
save_file = f"C:/Users/Administrator/Desktop/original_data/{file}/{file}.jsonl"  # 保存路径，就在本地清洗好的全量，任务名_clean文件下，就叫任务名.jsonl
fw = open(save_file, 'w',encoding="utf-8")

from transformers import AutoTokenizer
tokenizer = AutoTokenizer.from_pretrained("../../../basic_tools/tokenizer")
def tokenizer_lens(context):
    ids = tokenizer.encode(context)
    return len(ids)
sum_lens = 0

with open(f"C:/Users/Administrator/Desktop/original_data/{file}/{file}_clean.jsonl", "r",encoding="utf-8") as fs:  # 本地清洗好的全量数据，任务名_clean文件
    for item in fs.readlines():
        item = json.loads(item)
        context = item["text"]
        lens = tokenizer_lens(context)
        sum_lens += lens

with open(f"C:/Users/Administrator/Desktop/original_data/{file}/{file}_clean.jsonl", "r",encoding="utf-8") as fs: # 本地清洗好的全量数据，任务名_clean文件
    for item in fs.readlines():
        item = json.loads(item)
        item["tags"] = {
                        "id": item["seq_id"],
                        "clean_iters":"5",  # 清洗轮次
                        "quality_score":"98.33",  # 质量分
                        "binary_score": "93.33%",  # 合格率
                        "class_ratio_doc": {},
                        "class_ratio_tokenize": {},
                        "item_tokens": tokenizer_lens(item["text"]),
                        "dataset_tokens": sum_lens,
                        "bia_class": "临床案例"  # 任务类别
                        }

        item = json.dumps(item,ensure_ascii=False)
        fw.write(item+"\n")
