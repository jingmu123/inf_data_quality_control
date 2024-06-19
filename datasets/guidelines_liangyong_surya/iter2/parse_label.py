import json
import re
with open("sample/output/en_0131.json","r",encoding="utf-8") as fs:
    data = json.load(fs)
    for key,val in data.items():
        label_info = val["label_info"]
        print(val["seq_id"])
        for item in label_info:
            [type1,type2,start,end,des] = item.split("#")
            if type2 != "无关文本":
                continue
            # if "." in des or "[" in des or "]" in des or len(des.replace(" ","")) == 1 or len(re.findall("\d",des))>0:
            #     print(item)

            # cite error : done!
            if "[" in des or "]" in des:
                continue
            # done
            if "小狗" in des:
                continue
            if len(re.findall("\d",des))>0:
                print(item)
            # if "科研" in des:
            #     print(item)

