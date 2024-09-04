### 1.删除日期类文本

例如：

Page last reviewed: 24 May 2022

Next review due: 24 May 2025

*   Previous : Why it’s done

Next : What happens on the day day

Page last reviewed: 13 October 2021u and your baby at 25 weeks pregnant

增加到删除1：

```
(?:\n|^)((?:\* *)?(?:Next review due|Page last reviewed|Previous|Next|Media last reviewed|Media review due|iewed) *[:：].*)
```



### 2.类似使用说明书类的

这类需要整页删除，例如：

```
Benzoyl peroxide \- Brand name: Acnecide
========================================

Find out how benzoyl peroxide treats acne and how to use it.

*   About benzoyl peroxide
*   Who can and cannot use it
*   How and when to use it
*   Side effects
*   Pregnancy, breastfeeding and fertility
*   Using it with other medicines and herbal supplements
*   Common questions

Related conditions
------------------

*   Acne

Useful resources
----------------

*   HealthUnlocked: acne forum
    
    healthunlocked.com
    
*   HealthUnlocked: benzoyl peroxide forum
    
    healthunlocked.com
    
*   British Skin Foundation
    
    www.britishskinfoundation.org.uk
```

增加删除2

```
((?:.*\n=+\n+)(?:.*how to (?:use|take) it\.)\n+(?:\* *.*\n)+\n+(?:Related conditions\n-+)\n+(?:\* *.*\n)+\n+(?:Useful resources\n-+)\n+(?:(?:\* *.*(?:\n|$))|(?: {2,}.*(?:\n|$)))+)
```



### 3.视频介绍类的删除

例如：

Video: ovarian cysts

This video explores the symptoms ovarian cysts can cause, the long-term effects, and the treatment options.

Media last reviewed: 1 April 2021  
Media review due: 1 April 2024

Page last reviewed: 21 June 2023  
Next review due: 21 June 2026

*   Next : Causes（下个标题）

-------------------------------------------------------------------------------------------------------------------------------

遇到下一个标题时，会删除到下一个标题为止。下面没有标题时会删除以下全部内容

增加删除3

```
(?:\n|^)((?:#* *Video[:：].*\n-*\n)(?:.*\n*)*?)(?:(.*\n-+)|$)
```



### 4.视频内容介绍、问题介绍、帮助我们改进网站的删除

例如：

Help us improve our website（About this video/Common questions）标题

---------------------------

Can you answer some questions about your visit today?

Take our survey（内容）

遇到下一个标题时，会删除到下一个标题为止。下面没有标题时会删除以下全部内容

增加删除4

```
(?:\n|^)((?:About this video\n-*\n|Common questions\n-*\n|Help us improve our website\n-*\n)(?:.*\n*)*?)(?:(.*\n-+)|$)
```



### 5.特例的信息介绍

例如：

Information:

Find out more about stretch marks in pregnancy（特定以Find out more开始的介绍）


Information:

You can report any suspected side effect using the Yellow Card safety scheme.

Visit Yellow Card for further information.（固定句式，出现多次）

增加删除5

```
(?:\n|^)(Information: *\n+(?:Find out more about.*|You can report any.*\n+Visit Yellow Card.*))
```



### 6.固定格式的信息介绍

例如：

Information:

**Find out more:**

*   GOV.UK: SEND code of practice: 0 to 25 years gives advice about special educational needs and disability
*   Council for disabled children: What is an Education Health and Care Plan

Want to know more?

*   Kidney Patient Guide: Finances
*   MoneyHelper
*   Kidney Care UK: Benefits（以点开头）

Further information

National Joint Registry: metal-on-metal hip implants（出现冒号的介绍）

增加删除6

```
(?:\n|^)((?:Information:\n+)?\**#* *(?:Find out more[:：]|Further information[:：]?|Want to know more\?) *\**\n-*\n+(?:(?:\* *.*\n{1,2})|(?:.*[:：].*\n{1,2}))+)
```



### 7.单行：阅读更多获取信息类的删除

例如：

Spinal Muscular Atrophy UK has more information about type 3 SMA.

Find out more from infoKID about AKI in children
Read more about the heart transplant waiting list.

增加删除7：

```
(?:\n|^|.)((?:Read.{1,5}more|Find(?: out)?.{1,5}more|.*has more) (?:information (about)?|about|from).*)
```



### 8.单行：参见内容的删除

例如：

See preventing stillbirth for more information
See alcohol support for more information about the help available.
See pictures of genital warts 

增加删除8：

```
(?:\n)([Ss]ee[:：]? [^\n()（）]*(?:[Aa]ppendix|[Ff]igures?|[Tt]able|for more information|[Pp]ictures?|guide).*)
```



### 9.信贷类的删除

例如：

Credit:

SCIENCE PHOTO LIBRARY https://www.sciencephoto.com/media/481108/view（特征是后面会有链接）

增加删除9：

```
(?:\n|^)(Credit:\n(\n.*(?:https?:\/\/(?:www\.)?|www\.)[ a-zA-Z0-9-]+(?:\.[a-zA-Z]{2,})+(?:\/[^ \n\u4e00-\u9fa5]*)?)+)
```



### 10.目录类的删除

例如：

Contents

1.  Overview
2.  Symptoms
3.  Causes
4.  Tests and next steps
5.  Treatment
6.  Help and support

增加删除10:

```
(?:\n|^)(Contents *\n-+(\n+\d\..*)+)
```



### 11.更多内容、资源类的删除

例如：

More in Pilates and yoga exercise videos（Related conditions/Useful resources/You can find more）标题

----------------------------------------

*   Pilates video for beginners
*   Pyjama pilates video workout

增加删除11：

```
(?:\n|^)((?:More in.*\n-+| *Related conditions *\n-+| *Useful resources *\n-+|You can find more.*[:：])\n+(?:(?:\* *.*(?:\n|$))|(?: {2,}.*(?:\n|$)))+)
```

