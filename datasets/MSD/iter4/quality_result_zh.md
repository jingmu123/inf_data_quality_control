本次的中文问题：

#### 标点问题，集中在括号不匹配上，对匹配不到的括号用逗号代替（√）

1. 缺少右括号
2. 标点错误
3. 多于标点

#### 无关文本

1. 语义上的无关(需要考虑语义)

2. 一些文本上的错误

   文本干净度#无关文本#0#0#nie’gu非专业术语

   文本干净度#无关文本#0#0#（1）（√只将标点符号前的序号删除，例，孕产妇总死亡率在美国是 23.8 死亡/100,000 活产（ 1）。）

   文本干净度#无关文本#0#0#=“”=""   （√）

   文本干净度#无关文本#0#0#<2>（√）

#### 语义问题，语义问题需要参考语义



#### 另见问题的完善

```
    [r'（另见([^（）阅]*?（[^(阅读更多)]{1,50}）[^（）]*?){0,6}.*?(阅读更多|）)[\s。）]{0,3}','\n'],
    # 剩下的另见两百个左右，从另见前面的句号到后面的句号
    [r'[—]{0,2}[^。——]*?另见[^。]*[\s。）]{0,3}','\n'],
```



#### '。的'问题（√）

1. 删除残留
2. 原数据存在

```
[r'。的[^。]*','\n'],  对。的请款删除到后面的句号
```



#### 中文中的英文问题（√，英文这个情况很多，有点复杂，可能解决的不彻底，还需要看标注情况）

之前是对中文中的英文全部删除，太过绝对，导致有些应该存在的英文也全部删除

例：通常只在给予 肾衰竭 肾衰竭概述 本章包括关于 新型冠状病毒肺炎 (COVID-19) 和急性肾损伤 (AKI) 的新章节      这些不该被删掉

例：花斑癣的表现 花斑癣 在这张照片中，花斑癣表现在躯干多发低色素鳞屑性斑片。 图片由医学博士Thomas Habif提供。 花斑糠疹伴随棕色斑片 可见边界清楚的棕色斑片，伴发两处偶发的血管瘤。 © Springer Science+Business Media 花斑糠疹伴随颈部多发棕色斑片 © Springer Science+Business Media 背部有色素减退斑块的花斑癣 图像由Karen McKoy, MD提供。 面部和颈部出现色素减退斑疹和斑块的花斑癣 图像由Karen McKoy, MD提供。    

 治疗参考文献 1.Stamp LK, Frampton C, Morillon MB, et al: Association between serum urate and flares in people with gout and evidence for surrogate status: a secondary analysis of two randomised controlled trials.Lancet Rheumatol 4: e53-e60, 2022.doi.org/10.1016/S2665-9913(21)00319-2 2.Jutkowitz E, Dubreuil M, Lu N, et al: The cost-effectiveness of HLA-B*5801 screening to guide initial urate-lowering therapy for gout in the United States.Semin Arth Rheum 46:594-600, 2017.doi: 10.1016/j.semarthrit.2016.10.009 3.O'Dell JR, Brophy MT, Pillinger MH, et al: Comparative effectiveness of allopurinol and febuxostat in gout management.NEJM Evid 1(3):10.1056/evidoa2100028, 2022.doi: 10.1056/evidoa2100028.Epub 2022 Feb 3.PMID: 35434725; PMCID: PMC9012032. 4.White WR, Saag KG, Becker MA, et al: Cardiovascular safety of febuxostat or allopurinol in patients with gout.N Engl J Med 378:1200-1210, 2018.doi: 10.1056/NEJMoa1710895 5.Mackenzie IS, Ford I, Nuki G, et al: Long-term cardiovascular safety of febuxostat compared with allopurinol in patients with gout (FAST): a multicentre, prospective, randomised, open-label, non-inferiority trial.Lancet 396(10264):1745-1757, 2020.doi: 10.1016/S0140-6736(20)32234-0 关键点 

这两种情况就应该被删除

```
    ['[^。\u4e00-\u9fa5]{100,}',''],   对过长的英文句子删除，过长的英文句子一般都是英文参考文献
    ['[^\u4e00-\u9fa5]*©.[^。]*。',''],  对英文中带有©符号的进行删除，一般也是参考文献
```



#### 重复文本（对）

例：脊柱外伤 脊柱外伤 脊柱外伤可引起脊髓或椎骨损伤 ==> 脊柱外伤可引起脊髓或椎骨损伤



