# -*- coding: utf-8 -*-
import json
from tqdm import tqdm
file="medicalpdfv2"
save_file = f"../../../../full_data/{file}/{file}.jsonl"
fw = open(save_file, 'w',encoding="utf-8")

from transformers import AutoTokenizer
tokenizer = AutoTokenizer.from_pretrained("../../../basic_tools/tokenizer")
def tokenizer_lens(context):
    ids = tokenizer.encode(context)
    return len(ids)
sum_lens = 0
class_ratio_token= {}
class_ratio_doc= {}
with open(f"../../../../full_data/{file}/{file}_v0724_merge.jsonl", "r",encoding="utf-8") as fs:
    for item in tqdm(fs.readlines()):
        item = json.loads(item)
        context = item["text"]
        lens = tokenizer_lens(context)
        sum_lens += lens
print(sum_lens)

error_case = 0
with open(f"../../../../full_data/{file}/{file}_v0724_merge.jsonl", "r",encoding="utf-8") as fs:
    for item in tqdm(fs.readlines()):
        item = json.loads(item)
        try:
            seq_id = item["seq_id"]
        except:
            error_case += 1
            continue

        item["tags"] = {
                "id": seq_id,
                "clean_iters":7,
                "quality_score":"en: 51%",
                "class_ratio_doc":class_ratio_doc,
                "class_ratio_tokenize":class_ratio_token,
                "item_tokens": tokenizer_lens(item["text"]),
                "dataset_tokens": sum_lens,
                "bia_class":  "书籍"
        }
        item = json.dumps(item,ensure_ascii=False)
        fw.write(item+"\n")

print(error_case)
