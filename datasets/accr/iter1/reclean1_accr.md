## reclean0_accr问题
### 无关文本：
1.Abstract、Background以上无关段落。
```
end_pattern = [
    [r'(^[\*\s]*(Abstract|Background)[\*\s]*(\n|$))', 0],
]
```

2.Correspondence：、OPEN ACCESS、E-mail：、Copyright等无关段落删除。
```
[r'(^[\*_\\]*(Correspondence：|OPEN ACCESS|E-mail：|Copyright).*)', r'删除1:<u>\1</u>'],
```

3.补充无关段落至文末，**Ethics Approval**、**Authors' Contribution**、**Acknowledgement**、**Funding**
```
[r'^[#\*]{0,4}\s?(Reference|Funding and Disclosures|Polls on Public|Ethics Approval|Authors?\'? Contribution|Acknowledgement|Funding)s?[#\*]{0,4}\s{0,}($|\n)'],
```


4.5\]、\[6等缺少一边括号的情况。
```
[r'((\\)?\[[\d\s,，\-\–—]{1,}(\\)?\]?)|((\\)?\[?[\d\s,，\-\–—]{1,}(\\)?\])', r'通用删除6(英):<u>\1</u>'],  # 带有方括号的数字引用
```

5.单独一段人名，**_Kyaw AMM， Min Oo SZ， Maung W， Aye_**。
```
[r'(^[\*_\\]*(([A-Z][a-z]+( \w+){0,2})[,，] ?){2,}([A-Z][a-z]+( \w+){0,2})[\*_\\]*.*)', r'删除3:<u>\1</u>'],
```

