reclean3_uptodate_new_zh

reclean2标注结果分析
干净文本:38 脏文本:261
各纬度问题频次F={'缺少换行': 503, '多余换行': 3, '无关文本': 6, '语义不完整': 23, '完整性': 3, '缺少标点': 6, '多余标点': 10, '多余空格': 1, '标点错误': 1}
合格率=0.12709
质量分=46.6771
忽略 "缺少换行" 后质量分：94.84861
忽略 "多余换行" 后质量分：46.84193
忽略 "无关文本" 后质量分：46.94471
忽略 "语义不完整" 后质量分：48.59629
忽略 "完整性" 后质量分：46.96345
忽略 "缺少标点" 后质量分：46.7115
忽略 "多余标点" 后质量分：46.76881
忽略 "多余空格" 后质量分：46.6771
忽略 "标点错误" 后质量分：46.68593
{'缺少换行': 94.84861, '语义不完整': 48.59629, '完整性': 46.96345, '无关文本': 46.94471, '多余换行': 46.84193, '多余标点': 46.76881, '缺少标点': 46.7115, '标点错误': 46.68593, '多余空格': 46.6771}
忽略 "缺少换行#语义不完整" 后质量分：98.78604
忽略 "缺少换行#完整性" 后质量分：95.28403
忽略 "语义不完整#完整性" 后质量分：48.88264
{'缺少换行#语义不完整': 98.78604, '缺少换行#完整性': 95.28403, '语义不完整#完整性': 48.88264}

- 缺少换行问题还是出在step1，这里的step1确实能解决问题但是，还要进行倒叙匹配将step1改进成正则

```
def step1_drop_sentenc(self,content):
    pattern3=r'。?.*见.*详.*?[。]'
    pattern1=r'。?.*题专.*见.*?[。]'
    pattern2=r'。.*表附见.*?[。]'
    pattern4=r'。(图程流)?文(下|上)见.*?[。]'
    text=content.strip('\n').split("\n")
    for i in range(len(text)):
        text[i] = re.sub(pattern3, '。', text[i][::-1])[::-1]
        text[i]=re.sub(pattern1,'。',text[i][::-1])[::-1]
        text[i] = re.sub(pattern2, '。', text[i][::-1])[::-1]
        text[i] = re.sub(pattern4, '。', text[i][::-1])[::-1]
    text='\n'.join(text)
    return text
```

->

```
[r'[^。]*(详[^。]*见|见?[^。]*专题|见?附表|见(下|上)文(流程图)?|附图)[^。]*。',r''],
```



- 多余标点,出现了新的多余标点情况"。." 对处理多余标点的代码进行补充

- 语义不完整问题在原数据中基本都是没问题的，只是因为删除了几句话让剩下的内容看起来像是缺少了某些内容，删除的没问题
  有问题的是因为一条正则导致的，目前已经删掉，还有一些就是因为step1误删，目前改进过后该删的删干净了，不该删的还原回来了
  # ['\\((\\[?)\\s*#?((\\d+-\\s*\\d+-\\s*\\d+)|(\\d+-\\s*\\d+)|(\\d+(,|，)\\s*\\d+.*)|(\\d+))(\\]?).*?\\)', ''], #1.(23-1-32...) (12,dadada) ([12.医疗数据])

  例如：标注的  语义有效性#语义不完整#本文将宫颈先天性异常和良性病变的诊断和处理。

  良性宫颈病变和先天性宫颈异常\n\nAuthor:\n\nMarc R Laufer, MD\n\nSection Editor:\n\nRobert L Barbieri, MD\n\nDeputy Editor:\n\nAlana Chakrabarti, MD\n\n翻译:\n\n贺子秋, 副主任医师\n\nContributor Disclosures\n\n所有专题都会依据新发表的证据和 同行评议过程 而更新。\n\n文献评审有效期至： 2024-06.\n\n专题最后更新日期： 2023-06-01.\n\nThere is a newer version of this topic available in English .\n\n该专题有一个更新版本 英文版本 。\n\n引言 —\n\n妇科检查中常见良性宫颈异常。由于宫颈检查相对容易，医生可观察到卵巢激素分泌正常周期性变化带来的生理性改变，以及各种结构异常和病理情况，包括感染、良性肿瘤、癌前病变、恶性病变或先天性解剖异常。诊断和治疗良性宫颈异常可能需要结合肉眼观察、触诊、宫颈细胞学、HPV或其他感染的检测、放大镜(阴道镜)下检查或盆腔影像学检查。\n\n本文将总结宫颈先天性异常和良性病变的诊断和处理。处女膜、阴道和子宫的先天性异常详见其他专题。(参见 “阴道和处女膜先天异常” 和 “先天性子宫畸形的手术修复” )\n\n胚胎学、正常解剖学和组织学\n\n
  处理完之后->

  良性宫颈病变和先天性宫颈异常

  妇科检查中常见良性宫颈异常。由于宫颈检查相对容易，医生可观察到卵巢激素分泌正常周期性变化带来的生理性改变，以及各种结构异常和病理情况，包括感染、良性肿瘤、癌前病变、恶性病变或先天性解剖异常。诊断和治疗良性宫颈异常可能需要结合肉眼观察、触诊、宫颈细胞学、HPV或其他感染的检测、放大镜(阴道镜)下检查或盆腔影像学检查。
  本文将宫颈先天性异常和良性病变的诊断和处理。
  胚胎学、正常解剖学和组织学

- 