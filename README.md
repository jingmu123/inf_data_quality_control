### A. 清洗每轮迭代流程说明

###### 1. 根据（上一轮）标注结果，进行问题分析；一方面参照quality_tools/step2_get_label_result.py;另一方面需要对问题进行归类分析，要求具体的case，不能泛泛的说无关文本占比很高；

###### 2.根据分析结果，形成quality_result.md

###### 3.根据分析结果，进行清洗；清洗要求见 2. 清洗代码规范；

###### 4.清洗完成后，需要再次自检，避免错误解决的不干净，以及误修问题；

###### 5.清洗完成后，自检（quality_result.md）,clean.py or clean.ipynb, sample/reclean?_xxxx_en/zh_label.jsonl三个文件是否存在；并且排出掉其他中间文件；

###### 6.确认无误后，push到github;(还是建议大家建立个人仓库，push上去检查没问题之后，在merge到dev仓库)

## B. 清洗代码规范

###### 1. 写正则的过程中，请保证泛化性；不仅局限于某一个case，而是窥一求万，尽量保证对其他标注的case，以及看不到的同类型的case也覆盖到；最不好的就是，同一类问题，每个case都写一条规则；

###### 2. 写正则的过程中，保证1个规则解决一个问题；应尽量保证这一要求。若不能，则需要将统一功能型的规则，打包到一起；

###### 3. 每条正则写完，都要单独对样本进行匹配测试，避免误删；

###### 4. 要把每条（每套）正则做成插件式工具；函数运行中，要保证不同的规则顺序可调；不允许不同的规则互相牵制，由于顺序不一样，就产生不一样的结果。要求2中，同一功能块的规则，视为一条规则；

###### 5. 后续工作中，每条正则必须加一解释；解释包括：改正则解决的问题描述，要求面向开发者，可以读懂即可，但不允许太空；

###### 6. 如果某条规则无法泛化，请将其单独形成函数处理，不要放入正则库；


## C. 后处理代码

### 1. 清洗完成后，执行如下代码去掉首尾空置

```
context.strip(" ").strip("\n").strip(" ").strip("\n")
```

### 若文本确认为markdown，执行如下后处理代码：
```
def post_process(context):
    context = context.strip(" ").strip("\n").strip(" ").strip("\n")
    # 消除分界符失效  --*- 前面需要有连续两个\n;
    context = re.sub('\n    --', "\n\n    --", context)
    # 消除空格问题
    context = re.sub(r'\n +\n', "\n\n", context)
    context = re.sub(r'\n +\n', "\n\n", context)
    # 去掉过多\n的情况
    context = re.sub("\n{2,}", "\n\n", context)
    return context
```

## D.清洗框架
清洗代码模板请参考：
     - https://github.com/11983h/data_quality_control/blob/dev/datasets/atemplete/iter0/clean_template.py

对于正则，有如下要求：以列表形式，分别为替换src文本以及target文本
```
pattern_list = [
    [r'xxx',"yyy"],
]
```
清洗过程中，请固定如下基本框架，实现clean_text函数即可：
```
def clean_text(context, lang):
    #todo
    # ...
    for pattern_item in pattern_list:
        item = re.sub(pattern_item[0], pattern_item[1], item)
    # ...
    return context

def post_process(context):
    context = context.strip(" ").strip("\n").strip(" ").strip("\n")
    # 消除分界符失效  --*- 前面需要有连续两个\n;
    context = re.sub('\n    --', "\n\n    --", context)
    # 消除空格问题
    context = re.sub(r'\n +\n', "\n\n", context)
    context = re.sub(r'\n +\n', "\n\n", context)
    # 去掉过多\n的情况
    context = re.sub("\n{2,}", "\n\n", context)
    return context

fw = open("", "w", encoding="utf-8")
with open("", "r", encoding="utf-8") as fs:
    for items in tqdm(fs.readlines()):
        item = json.loads(items.strip())
        context = item["text"]
        # if need
        lang = item["lang"]
        context = clean_text(context, lang)
        context = post_process(context)
        item["text"] = context
        item = json.dumps(item, ensure_ascii=False)
        fw.write(item + "\n")
```
如果数据集涉及到中、英语种区分清洗，可以直接通过如下代码获取，并注意分别处理的实现应该放在clean()函数：
```lang=item["lang"]```
