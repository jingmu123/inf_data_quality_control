msd英文第六次清洗

1. 开头标点问题，

   某些正则会残余标点，这中情况已经写正则去解决了

   ```
   r'\n\s{}([,\.])', r'\1\n'
   r'([,\.])(\s?[,\.]\s?){1,3}', r'\1'
   ```

   有些开头是括号在经过括号修正时把括号给变成了逗号，这种情况就要从括号的角度去考虑

2. 有一些因为小数导致在进行句号判断的时候把小数点当成句号 （√）

   例：serum urate > 6. 8 mg/dL ,> 0.  后面缺少具体数值

   在前面加上read more前面加上判断.前面是数字就再往前面找句号([^\.]*?\d+\.){0,2}

   ```
   [r'([^\.]*?\d+\.){0,2}[^\.]*([Ss]ee.{0,300})?(\.\.\.)? read more[^\.\(\)?!]*(\(.{0,350}?\)[^\.\(!?]{0,350}){0,5}[\.!?\)]{0,3}(\d+[^.?!]*.){0,2}',r'\n'],
   ```

3. 格式规范性#标点错误#1#1# (via questionnaire,  应该是）（√）

   ​	这个问题出在后面是General reference前面没有标点，对原有的正则进行一个优化，让他能在遇到逗号时就停止

   ```
   [r'(\d\.)?,?[^\.\,]*?[rR]eference(s)?(.{0,300}\d\d[/]?\d\d\)?\.[^\d]?){1,5}',r'\n'],
   ```

   ​	例：It includes Obtaining information about the child and parents (via questionnaire, interview, or evaluation) Working with parents to promote health (forming a therapeutic alliance) Teaching parents what to expect in their child’s development, how they can help enhance development (eg, by establishing a healthy lifestyle), and what the benefits of a healthy lifestyle are General reference 1. Frankenburg WK, Dodds JB, Archer P, et al: The Denver II: A major revision and restandardization of the Denver developmental screening test. Pediatrics 89(1):91–97, 1992. 

4. TooltipReadMore问题，原因是之前的规则把前面可能出现的common给删掉了

   ```
   [r'[^\n]*?TooltipReadMore[^\.]*\.',r'\n'],
   ```

5. Liver transplantation Liver Transplantation Liver transplantation is the surgical removal ......  Liver transplantation多次重复

   代码中已经有了去重的代码

   ```
   [r'\b([^\d]+)(\s+\1){1,2}\b',r'\1']
   ```

解决不了的问题

1. 存在多个标注“与上下文内容都不联接”，文本只能存在最多的问题就是read more(阅读更多)，折叠起来的内容前后容易造成内容不同。

2. “某一段不需要换行”换行都是因为删除了内容被替换成的换行

3. 多余标点#9#9#or hepatic vascular abnormalities.  Consequences.                原文是这样的

4. Doctors treat the cause of urgency. 感觉话没有说完后面缺少内容              这里是合理的，原文这里就是结尾后面没内容了

   原文：Doctors treat the cause of urgency. (See also Overview of Urinary Tract Symptoms Overview of Urinary Tract Symptoms Kidney and urinary tract disorders can involve one or both kidneys, one or both ureters, the bladder, or the urethra, and in men, the prostate, one or both testes, or the epididymis. Problems... Common.TooltipReadMore .) 

   
