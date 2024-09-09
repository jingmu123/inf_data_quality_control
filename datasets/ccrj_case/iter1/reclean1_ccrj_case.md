## reclean0_ccrj_case问题
### 无关文本：
1.Abstract、Clinical Image Description以上无关段落。
```
end_pattern = [
            [r'(^[#\s]*(Abstract|Clinical Image Description)\s*(\n|$))', 0],
            ]
```

2.Conflict of Interest、Declarations、Important Points及以下无关段落补充删除。
```
[r'^[#\*]{0,4}\s?(Reference|Funding and Disclosures|Polls on Public|Conflict of Interest|Declaration|Important Point)s?[#\*]{0,4}\s{0,}($|\n)'],
```
