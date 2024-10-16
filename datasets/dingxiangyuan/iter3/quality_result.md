本次已解决的问题：

1. 文本中多余符号\、`、^(√)

   例：左布/比卡因是酰胺类局部麻醉药。局\`部麻醉药通过增加神经电刺^激的阈值、减慢神经刺激的传播和减少动作电位的升高率来阻滞神经刺激的产生和传导。通常，麻醉的进行与神经纤维的直径、髓鞘形成和传导速度有关。临... 登录

   ```
   # 匹配文本中多余符号\、`、^
   [r'\\|`|^',''],
   
   ```

2. 图片来源 （√）

   例：图片来源：visualdx

   ```
   ['图片来源：.*','']
   ```

3. 特殊符号：<br/><br/>（√）

4. 参考引用 （√）

   例：<sup>[1]</sup>

   ```
   ['(<sup>)?(\\\\)?(\\[|［)(\\d+|(\\d+[,.、~～-]\\s*\\d+.*))(\\\\)?(\\]|］)(</sup>)?','']
   ```

5. 相关日期（√）

   例：【 核准日期 】
       2008-07-23
      【 修改日期 】
       2008-07-23

   ```
   ['【.*日期.*】','']
   ```
6. 无关日期（√）
   
   例：2001-12-22

   ```
   [r'\d{4}-\d{2}-\d{2}','']
   ```

7. 图引用 （√）

   例：图 2：医疗器械）

   ```
   [r'（?图\s*\d+:.*?）?','']
   ```

8. 过滤掉 ...登录所在的句子： （√）
   （只过滤掉 “静脉注射... 登录。”，其他的内容不动 ）
   例：全身给药: 皮下注射: 重组人白介素-2（125 Ala）60－100 万 IU/m2 ，皮下注射 3 次/周，6 周为一疗程。静脉注射... 登录
   
   ```
   见代码所写函数step1_drop_login
   ```
   
9. 去除行前多余空格 （√）
    例：      **辅料为：** 依地酸二钠、磷酸二氢钠、磷酸氢二钠、注射用水。
    ```
    见代码所写函数step2_strip
    ```
##  new_wrong:
### 可以处理
      多余标的#20#20#^ 多余标点#22#22#^  （√）
      ['格式规范性#缺少标点#9#9#体重天中间缺了/']    （√）
      ['语义有效性#语义不完整#10#10#WHO 建议，应尽可能多地在伤口部位注射，如果没有足够量的本品。结尾缺少内容'] （√）
      ['文本干净度#无关文本#35#40#内容与正文无关']  （√）
      ['文本干净度#无关文本#16#16#具体如图']   （√）
      】 宝宝正常的睡眠时间见下图： （√） 【8】 数据来源：  （√）
      【 药品图片 】   （√）
      (参见“禁忌”)   （√）
      本固定的复方制剂不适用于高血压的初始治疗(详见“用法用量”)。  （√）

      况<tableclass=\"dmp_table_border\"><tbody><tr><tdrowspan=\"2\">异常值</td><tdcolspan=\"2\">ALT升高病例数观察病例数<sup>*</sup></td></tr><tr><td>拉米夫定</td><td>安慰剂</td></tr><tr><td>ALT≥2倍基线值</td><td>37/137(27%)</td><td>22/116(19%)</td></tr><tr><td>ALT≥3倍基线值<sup>＃</sup></td><td>29/137(21%)</td><td>9/116(8%)</td></tr><tr><td>ALT≥2倍基线值和ALT绝对值＞500IU/L</td><td>21/137(15%)</td><td>8/116(7%)</td></tr><tr><td>ALT≥2倍基线值；胆红素＞2倍ULN和≥2倍基线值</td><td>1/137(0.7%)</td><td>1/116(0.9%)</td></tr></tbody></table><sup>*</sup>  （√）

### 正常文本
      \n*   禁忌证\n 为非错误文本
      ['格式规范性#缺少换行#6#6# 化学结构式： 分子式。应与前文分开']
### 不能处理 (原文错误)
    【6】 每粒含 【7】 葡萄糖酸锌 158.5 mg (含元素锌：22.74 mg)


##  new_wrong:
### 可以处理且已处理
    1.缺少括号:（约为临床剂量的 500 倍胜用本品后
    2.如下表：具体的第一针接种后安全性结果如下表 1、2 所示.免疫原性结果如下表 3 所示
    3.多余标点：且无/可靠参考文献(多余/）
    4.多余空格：恶性肿瘤并发的 高钙血症 和溶骨性癌转移引起的骨痛。
    5.多余标点：治-疗低糖血症（多了-）
### 不能处理（原文错误）
    1.语义有效性#语义不完整#70#70#生活
    2.语义有效性#无意义文本#57#60#与上文无衔接
    【56】*   有助于降低血糖的糖尿病药物
    【57】Gerald W Smetana, MD. Evaluation of the patient with night sweats or generalized hyperhidrosis.
    【58】Hung K So1, Albert M Li1, Chun T Au1, etc. Night sweats in children: prevalence and associated factors.
    3.语法规范性#错别字#29#29#文身  应是纹身
