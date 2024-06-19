第七次清洗

1. Set the machine to 2-D mode or B mode and  后面缺少内容      误删（√）

   原因是，下面的代码是为了清洗一些无关应用的但是ready前面的.使用来匹配空格或点，但是误删的文本也是ready开始，console结尾，所以在ready前面加上转意

   ```
   (\$\(document\))?.ready.*?console    -->   (\$\(document\))?\.\s?ready.*?console
   ```

2. †符号（√）

   ```
   [r'†\s?', '']
   ```

3. 格式规范性#多余标点#0#0#effects.  : Garlic（√）

   这里是少删了修改了正则解决了

4. ['语义有效性#语义不完整#4#4# 4 Any physical activity Sometimes occurring at rest']（√）

   原文是： Table Canadian Cardiovascular Society Classification System for Angina Pectoris Class Activities Triggering Chest Pain 1 Strenuous, rapid, or prolonged exertion Not usual physical activities (eg, walking, climbing stairs) 2 Walking rapidly Walking uphill Climbing stairs rapidly Walking or climbing stairs after meals Cold Wind Emotional stress 3 Walking, even 1 or 2 blocks at usual pace and on level ground Climbing stairs, even 1 flight 4 Any physical activity Sometimes occurring at rest Adapted from Braunwald E, Antman EM, Beasley JW, et al: ACC/AHA Guidelines for the management of patients with unstable angina and non-ST segment elevation myocardial infarction: A report of the American College of Cardiology/American Heart Association Task Force on Practice Guidelines (Committee on the management of patients with unstable angina). Circulation 102(10):1193–209, 2000. doi: 10.1161/01.cir.102.10.1193. 

   之前是删除了Adapted from以及后面的内容，整句都是应该删的现在加上了前面的条件将前面的也删除了

5. ['语义有效性#语义不完整#5#5#Set the machine to 2-D mode or B mode and  后面缺少内容']

   这个是误删了，已经修复（√）

6. ['文本干净度#无关文本#2#2#2.  Häuser W, Brähler E, Ablin J, Wolfe F: Modified 2016 American College of ......Arthritis Care & Research 73 : 617–625, 2021.  无关引用']  已经删除（√）

7. ['文本干净度#无关文本#4#4# Accessed 3/7/22.  ']  已经删除（√）

