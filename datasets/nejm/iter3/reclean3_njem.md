reclean3_njem



针对页码数字和多余标点问题都是特殊格式，需要再写一条正则来对解决，预计这两个问题都能全部解决，但是分数上已经提升不大了

```
[r'([^\dm]+\s?)(<sup>(<a>)?[\d\s\-—,]{1,20}(</a>)?</sup>)',r'\1'],   # 特殊格式的数字引用删除
[r'<sup>(<a>)?[\s,]{1,5}(</a>)?</sup>',r''],
```

无关文本还有解决的空间

```
[r'^Download\s.*',r''], # 下载...
[r'^.{0,3}(Editor.s note|To learn more about).*',r'']  # 编辑信息 更多信息

带有括号的
Supplementary Appendix|For more   附加更多
```

整块开关条件增加

```
Historical Journal Articles Cited
```

