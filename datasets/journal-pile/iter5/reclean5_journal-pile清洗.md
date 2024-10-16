reclean5_journal-pile清洗

reclean4_journal-pile分析

针对本次抽样中的无关文本，预计可解决80%，提升5分

错误删除可解决60%，提升1.8分

其中的无关文本基本还都是新错误，预计还会有较多的新错误出现



错误删除

```
在删除类似于(IJCCM-21-40-g003)编号时匹配的范围比较宽对带有括号的(...-...-...)的情况都删除掉了
[r'(\(([^-\.,\s]{1,10}-){2,}[^-\.,\s]{1,10}\))',r'删除34:<u>\1</u>'],         # 删除类似于编号 (IJCCM-21-40-g003)
↓
[r'([^-]\s?)(\([\dA-Z]{1,10}-([^-\.,~\s]{1,10}-){1,}[^-\.,\s]{1,10}\))([^-]\s?)', r'\1删除34:<u>\2</u4'],  # 删除类似于编号 (IJCCM-21-40-g003)


```

无关文本

```

[r'(^(This|The)\s.* (was|is) supported[^$]*)', r'删除38:<u>\1</u>'],  # 这项研究得到了...的支持
↓
[r'(^(This|The)\s.* (was|is) (supported|funded)[^$]*)', r'删除38:<u>\1</u>'],  # 这项研究得到了...的支持/资金支持

[r'\([^\(\)]{0,20}([,\.;\s]{0,}\[[^\[\]]{1,50}\]\([^\)\(]{1,50}\)\{[^\{\}]{1,50}\}){1,}[^\(\)]{0,20}\)', r''],
↓
[r'\([^\(\)]{0,20}([,\.;\s]{0,}(and\s+)?\[[^\[\]]{1,50}\]\([^\)\(]{1,50}\)\{[^\{\}]{1,50}\}){1,}[^\(\)]{0,20}\)', r''],
# 固定删除格式 [...](...){...} 外面可带圆括号或方括号，括号一定是同一种要带都带,要不就都不带

[r'\[[^\[\]]{0,20}([,\.;\s]{0,}\[[^\[\]]{1,50}\]\([^\)\(]{1,50}\)\{[^\{\}]{1,50}\}){1,}[^\[\]]{0,20}\]', r''],
↓
[r'\[[^\[\]]{0,20}([,\.;\s]{0,}(and\s+)?\[[^\[\]]{1,50}\]\([^\)\(]{1,50}\)\{[^\{\}]{1,50}\}){1,}[^\[\]]{0,20}\]', r''],
# 固定删除格式 [...](...){...} 外面可带圆括号或方括号

[r'(^The authors?.*(thanks?|grateful|acknowledge).*)', r'删除26:<u>\1</u>'],  # 作者感谢...的支持之类的描述
↓
[r'(^(The authors?|We are).*(thanks?|grateful|acknowledge|indebted|appreciates?).*)', r'删除26:<u>\1</u>'],

[r'(^This work has been.*$)',r'删除40:<u>\1</u>'],   # 固定表述  这项工作...
[r'(^10.7717.*$)',r'删除41:<u>\1</u>'],  # 固定表述  单独一行 10.7717...
[r'(.*All authors read and approved the final manuscript.*)',r'删除42:<u>\1</u>'],     # 带有All authors read and approved the final manuscript的描述
[r'(\.)((Table|Fig)(\.)?\s?\d[A-Z].*)',r'\.删除43:<u>\2</u>'],      # 处于句子的句末的Table/Fig描述
[r'(^E-mail:[.\n]*)',r'删除44:<u>\1</u>'],   # E-mail:开头的句子
[r'(^The data underlying[.\n]*)',r'删除45:<u>\1</u>'],   # 基础的数据...  一般都在第一句
[r'(.*equally to this work.*)',r'删除46:<u>\1</u>'],    #  ...对此贡献对等
[r'(.*contributed equally.*)',r'删除47:<u>\1</u>'],     # 同46
[r'(.*All authors (participated|have read).*)',r'删除48:<u>\1</u>'],   #All authors participated 所有的作者都参加了...
[r'((Table|Fig)(\.)?\s?\d\s?$)',r'删除49:<u>\1</u>'],
# 检查是否匹配 'Ethics Statement'后连续对下一个item也进行删除
if re.search(r'^Ethics Statement[.\n]*', item):
    final_results.append("")  # 当前项置为空字符串
    if i + 1 < len(context):  # 确保下一个项存在
        final_results.append("")  # 下一个项也置为空字符串
        skip_next = True  # 标记跳过下一个项
    continue  # 跳过剩余替换逻辑
```

文章末尾段落删除新增

```
Additional Information and Declarations|Funding:|Declaration of patient consent|Enhanced content|Publisher(\'s)? note|No funding|The authors? declare that|Acknowledgment|Contributors:|The following information|Source of Support:
```



