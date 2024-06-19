msd英文第五次清洗

see [Ff]igure问题（√）

```
['\(?[^\.\(]*see [Ff]igure[^\.\)]*.','']
```

相关参考文献 （√）

```
([aA]dapted from[^\.]{0,100}\.\s)?(Treatment references)?[^\d]\d\.\s+[^\d].{0,300}, \d{4}\.
```

会有一个误判，多删一部分

0. LR+ = likelihood ratio for a positive result; LR- = LR for a negative result.  Adapted from Fagan TJ.  Letter: Nomogram for Bayes theorem.  New England Journal of Medicine 293:257, 1975.多删了0.  LR+ = likelihood ratio for a positive result; LR- = LR for a negative result.

Adapted from改编自（√）

```
[r'\(Adapted from[^\(]{0,200}(\([^\)]{0,200}\)[^\(]{0,200}){0,3}\)',r'\n'],有括号的情况

[r'(,)?(\s+Diagnosis reference 1.\s+)?Adapted from [^\.\n]*\.(.{0,300},\s?\d{4}\.)?(\s+Copyright 1992, American Medical Association.\s+)?',r'\n'],无括号情况
```

Erratum in勘误（个例）（√）

```
Erratum in[^\.]*[\.]
```

PMID电话号（前面清洗的残余）（√）

Also see Approach to the Patient With a Suspected Inherited Disorder of Metabolism Approach to the Patient With a Suspected Inherited Disorder of Metabolism 无关引用

无标点只能针对这句话写正则删除

原文：. Also see Approach to the Patient With a Suspected Inherited Disorder of Metabolism Approach to the Patient With a Suspected Inherited Disorder of Metabolism Most inherited disorders of metabolism (inborn errors of metabolism) are rare, and therefore their diagnosis requires a high index of suspicion.

括号里面加数字，无关文本#6#6# ( 1)(√)

```
\(\s?\d?\s?\)
```

Bender, MSPT, ATC, CSCS; and Whitney Gnewikow, DPT, ATC.与上文内容无联接（√）

这句是一个正文中穿插的一个引用，没什么特征只能针对性删除

例：5. Add light weight as tolerated. Courtesy of Tomah Memorial Hospital, Department of Physical Therapy, Tomah, WI; Elizabeth C.K. Bender, MSPT, ATC, CSCS; and Whitney Gnewikow, DPT, ATC. Side-Lying Shoulder External Rotation 1. Lie on uninvolved side with pillow between arm and body of the involved side. 

```
[r'Courtesy of Tomah Memorial Hospital, Department of Physical Therapy, Tomah, WI; Elizabeth C.K. Bender, MSPT, ATC, CSCS; and Whitney Gnewikow, DPT, ATC.',''],
```

Also see无关引用（√）

```
\(?[^\(\.]*Also see[^\(\.]*(\([^\)]*\)[^\.]*){0,3}[\.\s\)]{0,3}
```

For detailed了解详情（√）

```
[^\.]*For detailed[^\.]*.
```

et al 等问题（√）

```
[2.et](http://2.et) al 等问题
```

前面的删除留下了半句，将后半句删掉（√）

例：\n may be generalized, usually due to a pituitary tumor, or is idiopathic or may involve the selective loss of one or a few pituitary hormones. 

单词重复问题（√）

```
[r'\b([^\d]+)(\s+\1){1,2}\b',r'\1'],
```

COVID-19 COVID-19 COVID-19这个问题，去重的正则抓不到这个case很奇怪，单独对这个情况进行修改（√）

解决不了的问题

部分重复问题

例：['文本干净度#无关文本#1#1#Overview of Vasculitis is inflammation of blood vessels与前面重复的文本'] 

原文：Blood vessel inflammation in general is called vasculitis **Overview of Vasculitis Vasculitis is inflammation of blood vessels.** Vasculitis can affect any size or type of blood vessel It may affect many blood vessels in many organs or just a few vessels in 1 or 2 organs The... read more . What is giant cell arteritis? Giant cell arteritis is a type of vasculitis **Overview of Vasculitis Vasculitis is inflammation of blood vessels.**这只是句子中的后半句重复，设置的相似度是0.9



