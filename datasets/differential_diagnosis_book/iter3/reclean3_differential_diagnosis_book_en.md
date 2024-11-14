## reclean1B、2_differential_diagnosis_book_en问题
1. 对每本书的开头结尾进行统计分析，统计出批量开头和结尾删除的标记。并进行测试删除。

批量结尾删除：
```
    def delete_page_ending(self, context):
        ending_starts = [
            [r'(^|\n)[#\* _]*(APPENDIX.{0,8})[#\* _]*($|\n)'],
            [r'(^|\n)[#\* _]{0,4}(Reference|REFERENCE)[Ss]?[#\* _]{0,4}($|\n)'],
        ]
        for start in ending_starts:
            flag = False
            start_index = len(context)
            ref_started = [start_index]
            for index, item in enumerate(context):
                if re.search(start[0], item.strip()):
                    ref_started.append(index)
                    flag = True
            
            start_index = ref_started[-1]

            if start_index != len(context):
                for i in range(len(context)-start_index):
                    context[start_index] = "结尾批量删除-1:<u>{}</u>".format(context[start_index])
                    start_index += 1
            if flag:
                break
            # context = context[0:start_index]

        return context
```

批量开头删除：
```
    def delete_page_start(self, context):
        end_pattern = [
            [r'(^[#\*_ ]*(Abstract|I?ntroduction|Section\||INTRODUCTION|CHAPTER _1_|FIrs T-Tr IMEsTEr U LTr Aso UNd|DUKERADIOLOGT_ _CASE REVIEW)：?[_\* ]*$)', 0],
        ]
        end_index = 0
        flag = False
        for end in end_pattern:
            for index, item in enumerate(context):
                if re.search(end[0], item):
                    end_index = index + end[1]
                    flag = True
            if end_index > 0:
                patter = r'(^[#\*_\s]*([A-Z][a-zA-Z]+( [a-zA-Z]+){0,5})：?[_\*\s]*$)'
                if re.search(patter, context[end_index-1]):
                    end_index = end_index-1
                elif re.search(patter, context[end_index-2]):
                    end_index = end_index-2

                for i in range(0, end_index):
                    context[i] = "开头批量删除-1:<u>{}</u>".format(context[i])
                    # context[i] = ""
            if flag:
                break
        return context
```

2. 删除零碎简短段落，**103.**、_F1_ _F2_、**102.**、**2**、100等
```
    def move_short_duan(self,context):
        for i ,con in enumerate(context):
            # lower = False if re.search(r'[a-z]', con) else True
            # upper = True if len(re.findall(r'[A-Z]', con)) <= 3 else False
            count = True if len(re.findall(r'[A-Za-z]', con)) <= 3 else False
            if len(con) <= 15 and count:
                context[i] = "零碎段落删除-1:<u>{}</u>".format(context[i])
                # context[i] = ''
        return context
```

3. 人名占比超过40%的段落删除。
```
  def is_person_name_ratio_high(self, text):
        doc = nlp(text)
        total_characters = len(text)
        person_characters = sum(len(ent.text) for ent in doc.ents if ent.label_ == "PERSON")
        if total_characters == 0:  # 避免除以零的错误
            return False
        return (person_characters / total_characters) >= 0.4

  def move_duan(self,context):
        for i ,con in enumerate(context):
            # 人名段落删除
            if self.is_person_name_ratio_high(con):
                context[i] = "人名段删除-1:<u>{}</u>".format(context[i])
                continue
        return context
```

4. 页码段落删除时会漏删，补充连续判定，
```
 def is_page_number(self, con):

        if len(re.findall(r'([，；] ?\d+([\-，] ?\d+)*[A-Za-z])|([ _]\d+[_ ])', con)) > 25:
            return True

        if re.search(r'([^\d][，；\._]+ ?\d+[a-z]?[\d\-]*[a-z]?[\*_]*$)|(^[\*_]*[a-z\\\-A-Z ]+\d+[\*_]*$)|([a-zA-Z][，；\._] ?\d+[a-zA-Z]?([\-，] ?\d+[a-zA-Z]?)*[\*_ ]*$)|( \d+$)', con) and len(con) < 100:
            if re.search(r'(^[#\*\s_]*(CASE|[Cc]ase|[Cc]hapter|Question) \d+)', con):
                return False
            else:
                return True

        return False

 # 页码段落删除
        if self.is_page_number(con):
            page_count += 1
            context[i] = "页码段删除-1:<u>{}</u>".format(context[i])
            continue
        else:
            if page_count >= 3 and len(con) < 100:
                context[i] = "页码间删除-1:<u>{}</u>".format(context[i])
                page_count -= 2
                continue
            pass
```





