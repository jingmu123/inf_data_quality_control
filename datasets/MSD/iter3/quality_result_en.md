msd英文问题

#### 无关文本

1. 文本重复(问题多)添加一个算法，用句号分割判断句子是否相同

   ```
   def remove_duplicates(text):
       # 分割文本成句子
       sentences = text.split(". ")
       # 识别和删除重复句子
       unique_sentences = []
       seen_sentences = set()
       for sentence in sentences:
           if sentence not in seen_sentences:
               unique_sentences.append(sentence)
               seen_sentences.add(sentence)
       # 重新组合文本
       cleaned_text = ". ".join(unique_sentences)
   
       return cleaned_text
   
   ```

   示例
   text = """
   **Kyphosis is an abnormal curving of the spine that causes a humpback. The upper back normally curves forward somewhat.** Some children have a greater degree of curvature. The excessive curvature may be Flexible Fixed (structural) In flexible kyphosis, children can straighten the spine by tightening their muscles and the backbones (vertebrae) are normal. The cause is not known. Muscle-strengthening exercises may help, but no other specific treatment is needed. In fixed kyphosis, children cannot straighten the spine because several of the vertebrae in the upper back are wedge-shaped rather than rectangular. Usually, 3 or more vertebrae are involved. Rarely, infants are born with fixed kyphosis, but it more commonly develops later in life, usually in adolescence. There are many rare causes, including fractures, infections, and cancer, **but the most common cause is Scheuermann disease Scheuermann Disease Kyphosis is an abnormal curving of the spine that causes a humpback. The upper back normally curves forward somewhat.**Kyphosis often causes no symptoms. Sometimes mild, persistent back pain develops. Kyphosis may be noticed only because it alters the body’s appearance. The shoulders may appear rounded. The upper spine may appear more curved than normal, or a hump may be visible. Some people have an appearance similar to those with Marfan syndrome Marfan Syndrome Marfan syndrome is a rare hereditary disorder of connective tissue, resulting in abnormalities of the eyes, bones, heart, blood vessels, lungs, and central nervous system. Mild kyphosis that does not cause symptoms is sometimes detected only during a routine physical examination. A doctor may confirm the diagnosis of kyphosis by taking x-rays Plain X-Rays X-rays are high-energy radiation waves that can penetrate most substances (to varying degrees). In very low doses, x-rays are used to produce images that help doctors diagnose disease.**Treatment of kyphosis Treatment Kyphosis is an abnormal curving of the spine that causes a humpback. The upper back normally curves forward somewhat**. Kyphosis: A Humpback Scheuermann Disease Scheuermann disease is the most common form of fixed kyphosis. It usually begins in adolescence, affecting boys slightly more often than girls. The cause of Scheuermann disease is unknown, but it sometimes runs in families. Scoliosis is abnormal curvature of the spine. Scoliosis can be present at birth or can develop during adolescence. Scheuermann disease is an osteochondrosis, which is a group of disorders of the growth plate of bones Overview of Bone Disorders in Children Bone disorders can be caused by injury, infection, or cancer, be inherited, occur as part of a child’s growth, or occur for no known reason. Doctors are not sure what causes osteochondrosis, but the disorders do seem to run in families. Osgood-Schlatter disease Osgood-Schlatter Disease Osgood-Schlatter disease is painful inflammation of the bone and cartilage at the top of the shinbone (tibia). This disease is caused by overuse of the leg. This disease is caused by a poor blood supply to the upper growth plate of the thighbone near the hip joint. Severe kyphosis is more likely to cause discomfort and sometimes can restrict chest motion, causing lung disease. 
   """

   **Kyphosis is an abnormal curving of the spine that causes a humpback. The upper back normally curves forward somewhat.** Some children have a greater degree of curvature. The excessive curvature may be Flexible Fixed (structural) In flexible kyphosis, children can straighten the spine by tightening their muscles and the backbones (vertebrae) are normal. The cause is not known. Muscle-strengthening exercises may help, but no other specific treatment is needed. In fixed kyphosis, children cannot straighten the spine because several of the vertebrae in the upper back are wedge-shaped rather than rectangular. Usually, 3 or more vertebrae are involved. Rarely, infants are born with fixed kyphosis, but it more commonly develops later in life, usually in adolescence. There are many rare causes, including fractures, infections, and cancer, **but the most common cause is Scheuermann disease Scheuermann Disease Kyphosis is an abnormal curving of the spine that causes a humpback.** Kyphosis often causes no symptoms. Sometimes mild, persistent back pain develops. Kyphosis may be noticed only because it alters the body’s appearance. The shoulders may appear rounded. The upper spine may appear more curved than normal, or a hump may be visible. Some people have an appearance similar to those with Marfan syndrome Marfan Syndrome Marfan syndrome is a rare hereditary disorder of connective tissue, resulting in abnormalities of the eyes, bones, heart, blood vessels, lungs, and central nervous system. Mild kyphosis that does not cause symptoms is sometimes detected only during a routine physical examination. A doctor may confirm the diagnosis of kyphosis by taking x-rays Plain X-Rays X-rays are high-energy radiation waves that can penetrate most substances (to varying degrees). In very low doses, x-rays are used to produce images that help doctors diagnose disease. **Treatment of kyphosis Treatment Kyphosis is an abnormal curving of the spine that causes a humpback.** Kyphosis: A Humpback Scheuermann Disease Scheuermann disease is the most common form of fixed kyphosis. It usually begins in adolescence, affecting boys slightly more often than girls. The cause of Scheuermann disease is unknown, but it sometimes runs in families. Scoliosis is abnormal curvature of the spine. Scoliosis can be present at birth or can develop during adolescence. Scheuermann disease is an osteochondrosis, which is a group of disorders of the growth plate of bones Overview of Bone Disorders in Children Bone disorders can be caused by injury, infection, or cancer, be inherited, occur as part of a child’s growth, or occur for no known reason. Doctors are not sure what causes osteochondrosis, but the disorders do seem to run in families. Osgood-Schlatter disease Osgood-Schlatter Disease Osgood-Schlatter disease is painful inflammation of the bone and cartilage at the top of the shinbone (tibia). This disease is caused by overuse of the leg. This disease is caused by a poor blood supply to the upper growth plate of the thighbone near the hip joint. Severe kyphosis is more likely to cause discomfort and sometimes can restrict chest motion, causing lung disease. 

2. 非正文没删干净
   1. **存在网址**(例：September 15, 2022.https://www.ada.org/resources/research/science-and-research-institute/oral-health-topics/antibiotic-prophylaxis.3.Wilson WR, Gewitz M, Lockhart PB, et al: Prevention of viridans group streptocococcal infective endocarditis: A scientific statement from the American Heart Association.Circulation 143(20):e963-978, 2021.DOI: 10.1161/CIR)（√）
   2. **版权**(例：© Elsevier Inc. All Rights Reserved)（√）
   3. 参考
      1. 参考问题可翻译后面文本的意思，有些后面的文本并不是参考书籍，有些是参考治疗方法，参考病例(例： 1, 2 Treatment references Cardiac arrest is the cessation of cardiac mechanical activity resulting in the absence of circulating blood flow.)
      2. **参考文献**（√）

3. 非本文内容
   1. (Other tests, such as vitamin B12 and folate levels and iron and iron binding capacity, are done depending on the suspected cause of anemia.Other tests are discussed under specific anemias and bleeding disorders. )(这个问题，要从文本的内容方面下手去判断删不删)
   2. (.Epub 2020 Dec 10. )全文只有一个属于个例没有删

#### 缺少空格

1. 单词粘连 ([r'([a-z]{2,})([A-Z])',r'\1.\2'])获取多个小写后面跟大写的情况，分别捕获小写和大写，后面大写开头中间加个句号（√）

#### 信息完整

1. 结尾缺少内容

   1. 爬过来的数据本身就没有，只是翻译过来的意思看上去缺少东西，没法处理(例："seq_id": "ead3c455-3e60-481b-9797-77e6b14cabdc")

      (例：信息完整性#0#0#结尾缺少内容，Complicated UTI requires 10 to 14 days of treatment with an antibiotic that is effective against gram-negative organisms, particularly Escherichia coli.Key Points Dysuria is not always caused by a bladder infection.STIs and cancer should also be considered.)

   2. **结尾是半句删到最后的句号处**（√）

#### 标点

1. 缺少标点
2. 多余标点**转义符**，存在markdown格式，正则[r'\\\+','']删不掉，直接print这句话会删掉，在文件里还是存在