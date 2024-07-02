from transformers import AutoTokenizer
import json
tokenizer = AutoTokenizer.from_pretrained("../basic_tools/tokenizer")
def tokenizer_lens(context):
    ids = tokenizer.encode(context)
    return len(ids)

def get_file_lens(file):
    file_path = "../../full_data/{}/{}_preformat.jsonl".format(file, file)
    lens = 0
    with open(file_path, "r", encoding="utf-8") as fs:
        for item in fs.readlines():
            item = json.loads(item)
            context = item["text"]
            lens += tokenizer_lens(context)
    print(lens)


# get_file_lens("baiduyidian")
# #8544953
# get_file_lens("dingxiangyisheng")
# get_file_lens("dingxiangyuan")
# get_file_lens("drug_detail_zh")
# get_file_lens("druginstruction")
# get_file_lens("guidelines")
# get_file_lens("MSD")
# get_file_lens("uptodate")
# get_file_lens("xiaoheyidian")
get_file_lens("xunyiwenyao")
get_file_lens("zhonghuayangsheng")
get_file_lens("renwei_linchuangzhushou")
