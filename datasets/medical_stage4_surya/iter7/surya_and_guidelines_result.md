## 无关文本

- 正则能识别但是删不掉 (已解决)

例，78f29033-7524-4ab7-b71b-9eafb38c55ce：Several risk factor estimates are available for use by clinicians, including Simoons,  the Co-Operative Cardiovascular Project,  and the In-Time 2 trial. 211\n\n##Percutaneous Coronary Intervention (Pci)

这里的211能识别，单独这句话拿出来也能删掉，但是跑全量删不掉，一般出现在两个换行符的时候





- 最后还是把暴力的数字删除方法去掉了 ，会有一些数字删不掉

例：6cca7dc3-d31b-48e3-9cfb-1709f8d732ff：Potential dangers of prolonged tourniquet application include temporary 62 or permanent 63 injury to the underlying nerves and muscles,  and systemic complications resulting from limb ischemia,  including acidemia, hyperkalemia, arrhythmias, shock, and death.里面的62，63



## 多于换行,主要是还有需要解决的问题未解决，没有看到是因为处理缺少换行错误导致的

- 应该连接的两行中间穿插点其他内容，导致没有办法合并

  例：

  substitute for tocilizumab. Upon development of CRS, the Network

  ##Nccn Guidelines Version 4Acute Lymphoblastic Leukemia（中间有个标题穿插进去）

  panel recommends holding blinatumomab infusions with consideration for 

- 前一句小写结尾下一句大写开头的情况，因为他和上面标题下面正文的情况特征相同，所以此情况并没有处理，（但是此特征确实需要连上去的情况也比较多）

  例：Spirometry: Spirometry is one of the PFTs, and is the most important\n

  PFT in the setting of asthma diagnosis and treatment. Spirometry measures the flow of air from the lungs as a person forcefully and fully exhales from a deep inspiration.

## 语义不完整

误删导致的语义不完整，这里在解决页边角问题上对每一小块进行了检测，检测的规则是块的上边界距离页的下边界<=80,证明这个块很靠近下边界就会返回True，所以会导致一部分正文的块也非常的靠近下边界被误删（已解决用full_blocks进行is_page_foot的判断）

```
# 检测右测边角
if img_box[2] - least_bbox[0] <= 80:
    return True
# 检测下面边角
elif img_box[3] - least_bbox[1] <= 80:
    return True
# 检测左侧边角
elif least_bbox[2] - img_box[0] <= 80:
    return True
# 上边角会遇到标题这个问题，要不要解决？
elif least_bbox[3] - img_box[1] <= 80:
    return True
else:
    return False
```

例如：

"block_text_old": " If a lone rescuer finds an unresponsive adult (ie, no movement or response to stimulation) or witnesses an adult who suddenly collapses, after ensuring that the scene is safe, the rescuer should check for a response by tapping the victim on the shoulder and shouting at the victim. The trained or",

 "raw_context": [

{"text": "If a lone rescuer finds an unresponsive adult (ie, no move-", "bbox": [404.0, 916.0, 719.0, 930.0]},

 {"text": "ment or response to stimulation) or witnesses an adult who", "bbox": [403.0, 931.0, 721.0, 945.0]}, 

{"text": "suddenly collapses, after ensuring that the scene is safe, the", "bbox": [403.0, 946.0, 720.0, 961.0]},

 {"text": "rescuer should check for a response by tapping the victim on", "bbox": [403.0, 962.0, 720.0, 977.0]},

 {"text": "the shoulder and shouting at the victim. The trained or", "bbox": [403.0, 977.0, 720.0, 991.0]}]

减小数字或者加入其他条件  （左右应该没问题，上下的话可以考虑一下）   

用full_blocks去判断也可以,如果页脚混在某个大块里是里面的一个最小单位怎么办？



