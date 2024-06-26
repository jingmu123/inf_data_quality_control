import json
import os
from tqdm import tqdm

file = "guidelines_liangyong_surya"
base_dir = "../../../../full_data/{}/split_book".format(file)
fw = open("../../../../full_data/{}/{}_merge.jsonl".format(file, file), "w")
def update_progress():
    progress_bar.update(1)



progress_bar = tqdm(total=2206, desc='Processing file')

for file in os.listdir(base_dir):
    with open("{}/{}".format(base_dir,file),"r",encoding="utf-8") as fs:
        context = []
        final_item = {}
        lang_list = []
        for idx,item in enumerate(fs.readlines()):
            item = json.loads(item.strip())
            if idx == 0:
                final_item = item
            if len(item["text"]) == 0:
                continue
            if len(item["text"].split("\n\n")) == 1 and len(item["text"]) < 50:
                continue
            lang_list.append(item["lang"])
            page_num = item["attr"]["page_num"]
            context.append([page_num,item["text"],item["lang"]])
        context = sorted(context,key=lambda x:x[0])
        final_context = []
        for pice in context:
            final_context.append(pice[1])
        final_context = "\n\n".join(final_context)
        final_item["text"] = final_context
        final_item["attr"]["raw_info"] = ""
        final_item["lang"] = list(set(lang_list))
        data = json.dumps(final_item,ensure_ascii=False)
        fw.write(data+"\n")
        update_progress()
