reclean2_uptodate_new_zh
无关文本

```
# 对多标点进行替换
context = re.sub(r'[。，\s]{3,}',r'。',context)
context = re.sub(r'[,\.]{3,}',r'\.',context)
固定格式的无关文本删除
[r'^由 UpToDate 的医生.*',r''],
[r'^There is a newer version of this topic available in English.*',r''],
[r'^该专题有一个更新版本.*',r''],
[r'^请阅读本页末的.*',r''],
修改关于[\d]无关文本删除的长度20->100
[r'\\\[[\d\s\-,—\\]{0,100}\]',''],
整理关于（参见...）删除，允许括号里面可出现0-5次子括号
 [r'\(参见[^\(\)]*(\([^\(\)]*\)[^\(\)]*){0,5}\)', ''], #（参见...）  （参见（...）{0,5}）
修改两条正则，存在误删太多了
['[^。](见?)([^。]*)专题(.*)', ''],
['[^。](参见附图|详见).*', ''],
```

加入一个新的去除空格方法

```
def step4_rm_kongge(self, context):
    context = context.lstrip().rstrip()
    content = context.split(" ")
    first_content = content[0]
    last_content = " ".join(content[1:])
    final_content = re.sub(r'([\u4e00-\u9fa5]) {1,3}([\u4e00-\u9fa5])', r'\1\2', last_content)
    # 多执行一次，弥补正则边界重叠问题；
    final_content = re.sub(r'([\u4e00-\u9fa5]) {1,3}([\u4e00-\u9fa5])', r'\1\2', final_content)
    if len(final_content) == 0:
        return first_content

    merge_piece = first_content + final_content.lstrip()[0]

    split_word = list(jieba.cut(merge_piece, cut_all=False))
    if len(split_word[-1]) > 1:
        return first_content + final_content
    return first_content + " " + final_content
```

step1不知道这是干嘛的看不懂，会造成错误

```
def step1_drop_sentenc(self,content):
    pattern3=r'。?.*见.*详.*?[。，]'
    pattern1=r'。?.*题专.*见.*?[。，]'
    pattern2=r'。.*表附见.*?[。，]'
    pattern4=r'。(图程流)?文(下|上)见.*?[。，]'
    text=content.strip('\n').split("\n")
    for i in range(len(text)):
        text[i] = re.sub(pattern3, '。', text[i][::-1])[::-1]
        text[i]=re.sub(pattern1,'。',text[i][::-1])[::-1]
        text[i] = re.sub(pattern2, '。', text[i][::-1])[::-1]
        text[i] = re.sub(pattern4, '。', text[i][::-1])[::-1]
    text='\n'.join(text)
    return text
```