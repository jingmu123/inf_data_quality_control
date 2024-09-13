## reclean2_accr和ccri问题
### 多余换行：
1.段内插入表格内容导致多余换行，针对性移动拼接，并去除换行。
```
context = re.sub(r'([a-z])(\n\nTable [\W\w]*?)(\n\n)([a-z].*)', r'\1删除段之间换行\4\2', context)
```
发现多段需要拼接的，后续优化：
```
context = re.sub(r'([a-z，\d])(\n\nTable [\W\w]*?)(\n\n)(([a-z]|\(\d+%\)).*)', r'\1删除段之间换行\4\2', context)
```

### 错误删除：
1.delete_page_middle文章部分段落删除误删带序号的段落，补充更改。
```
start_to_end = [
    [r'(^[\\ #]*(OPEN ACCESS)[\\ #]*$)', r'(^[\\ #]*([A-Z][a-z]+( [A-Z][a-z]+)?)[\\ #]*$)|(.{250,})', 0],
    [r'(^[\\ #]*(Correspondence：|Citation：))', r'(^[\\ #]*([A-Z][a-z]+( [A-Z][a-z]+)?)[\\ #]*$)|(.{250,}|(^\d{1,2}\\?\.))', 0],
]
```

2.句子结尾数字误删，误删比较多，将删除4去掉。

3.(p=0.002， Rolland Morris questionnaire； Table 2)、(p<0.001， Table 2)、(p<0.001， Figure 1)、(p=0.041， Table 3)误删。
给通用删除括号内部分内容加入中文逗号和分号。
```
[r'(\(\s?[^\(\)]*)([\.;；，]\s([Ff]igs?(ure)?|F\s?IGS?(URE)?|Table|[sS]ee|For more|http|www)s?[\s\.:][^\(\)]*)(\))', r'\1)'], 
```

**0912补充**：
### 多余换行：
1.表格插入导致的多余换行补充Baseline difference inter-group： $$$ p<0.001删除段之间换行±18.9 mm (p<0.001)。
```
def move_duan(self,context):
    context = re.sub(r'([a-z，\d])(\n\nTable [\W\w]*?)(\n\n)(([a-z]|\(\d+%\)).*)', r'\1删除段之间换行\4\2', context)
    context = re.sub(r'([\d])(\n\nTable [\W\w]*?)(\n\n)((±\d).*)', r'\1删除段之间换行\4\2', context)
    return context
```
优化补充没有Table表例的表格插入导致的多余换行，补充 | 标识确认是表格
```
context = re.sub(r'([a-z，\d])(\n\n(Table|\|) [\W\w]*?)(\n\n)(([a-z\(]).*)', r'\1删除段之间换行\5\2', context)
context = re.sub(r'([\d])(\n\n(Table|\|) [\W\w]*?)(\n\n)((±\d).*)', r'\1删除段之间换行\5\2', context)
```

2.(95% CI： 20.2-41.8\n\nmonths)， 33.9% (37/109)、patient developed LMC after 2\n\nyears. 、on T1-\n\nweighted等。
```
context = re.sub(r'([a-z，\-\d])(\n\n)([a-z])',  r'\1删除换行\3', context)
```

### 无关文本：
1.\[10-171、\[24，251、3，11，13，16，28-30\]等。
将通用正则修改补充：
```
[r'(((\\)?\[[\d\s,，\–\-—]{1,}(\\)?\]?)|((\\)?\[?[\d\s,，\–\-—]{1,}(\\)?\]))', r'通用删除6(英):<u>\1</u>'], # 带有方括号的数字引用
```

2.文本中出现的中文加一个空格删除。
```
context = re.sub(r'([\u4e00-\u9fff]+ )', r'删除8:<u>\1</u>', context)
```

3.补充E-mail：在段内的情况。
```
[r'(.*((Received|Accepted|Published) Date：|E-mail：).*)', r'删除7:<u>\1</u>'],
```

4.无关文本删除，is properly cited.、ISSN： 2474-1655、cited.、4：1685.、C d、Hz).等。
```
[r'(^(ISSN：).*)', r'删除9:<u>\1</u>'],
[r'(^(is properly cited|cited|\d+：\d+|\w ?\w\))[\.\s]*$)', r'删除10:<u>\1</u>'],
```

5.文末引用其他格式补充删除，1.Noone AM， HowladerN，Krapcho M， Miller D， Brest A， Yu M， et al. SEER Cancer Statistics Review， 1975-2015.Bethesda： National Cancer Institute；2018.。
```
[r'(^\d+\\?\..*\d{4}[;；\.]\w+(\(\d+\))?[:：]?[\w\-]+.*)', r'删除6:<u>\1</u>'],
```

6.无关段落至文末补充，Disclosure、Declarations、Permission。
```
[r'^[ #]*(Reference|Ethics Approval|Authors?\'? ?Contribution|Acknowledge?m ?ent|Funding|Funding Sources|Research Funding|Pseudomembranous Tracheobronchitis|Disclosure|Declaration|Permission)s?[ #]*($|\n)'],
```

7.通用括号删除补充，Panel、Video。
```
[r'(\(\s?([Pp]anel|[Vv]ideo|[Ff]igs?(ure)?|F\s?IGS?(URE)?|Table|[Ss]ee|For more|panel|http|www|NCT\d+|NO\.|version|p\.)s?[\s\.:]?[^\(\)]*\))', r''],
```

**0913补充：**
### 多余换行：
1.补充PolyPhen2 ， PROVEAN (http：//provean.jcvi. \n\n org/index.php)， and Mutation Assessor 等情况。
```
context = re.sub(r'([^|\n]{100,})(\n\n)( *[a-z])', r'\1删除2换行\3', context)
```

### 无关文本：
1.Canada：A Case Report. Ann Clin Case Rep. 2021；6：2073. ISSN： 2474-1655补充删除句中ISSN。
```
[r'(\.)([\d；：\. ]*(ISSN：).*)',  r'\1删除11:<u>\2</u>'],
```

2.结尾删除优化，补充Institutional Review Board Statement，将单独的序号参考文献加入。
```
ending_starts = [
    [r'^[ #]*(Reference|Ethics Approval|Author[s\' ]*Contribution|Acknowledge?m ?ent|Funding|Funding Sources|Research Funding|Pseudomembranous Tracheobronchitis|Disclosure|Declaration|Permission|Institutional Review Board Statement)s?[ #]*($|\n)'],
    # [r'(^1\\\. )']
    [r'(^1\\?\..*\d{4}[;；：\.]\w+(\(\d+\))?[:：；]?[\w\-]+.*)']
]
```

3.We thank the Bob & Renee Parsons Foundation删除。
```
[r'(^We thank .*)', r'删除12:<u>\1</u>'],
```

4.通用文章中间某一部分段落的删除，补充若没有匹配到结尾，则一直删除到文末，补充到delete_page_ending2。
```
ending_starts = [
    [r'(^[\\ #]*(OPEN ACCESS)[\\ #]*$)'],
    [r'(^[\\ #]*(Correspondence：|Citation：))']
]
```

5.通用删除从文章开头到某一段，补充删除Clinical Image、Clinical Video及前面内容，并调整顺序。
```
end_pattern = [
    [r'(^[ #]*(Abstract)[ #]*(\n|$))', 0],
    [r'(^[ #]*(Background|Introduction)[ #]*(\n|$))', 0],
    [r'(^[ #]*(Clinical ?Image|Clinical ?Video|ClinicalPresentation)[ #]*(\n|$))', 0],
]
```
```
[r'(^(Clinical ?Image|Clinical ?Video)$)', r'删除14:<u>\1</u>'],
```

6.补充删除work is properly、is properly cited段落。
```
[r'(.*(work is properly|is properly cited).*)', r'删除13:<u>\1</u>'],
```



