## reclean4_aiaiyi_zhenliaozhinan_en
### 标点错误：
无关文本：
1.无关特殊文本补充。
```
[r'((ó 2011 European|Perth:|Date written:|Final submission:|Author:|Stack A|For more detailed|Footnote:|See the NICE|Entries to MEDLINE|From the National|CREST wishes|Dr Mark Gibson|Experts of the guideline|Copies of the full-text|therecent American)[^\n]+)', r'删除15:<u>\1</u>'],
[r'(,)(\s{3,})', r'\.\2'],
[r'(\s{4,})(\d+(([\s，,\-–]+\d+){0,20}) *)([A-Zabeih][A-Za-z])', r'\1删除6:<u>\2</u>\5'],
[r'((\\\*Refer to|Review by date|\*+Disclaimer|\*+《2013AHA ACC成人超重与肥胖管理指南》内容预览)[\w\W]*)', r'删除16:<u>\1</u>'],
```

**0821补充：**
1.无关特殊文本补充。
```
[r'(The 2002 American[^\.]+\.)', ''],
[r'fashion3through', 'fashion through'],
[r'rare6,7and', 'rare and'],
[r'2005.2,3The', '2005. The'],
[r'statin2,3,9 -13and', 'statin and'],
[r'preexcitation.3', 'preexcitation.'],
[r'concentration74-76andthere', 'concentration and there'],
[r'((ó 2011 European|Perth:|Date written:|Final submission:|Author:|Stack A|For more detailed|Footnote:|See the NICE|Entries to MEDLINE|From the National|CREST wishes|Dr Mark Gibson|Experts of the guideline|Copies of the full-text|therecent American|see NEJM|Advice on|A recent document)[^\n]+)', r'删除15:<u>\1</u>'],
```
2.无关页面删除。
```
exit_flag = False
wuguan = ["目录：","自然人群中幽门螺杆菌感染特点：","The  American Heart Association","Hisamichi AIZAWA","《2010RNAO慢性疾病支持性自我管理策略》","2013 AHA/ACC/TOS Guideline"]
for txt in wuguan:
    if txt in context:
        # context = "(本页删除)本页文本质量太差:\n" + context
        exit_flag = True
        break
if exit_flag:
    continue
```

**reclean3_aiaiyi_zhenliaozhinan_en**剩余无关问题基本解决，删除标签清洗封版。
