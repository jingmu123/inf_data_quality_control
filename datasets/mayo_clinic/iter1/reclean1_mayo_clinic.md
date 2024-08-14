reclean1_mayo_clinic

目前标注分数为5.95925，因为文件是第一次清洗，基本全是无关文本问题，预计能解决70%到80%左右的无关文本

提升到80分左右，会有新的错误误删的存在

无关文本

无关文本大概分为三种

1.文章末端关于...咨询电话   或  付费阅读文章的描述

```
【64】Call your doctor for medical advice about side effects. You may report side effects to the FDA at 1-800-FDA-1088.

【65】Portions of this document last updated: Aug. 01, 2023

【66】Original article: https://www.mayoclinic.org/drugs-supplements/pimavanserin-oral-route/description/drg-20311664
```

```
【1】To read this article in full you will need to make a payment

【2】### Purchase one-time access:

【3】Academic & Personal: 24 hour online access Corporate R&D Professionals: 24 hour online access

【4】One-time access price info

【5】*   For academic or personal research use, select ‘Academic and Personal’

For corporate R&D use, select ‘Corporate R&D Professionals’
【6】### Subscribe:

【7】Subscribe to Mayo Clinic Proceedings

【8】Already a print subscriber? Claim online access

【9】Already an online subscriber? Sign in

【10】Register: Create an account

【11】Institutional Access: Sign in to ScienceDirect

【12】Article info
【13】### Identification

【14】DOI: https://doi.org/10.1016/j.mayocp.2022.10.023

【15】### Copyright

【16】### ScienceDirect

【17】Access this article on ScienceDirect

【18】Related Articles
【19】Hide Caption Download See figure in Article

【20】Toggle Thumbstrip

【21】*   Download Hi-res image

Download .PPT
```

解决方法设置开关

对后面匹配到(To read this article in full you will need to make a payment|Call your doctor)开始对后面进行删除

2.对于整页价值密度低，可整页都不要

3.整页价值密度低但是需要保留部分内容

方法2：根据一些无关行的特征去删除无关行

```
def step2_wuguanpage(self, context):
    new_context = []
    line_num = 0    # 定义一个变量记录行数
    wuguanline_num = 0   # 定义一个变量记录无关行数
    select = False   # 定义一个开关寻找本页是否有选择题的存在
    for item in context:
        if item.strip():
            line_num += 1
        if len(re.findall("[\da-z]\.\n", item.strip())) >= 4:   # 判断业内是否有选择题的存在   如果有打开开关
            select = True
        if re.search('[\.\s][A-Z]\.\n',item) or re.search('\d+-\d+$',item.strip()) or re.search(r'\*\s+Google',item):   # 匹配到无关行的特征打标签
            wuguanline_num += 1
            item = "无关删除-2" + item

        new_context.append(item)
    print(len(new_context))
    print(line_num)
    print(wuguanline_num)

    return new_context
```

正则
[r'(^By Mayo.*)',r'删除1:<u>\1</u>'],   # 作者信息