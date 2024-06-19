本次解决的问题：
无关文本（均已处理），语义不完整问题已处理17%（由之前的正则引起的误删，以对pattern重新调整，具体如下）
1. 无意义文本： 
   例：↑ Jump up to: 1.0 1.1(√)
   ```
   [r'↑.*(\d|\.|})','']
   ```

2. 跟for more details有关的文本，把之前的正则进行完善 （√）
   例：For a more detailed description of some of these studies, please see NACI’s .
   ```
   'For.*details.*?\.'
   ```

3. 多余括号（√）
   例：(including dichotic listening))多余括号
   ```
   step3函数
   ```

4. 无关文本  be present.（√）
   此处因为之前写的正则存在误删情况，原文本是Signs consistent with acute abdomen may also be present.
   已将正则改为
   ```
   ((\.)?(.*?)(See|(see also)).*)
   ```
   
5. 含Page无关文本 （√）
   例：Please Take Over This Page and ......and or biographical sketch.
   ```
   r'(-\s*)?Please.*(Join|Page).*\.'
   ```

6. 处理语义不完整
   例：- There
   原文：Therefore, although some medical practitioners are open to cyberchondriacs' personal research, stating that this can open lines of communication between doctors and patients, there is concern by other doctors about misuse of the Internet by people who mistakenly believe that the information they find is sufficient to make a self-diagnosis.
   之前写的正则```r'(F|f)or.*information.*'```把There之后的内容删掉了，已将正则重新修改为
   ```r'\..*?additional information.*?\.'```

7. 处理语义不完整
   例：- tocilizumab every week with 26‑week prednisone taper (n=
   原文：tocilizumab every 2 weeks with 26‑week prednisone taper (n=50)\nplacebo with 26‑week prednisone taper (n=50)
   之前的正则```'(\(\s*\))|(\d+\s*\))'```将50）误删，已将正则重新修改为
   ```'\(\s*\d+\s*\)'```

8. 无关文本乱码
   例：nn:Pulmonalklaff.....
   ```r'\bnn\b:.*'```

9. 处理语义不完整
   例：pp. 202-26 (No 、(question 、once daily (N= .
   原文：pp. 202-26 (No. 318) 、(question 1)
   之前的正则```'(\(\s*\))|(\d+\s*\))'```将 318)、1)误删，已将正则重新修改为
   ```'\(\s*\d+\s*\)'```

10. 处理语义不完整
   例：While every ef
   原文：While every effort has been made to ensure the accuracy of the contents at the time of publication, neither the authors nor the Registered Nurses' Association of Ontario (RNAO) gives any guarantee as to the accuracy of the information contained in them or accepts any liability with respect to loss
   之前写的正则```r'(F|f)or.*information.*'```把There之后的内容删掉了，已将正则重新修改为
   ```r'\..*?additional information.*?\.'```

11. 换行问题
   例：Use adenosine, dipyridamole, or dobutamine as stress agents for MPS with SPECT and
      - adenosine or dipyridamole for first-pass contrast-enhanced MR perfusion.

12. 语义重复问题
   例：- Source: Data from the Bureau of Health Professions 
      - Source: Data from the Bureau of Health Professions. .

13. 多余标点
   例：- On gross pathology, ,  and  are characteristic findings

未解决问题：原文冒号后缺少内容导致的语义不完整问题
