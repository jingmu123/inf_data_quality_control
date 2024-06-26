import json
from tqdm import tqdm
count = 0

file = "guidelines_liangyong_surya"
base_dir = "../../../../full_data/{}".format(file)
def update_progress():
    progress_bar.update(1)
with open("{}/{}_clean_en.jsonl".format(base_dir,file),"r",encoding="utf-8") as fs:
    item = fs.readline()
    progress_bar = tqdm(total=43191, desc='Processing file')
    while item:
        item = item.strip("\n")
        line = json.loads(item)
        book_name = line["attr"]["obj_key"]
        book_name = book_name.split("/")[-1].replace("pdf","txt")
        save_path = "{}/split_book/{}".format(base_dir, book_name)
        fw = open(save_path,"a+",encoding="utf-8")
        fw.write(item+"\n")
        item = fs.readline()
        update_progress()
        # break