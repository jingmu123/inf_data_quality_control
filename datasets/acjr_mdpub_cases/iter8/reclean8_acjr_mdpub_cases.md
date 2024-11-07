## reclean7_acjr_mdpub_cases问题
### 多余换行：
1.上段小写结尾，下段逗号开头的多余换行。breast metastases（\n换行\n）， so there seems。
```
context = re.sub(r'([^|\n]{50,}[a-z\-\d，\=\&])(\n+\n *)([\.，,]|\\\[|\d+\.\d+ ?(\%|\)|mg\/|±)|\d+\)\.|\\\-)', r'\1 \3', context)
```

### 无关文本：
1.1.通用结尾删除遗漏，ending_starts里补充Statement of ethics、Funding statement、Disclaimer、Authors’information and contributions、Disclosures and freedom of investigation、Source of Fund、Data Availability Statement、Declaration of conflicting interests、Acknowledgement，Source(s) of Support None.等
```
[r'^[#\*]{0,4}\s?((Disclosure |Ethics )?Statement( of [Ee]thics)?|Funding ?(Sources|[Ss]tatement|and Disclosure|program)?|Disclaimer|Declarations?( of( competing| conflicting)? interest)?|Data Availability Statement|Source of (Support|Fund(ing)?)|Acknowledgement，Source\(s\) of Support None\.|Disclosures and freedom of investigation|Author[s\'’ ]*information and contribution
)s?[：\.]?[#\*]{0,4}\s{0,}($|\n)'],
```

2.References里提取出了通用结尾删除的文本，但未能提取出标题，导致通用结尾删除失效，造成标题下的无关文本。进行标题补充Disclosures，且优化以前的判断。将
```
if n_text in "Conclusions" or n_text in "CONCLUSIONS" or n_text in "Acknowledgments" or n_text in "Acknowledgements" or n_text in "Disclosures":
```
修改为：
```
patter = r'((Conclusion|CONCLUSION|Acknowledge?ment|Disclosure)[Ss]?)'
if re.search(patter, n_text):
```

2.1 move_ref_confusion提取出了参考文献内容，补充不符提取特征，114：p84.
```
(\d+(\(\w+\))?[:：； ]+pp?\d+\.)
```

3.补充删除括号内.org网址。(z-score.chboston.org)
```
[r'([（\(][^\)\(（）]*\.(com|org)[^\)\(（）]*[\)）])', r'删除24:<u>\1</u>'],
```

4.段落结尾，无关数字。presence of eosinophilia.26、clinically elevated.26、earlier investigations.|14.151等。
```
[r'([a-z]\.)( ?[\|\d]+([， \.\-\|]\d*)*$)', r'\1删除28:<u>\2</u>'],
```












