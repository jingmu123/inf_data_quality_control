# -*- coding: utf-8 -*-
import json
import os
# 定义不同类型的标注等级映射


class ParseLabelResult:
    def __init__(self,need_details=True,base_dir="./",file_name=""):
        # 读取并处理JSON文件
        self.need_details = need_details
        self.m = 10
        self.Beta = 0.01
        self.term_level={
            '错别字': 'level1', '缺少字母': 'level1', '数字误用': 'level1', '多余标点': 'level1', '缺少标点': 'level1', '标点错误': 'level1', '多余空格': 'level1', '空格代替标点': 'level1', '缺少空格-中文': 'level1', '换行空格': 'level1', '语句不通顺': 'level2', '缺少空格-英文': 'level2', '页码/数字': 'level2', '特殊符号': 'level2', '重复符号': 'level2', '缺少换行': 'level2', '序号格式不一致': 'level2', '多余换行': 'level3', '表格格式错误': 'level3', '公式格式错误': 'level3', '术语格式错误': 'level3', '无关文本': 'level3', '页眉': 'level3', '页脚': 'level3', '无关链接': 'level3', '语句/字词重复': 'level3','语句重复': 'level3', '有用性-轻': 'level3', '导航栏': 'level3', '栏目混乱-轻': 'level3', '数据安全': 'level3', '广告': 'level4', '有用性-重': 'level4', '准确性': 'level4', '侧栏': 'level4', '语义不完整': 'level4', '语义冲突': 'level4', '错误删除': 'level4', '表格正文混乱': 'level4', '完整性': 'level4', '栏目混乱-中': 'level4', '专业性': 'level4', '格式杂乱': 'level5', '乱码': 'level5', '文本碎片化/无意义': 'level5', '栏目混乱-重': 'level5', '违反医德': 'level5', '违法': 'level5', '负面价值观': 'level5', '歧视': 'level5', '政治敏感': 'level5'
        }
        self.level_param = {
            "level1": 0.5,
            "level2": 0.42,
            "level3": 0.26,
            "level4": 0.13,
            "level5": 0,
        }
        self.file_path = "{}/{}.jsonl".format(base_dir, file_name)

        self.save_dir = "{}/output".format(base_dir)
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)

    def init_val(self):
        self.score_list = []
        self.F = {}
        self.error_list = {}
        self.invalid_count = 0
        self.final_result = {}

    def get_label_info(self,result_info, text_len, ignore_key_list = []):
        # 获取标注结果
        label_info = []
        penaty = 0
        for label_values in result_info["text"]:
            if "province" not in label_values:
                continue
            [p_level1, p_level2] = label_values["province"]
            if p_level2 in ignore_key_list:
                continue

            problem_text = label_values["text"]
            comment = label_values["comment"] if "comment" in label_values else "无"
            assert len(problem_text) > 0

            level = self.term_level[p_level2]
            pena_val = self.level_param[level]
            ##todo: if comment=="全文"
            p_score = ((self.m/text_len)**pena_val)*(1+self.Beta*self.F[p_level2])*100
            penaty += p_score

            type_info = "{}#{}#{}#{}".format(p_level1, p_level2, problem_text, comment)
            label_info.append(type_info)
        result_score = 0 if penaty > 100 else 100-penaty
        return label_info, result_score

    def get_blobal_F(self, con):
        for line in con:
            data = json.loads(line)
            if not data.get("user_name"):
                continue
            # 标注规范性检查
            result_info = data.get("result_info",None)
            if result_info == None:
                continue
            for label_values in result_info["text"]:
                if "province" not in label_values:
                    continue
                [p_level1, p_level2] = label_values["province"]
                self.F[p_level2] = self.F.get(p_level2,0) + 1

    def write_info(self,label_info,user_name,text_info):
        type_all = "#".join(list(set([item.split("#")[1] for item in label_info])))
        type_all = type_all.replace("/","-")
        file_name = "{}/{}_{}_{}.txt".format(self.save_dir, type_all, text_info["seq_id"], user_name)

        with open(file_name, "w", encoding="utf-8") as fw:
            fw.write(text_info["text"])
            fw.write(user_name + "\n")
            fw.write("\n" + "=====" * 20 + "\n")
            try:
                fw.write("\n" + text_info["attr"]["obj_key"] + "\n")
            except:
                pass
            for item in label_info:
                fw.write(item + "\n")

    def process_data(self,ignore_key_list):
        with open(self.file_path, "r", encoding="utf-8") as fs:
            con = fs.readlines()

        self.get_blobal_F(con)
        for line in con:
            data = json.loads(line)
            if not data.get("user_name"):
                self.invalid_count+=1
                continue

            user_name, ids = data["user_name"], data["id"]
            text_info = data["source_info"]
            if "source_info" in text_info:
                text_info = text_info["source_info"]

            dataset = ""
            attr = {}
            if "dataset" in text_info:
                dataset = text_info["dataset"]
            if "attr" in text_info:
                attr = text_info["attr"]


            result_info = data.get("result_info",None)
            if result_info == None:
                self.error_list.setdefault(ids, {"name": user_name, "label_rel": data["result_info"]})
                self.invalid_count += 1
                continue


            # 获取标注结果
            text_len = len(text_info["text"])
            label_info,result_score = self.get_label_info(result_info,text_len,ignore_key_list)
            self.score_list.append(result_score)
            self.final_result[ids] = {
                "seq_id": "null" if "seq_id" not in text_info else text_info["seq_id"],
                "user_name": user_name,
                "label_info": label_info,
                "text":text_info["text"],
                "attr_info": attr,
                "dataset": dataset
            }
            if self.need_details:
                self.write_info(label_info,user_name,text_info)

        with open(f"{self.save_dir}/0000_final_result.json","w",encoding='utf-8') as fw:
            json.dump(self.final_result,fw,ensure_ascii=False,indent=4)

        return self.final_result

    def score_count(self, ignore_key_list=[]):
        self.init_val()
        final_result = self.process_data(ignore_key_list)
        clean_count = 0
        dirty_count = 0
        problem1 = {}
        problem2 = {}

        # for key,value in final_result.items():
        #     if len(value["label_info"]) == 0:
        #         clean_count += 1
        #     else:
        #         dirty_count += 1
        #         for item in value["label_info"]:
        #             item = item.split("#")
        #             level1 = item[0]
        #             level2 = item[1]
        #             problem1[level1] = problem1.get(level1,0) + 1
        #             problem2[level2] = problem2.get(level2,0) + 1

        for item in self.score_list:
            if item == 100:
                clean_count += 1
            else:
                dirty_count += 1

        S1 = round(clean_count/(clean_count+dirty_count),5)*100
        S2 = round(sum(self.score_list)/len(self.score_list),5)

        if len(ignore_key_list) == 0:
            print("采样量:",clean_count+dirty_count)
            print(f"干净文本:{clean_count}", f"脏文本:{dirty_count}")
            print([clean_count+dirty_count,self.F],",")
            print(f"各纬度问题频次F={self.F}")
            print(f"合格率={S1}%")
        if len(ignore_key_list) == 0:
            print(f"质量分={S2}")
        else:
            #print("忽略 \"{}\" 后质量分：{}".format("#".join(ignore_key_list),S2))
            pass
        return self.F, S2

def computer_ignore_1(problem_list):
    ignore_score = {}
    for key,val in problem_list.items():
        _, score = pr.score_count([key])
        ignore_score[key] = score
    ignore_score_sorted = sorted(ignore_score.items(),key=lambda x:x[1],reverse=True)
    #print(dict(ignore_score_sorted))
    return ignore_score_sorted

def computer_ignore_2(ignore_score_sorted):
    ignore_score = {}
    k = 3
    for i in range(k):
        for j in range(i+1,k):
            ignore_list = [ignore_score_sorted[i][0],ignore_score_sorted[j][0]]
            _, score = pr.score_count(ignore_list)
            key = "#".join(ignore_list)
            ignore_score[key] = score
    ignore_score_sorted = sorted(ignore_score.items(),key=lambda x:x[1],reverse=True)
    return ignore_score_sorted


if __name__ == '__main__':

    pr = ParseLabelResult(need_details=True,
                          base_dir="../datasets/bmj_case/iter0/sample/",
                          file_name="reclean0_bmj_case")
    problem_list,score = pr.score_count() # 默认为空，不忽略key

    ignore_score_sorted = computer_ignore_1(problem_list)
    print("推荐解决的单个问题顺序以及收益（供参考）：{}".format(dict(ignore_score_sorted)))
    ignore_score_sorted = computer_ignore_2(ignore_score_sorted)
    print("推荐解决的组合问题顺序以及收益（供参考）：{}".format(dict(ignore_score_sorted)))



# 干净文本:153 脏文本:147
# 各纬度问题频次F={'有用性-重': 8, '缺少换行': 56, '无关文本': 28, '公式格式错误': 5, '多余换行': 55, '页脚': 6, '有用性-轻': 41, '错误删除': 59, '栏目混乱-轻': 10, '表格格式错误': 12, '页码/数字': 13, '完整性': 13, '语义不完整': 12, '序号格式不一致': 5, '栏目混乱-中': 18, '页眉': 4, '语句/字词重复': 3, '表格正文混乱': 7, '错别字': 5, '多余标点': 2, '多余空格': 3, '栏目混乱-重': 5}
# 合格率=51.0%
# 质量分=65.25909
# 推荐解决的单个问题顺序以及收益（供参考）：{'错误删除': 72.28166, '多余换行': 68.74597, '有用性-轻': 68.35853, '无关文本': 67.09011, '缺少换行': 66.92422, '栏目混乱-中': 66.49335, '栏目混乱-重': 66.46811, '完整性': 66.3778, '有用性-重': 66.07726, '语义不完整': 66.04372, '页脚': 65.75789, '表格格式错误': 65.63747, '栏目混乱-轻': 65.51765, '表格正文混乱': 65.4418, '语句/字词重复': 65.41333, '页码/数字': 65.41202, '序号格式不一致': 65.40831, '错别字': 65.33014, '公式格式错误': 65.32678, '页眉': 65.32395, '多余空格': 65.30558, '多余标点': 65.27807}
# 推荐解决的组合问题顺序以及收益（供参考）：{'错误删除#多余换行': 76.5411, '错误删除#有用性-轻': 76.00433, '多余换行#有用性-轻': 72.05104}


# 干净文本:117 脏文本:183
# 各纬度问题频次F={'无关文本': 29, '有用性-重': 31, '错别字': 2, '错误删除': 45, '栏目混乱-中': 17, '缺少换行': 79, '页码/数字': 15, '有用性-轻': 38, '页眉': 5, '表格正文混乱': 4, '完整性': 14, '表格格式错误': 19, '多余换行': 55, '多余标点': 6, '栏目混乱-轻': 8, '序号格式不一致': 5, '栏目混乱-重': 8, '公式格式错误': 5, '语义不完整': 6, '缺少字母': 1, '多余空格': 2}
# 合格率=39.0%
# 质量分=59.70738
# 推荐解决的单个问题顺序以及收益（供参考）：{'错误删除': 66.06185, '有用性-重': 65.93564, '有用性-轻': 63.2544, '多余换行': 63.03506, '缺少换行': 62.15507, '栏目混乱-中': 61.80082, '栏目混乱-重': 61.75983, '无关文本': 61.39688, '表格格式错误': 61.06722, '完整性': 61.06554, '页码/数字': 60.10754, '语义不完整': 60.09647, '表格正文混乱': 60.07837, '栏目混乱-轻': 60.05796, '多余标点': 59.84808, '页眉': 59.84187, '错别字': 59.75733, '序号格式不一致': 59.74411, '多余空格': 59.72678, '公式格式错误': 59.70738, '缺少字母': 59.70738}
# 推荐解决的组合问题顺序以及收益（供参考）：{'错误删除#有用性-重': 72.29011, '错误删除#有用性-轻': 70.09674, '有用性-重#有用性-轻': 69.48265}
