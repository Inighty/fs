import hashlib
import json
import logging
import os
import re
import time
import urllib.parse
import urllib.request
import urllib.request
from hashlib import md5
from mimetypes import guess_extension

import requests

logger = logging.getLogger(__name__)


def get_audio(id):
    url = f"https://www.ximalaya.com/revision/play/v1/audio?id={id}&ptype=1"
    payload = {}
    headers = {
        'authority': 'www.ximalaya.com',
        'dnt': '1',
        'sec-ch-ua-mobile': '?0',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36',
        'sec-ch-ua-platform': '"Windows"',
        'accept': '*/*',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'accept-language': 'zh,zh-CN;q=0.9,en;q=0.8,zh-TW;q=0.7,en-US;q=0.6,ja;q=0.5'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    res = json.loads(response.text.encode('utf8'))
    src = res['data']['src']
    result = urllib.request.urlretrieve(src)
    if result and len(result) > 0:
        temp_path = result[0]
        content_type = result[1].get_content_type().partition(';')[0].strip()
        if content_type.__contains__("m4a"):
            suffix = ".m4a"
        else:
            suffix = guess_extension(content_type)
        result = temp_path + suffix
        os.rename(temp_path, result)
        return result
    else:
        logger.error("下载异常:" + src)
        exit(0)


def pre_upload():
    data = {
        "tasktype": "voice2text",
        "limitsize": 20480,
        "filename": "audio.mp3",
        "filecount": 1,
        "isshare": 1,
        "timestamp": int(round(time.time())),
        "softname": "pdfonlineconverter",
        "softversion": "V4.2.9.1",
        "machineid": mid,
        "productid": 146,
        "validpagescount": 20,
        "filesrotate": 0,
        "filesequence": 0,
        "fanyi_from": "zh-CHS"
    }

    data_sign = []
    for k in sorted(data):
        data_sign.append(k + "=" + str(data[k]))
    data_sign = "&".join(data_sign) + "hUuPd20171206LuOnD"
    data['datasign'] = hashlib.md5(data_sign.encode("utf-8")).hexdigest()

    req = urllib.request.Request(url="https://app.xunjiepdf.com/api/v4/uploadpar",
                                 data=urllib.parse.urlencode(data).encode('utf-8'))
    resp = urllib.request.urlopen(req)
    body_str = resp.read().decode("utf-8")
    meta = json.loads(body_str)
    return meta


def upload_chunk(tasktag, timestamp, tasktoken, chunks, chunk, size, data):
    headers = {
        "Content-Length": size,
        "Cookie": "xunjieUserTag=98F0CBB05248B0FB6ED5B487D49F4752; site_redirect_loginuri=https%3A//app.xunjiepdf.com/voice2text/; _ga=GA1.2.1632791774.1624503980; _gid=GA1.2.2015745962.1624503980; OUTFOX_SEARCH_USER_ID_NCOO=1563871560.1974661; appdownhide=1; Hm_lvt_6c985cbff8f72b9fad12191c6d53668d=1624503980,1624505334; xunjieTempFileList=0bd2b06ce2bb4b0b937e51ef1850d09c%7c87fbc4af9f7141da8a70001f675ffd0c%7cf87142a187244fb89428e56b81d1e573%7c7e96eef5ccb3448cbf2d85044b2f1e13%7c0ce8ca7c41de474ea9ac387e99c653f5; Hm_lpvt_6c985cbff8f72b9fad12191c6d53668d=1624517381; _gat_gtag_UA_117273948_9=1"
    }
    req = urllib.request.Request(
        url=f"https://app.xunjiepdf.com/api/v4/uploadfile?tasktag={tasktag}&timestamp={timestamp}&tasktoken={tasktoken}&fileindex=0&chunks={chunks}&chunk={chunk}&id=WU_FILE_0&name=audio.mp3&type=audio^%^2Fmpeg&lastModifiedDate=Thu+Jun+24+2021+11^%^3A08^%^3A48+GMT^%^2B0800+(^%^E4^%^B8^%^AD^%^E5^%^9B^%^BD^%^E6^%^A0^%^87^%^E5^%^87^%^86^%^E6^%^97^%^B6^%^E9^%^97^%^B4)&size={size}",
        headers=headers,
        data=data)
    resp = urllib.request.urlopen(req)
    body_str = resp.read().decode("utf-8")
    upload_result = json.loads(body_str)
    return upload_result


def task_down(tasktag):
    headers = {
        "Content-Type": "application/json; charset=UTF-8"
    }
    data = {"productinfo": "1245A2A101F776005F2E909C29CC8F7369FAA0BED21AE0A9F9ADBD8D49EE3783",
            "deviceid": mid, "timestamp": int(round(time.time())), "tasktag": tasktag,
            "downtype": 2,
            "brandname": "-迅捷PDF转换器"}

    data_sign = []
    for k in sorted(data):
        data_sign.append(k + "=" + str(data[k]))
    data_sign = "&".join(data_sign) + "hUuPd20171206LuOnD"
    data['datasign'] = hashlib.md5(data_sign.encode("utf-8")).hexdigest()
    url = "https://app.xunjiepdf.com/api/v4/taskdown"

    response = requests.request("POST", url, headers=headers, data=json.dumps(data))
    body_str = response.text.encode("utf-8")
    down_result = json.loads(body_str)
    return down_result


def split_data(filepath):
    fp = open(filepath, "rb")
    data = fp.read()
    fp.close()
    length = 3 * 1024 * 1024
    chunks = [data[i:i + length] for i in range(0, len(data), length)]
    return chunks


def audio2text(filepath):
    meta = pre_upload()

    if meta["code"] != 10000:
        print(meta)
        return

    chunks = split_data(filepath)
    for i in range(0, len(chunks)):
        upload_chunk(meta["tasktag"], meta["timestamp"], meta["tasktoken"], len(chunks), i,
                     len(chunks[i]), chunks[i])

    time.sleep(30)

    down_result = task_down(meta["tasktag"])
    result = urllib.request.urlretrieve(down_result['downurl'])
    path = result[0]
    with open(path, mode='r', encoding='utf-8') as f:
        result_text = f.read()
    os.remove(path)
    return result_text


if __name__ == '__main__':

    import pycorrector

    aa = '﻿大家好，欢迎收听牧师讲堂。那今天这节课我们来讲出租房风水那些事儿。前几天有个同学联系我，说自己住了一个房子，搬家的时候打扫卫生，结果在客厅墙壁的一个夹层里找到了一张黄色的符纸，就是那种用红朱砂写的道符，应该是前一个租客留下来的东西。他心里发毛，就发给我，让我帮忙看看这张图到底有什么用。那我看了一眼他发过来这个照片可能放了挺久，上面的字迹很模糊，但是挺明显的，有镇宅两个字，民间其实也比较常见。其实我对这类东西没有太多研究，所以也不好评价。不过在我看来，这张符本身是什么不重要，重要的是通过这。这东西间接地得到了一个线索，就是前租客肯定是摊上了什么事儿，如果住在这个房子里顺风顺水的情况下，没人会想到去搞一张这个东西藏在家里，对不对？那这样我想起了这个零九年的时候，在成都数码广场附近，我看过的一个风水客户是一对情侣，因为都在城里工作，为了通勤方便就在公司附近租了一个老房子。房东是一位老人，特别迷信，家里贴了很多乱七八糟的这种符纸，而且还特别要求这个房子里的这些符纸你一张都不能给他动。虽然看着特别不舒服，但是除了这一点，这房子无论是租金还是地理位置都符合他们的需求，所以他当时也没有多想决定。但租下来，可是后来发生了很多诡异的事情，住进来以后两人就经常吵架，而且瞌睡还特别多，一回到家就想睡觉，但是睡觉又睡不踏实，精神状态也不好。特别是她男朋友还经常睡到中途的时候，嘴里急急哼哼，开始手和脚就开始乱蹬，看着像是做噩梦，喊他半天也没反应。两个人后来也是吓得不轻，住了半年以后情况是是越来越糟糕，家里还经常闻到臭味儿，但是家里也没有什么腐烂的东西，找不到这个臭味儿的源头，墙角经常还出现很多死虫子，甚至还遇到过几次小鸟莫名其妙的撞家里窗户的情况。其实后来他俩找到我的时候，他们已经是在找另外的房子了，准备搬出去。然后计划是去看新房子，那请我顺道帮他们去现在住的房子看一看，因为找房子和搬家还需要一段时间，那当时我就去现场看了一下，一进门就正对厕所，而且还是没有窗户的那种厕所。他俩住在西南方的主卧，有阳台，其实按理说通风、采光应该都不错，但是一进去就感觉阴凉阴凉的。东北角有一个房间上着锁，一问好像是房东用来堆放以前家里杂物的，房间不让用，一直都锁着。住进来快一年了，房东只来过一次，到这个房间里取了一些东西。听他们俩说里面好像还有一些照片，看着挺像那种遗像的，但是不确定，也不敢问。那我仔细观察了一下家里从入户门。开始里面每个房间的这个门的门头上都贴着一张黄纸，画了一些不明所以的文字和符号，那挺像茅山一派的东西。其实这些对我来说都不算什么大问题。那我比较敏感的是这房子打一走进来，开始就给我一种衰败的感觉，就是那种长期无人居住，就差这个满屋挂满蜘蛛网的那种感觉。那其实这就是我以前讲过的一个问题，首先这房子气色就不好，而且我在这个窗台外一个不太明显的位置发现了一些用过的针头和一个医用输液的那种导管。那这房子斜对面就是成都的华西医院，说明这个房子很可能曾经居住过病人，而且应该挺严重。然后客厅的地板上还有很明显的一大片这个油渍，还有一块儿被火烧焦的一个区域。那我当时我就问他们有没有问过房东这里到底是怎么回事儿？那他俩当时其实也看到了，也问过房东说这里曾经租给过一个卖烤串儿的夫妇，可能是晚上在客厅里加工烤串儿造成的，所以这个房子曾经还做过临时的食品小作坊。总而言之，这房子的历史应该是非常复杂，而且每个租客待的时间都不长。那我为什么要花这么长时间讲这个事情？其实通过这个事情，有几点大家租房的时候可能会忽略掉的事情，首先就是你需要了解一下房子的前世今生，就像这种房子。年代久远，而且房东长期不住，主要是用来出租的房子。那说实话能不选就不要选，为什么因为你都不知道这房子到底经历过什么。那我们最好是租那种性质比较单纯的房子，比如说房东一直都住在这里，然后近期换房了，把空余的房产出租。那这种房子性质相对它比较单纯一些，没有太多乱七八糟的事情。那第二点就是租整不租零，就是有能力咱们就租整套，就不要跟别人合租单间。如果你是整租的一套房子，那这个房子里所有的房间理论上应该都是你的。如果像前面这个事情中讲的，这个房东说其中一间你不能用，他要用来放自己的。东西，那你就不要租了，因为你无法控制他会在这个房间里放些什么东西，会对你产生什么样的影响。所以我们不去赌这个运气，那合租也会出现这样的问题，你自己可能很注意风水、环境的问题，但是你无法保证别人怎么去做。所以我们能整租，我们就最好不要去租单间。那对于租房来讲，大家还有一点要注意一下，除了家里必须用到的家具、家电以外，那房东或者上一任租客留下来的东西我们都尽量不要放。在正式签约之前，就要把这些细节问题都讲清楚，让房东给你处理干净。那我经常是遇到一些客户或者一些同学来咨询我，买二手房的或者租房的都有都遇到过一些相同的。问题就是前房东或者前租客遗留下来一些什么佛像、风水物品、甚至是他们自己的照片。那这些东西如果等你住进去以后再处理就很麻烦，最好一开始你就检查清楚，同时还要注意房子的一些细节以及征兆。那比如说像这个案例中讲的，房子里墙角发现经常发现死虫子，或者说有找不到源头的这个臭味儿，或者说房子里贴着莫名其妙的什么纸张或者符咒，或者一进门就感到什么阴凉或者让人不舒服。其实这些都是征兆。什么征兆风水不好的征兆。那第三点就是不租三改柱。什么叫商改住？就是原来这里用来做经营场所，后来。你租过来用来居住，那这种最好不要租。比如说在一些小区或者公寓住宅中，有一些租客会把租来的这个住宅用作办公，经常就有人在这里来来去去、乱七八糟的，什么人都有，甚至还有像我前面案例中讲到的，直接就把这个房子用来搞成的这个小作坊，搞的房子里是乌烟瘴气，然后你住进来以后，那这种房子其实很难短时间内去做好净化，你至少得放个小半年，特别麻烦。那第四点，对于出租房来讲，还有一点就是租新不租旧。因为大家要知道，风水中也讲究喜新厌旧，什么叫喜新厌旧？就好比说房子、家中的家具、物品等等，那跟我们人以。都有一个使用寿命，或者再说直白一点，都有一个气运。所以说不管任何东西都可以用这个理论去讲。就比如说你从外面买一个什么招财的物品回家，那我们假设它起了作用，那可能刚开始放的时候你明显感到了变化，但是随随着时间的推移，你发现这种变化会越来越小，甚至说到最后又回到了跟以前一样的状态。那这种现象其实在风水中会经常出现，所以不管是什么风水布局都不可能永远对你有利，那房子其实也是这样，所以对于出租房来讲，那当我们有条件选择的情况下，我们最好首先考虑房龄新一点的小区，同时。优先选择装修新一点的房子，那这就是租金不租旧的第一原则。那否则就好比说我们以前讲地运一样，七运的房子相对于现在八运来讲就属于会运宅。那这种过了运的房子，如果不是特别好的户型或者特别好的外环境，那如果没有这些因素的这个辅佐或者是加持，那基本上就是越做越衰的格局。那相当于就是说你一住进来就已经是房子最衰弱的时候了。那可能有同学又说了，老师没办法，找不到合适的房子，我只能租那种老房子就装修的房子，怎么办？那这就得说到另一个问题，就是旧装修、新装饰。那什么是。就装修、新装饰那现在很多装修公司都比较流行和提倡一个理念，就是轻装修、重装饰。那也就是说不必要把这个钱花在昂贵的材料上面，而是重点关注如何处理好装修的美观和设计上。那旧装修、新装饰的意思也就是说在原来的装修不改变的情况下，利用如短信的装饰与重新对家里进行布局、设计，达到除旧换新的目的。那就好比说你人没变，但是你穿上了一件新衣服，人虽然老了，但是显得年轻、漂亮，大概就是这个道理。那旧装修、新装饰需要注意的几点就是当你租到。一个房子以后，你尽最大的可能将房子内的陈设、陈列都重新换一下，因为也是别人的房子，你投入太多钱在装装修上面感觉也不划算，对吧那你以后也拿不走，但是装饰物品它很简单、很便宜，以后你也可以打包拿走。比如说举个例，你在原来空空如也的这个电视柜上，你放一个漂亮的花瓶，是吧？你更换一下房内的挂画，对吧，然后买一张新的沙发垫或者新的花像购置一些漂亮的装饰摆件，或者在条件允许的情况下，换一换家里的家具、摆设，那不管你是怎么换，只要稍微跟原来不一样就行。那我为什么要讲这个？因为很多人在租房子的时候都有一个想法，就是最好能够拎包入。住什么也不用管。那如果你是长期住下去的话，那建议你在听完我这节课以后改变这个想法。那最好的思路就是在房东已经提供相关东西的情况下，小南你仔细去看一看，哪些是可以替换的，哪些是不必要替换的、需要替换的、更换的。你跟房东协调好，就说你不需要请房东搬走。比如说你发现出租房的阳台有一个房东留下来的花架，那可以用来种花，那这种东西其实不值钱，完全可以换新的，你就让房东拿走，你重新再买一个新的回来。所以不是说什么东西你都要留下，好像你占了房东很大便宜一样。相反的，如果你打算在这里长期住上很长一段时间的话，最好是换一些自己的新东西进来，特别是。房子的软装方面特别需要设计、布置一下。那因为对于出租房而言，很多东西不止一个人用过，是很多人都用过。那有同学可能会说二手房也是这样，但是出租房跟二手房的性质又有一些不同，二手房通常来说可能几十年才会换主人，对吧？而出租房的流动性就大了，在一些人员流动性大的地区，一年内可能会换一到两个租客。那按照这种频率来看，即便房子本身很好的风水，可能都难以发挥作用。不仅发挥不了作用，还会有反作用。那就是人来人往的环境下，难免会留下一些不好的东西。所以以前有同学问我说，小区里的样板房能不能买，或者说小区开发商想把自己的房子装修成样板间共。您参观。那这样有没有问题？说实话，你要是不差这点钱的话，你最好还是不要去贪这点小便宜，所以能换新的就换新的。但是出租房不同于二手房的事，出租房我们不需要更换火灶和床，因为毕竟你只是租住而不是购买，所以火燥不必更换。按照民间习俗上的说法来讲，就是这个赵老爷你没必要请过来，因为跟你也没有什么关系。那说到这个火灶，顺便说一下另外一件事情，那以前有同学问我说：老师听你讲课，这个课程中讲保险柜要放在西北方，那如果是租的房子，这保险柜是不是还是放西北方？那关于这个问题，我说两点，第一，按理论来讲。西北为财库，那住在这里财库肯定也在西北，那这个是没有任何疑问的。所以理论上来讲还是放西北方。但是我要说的第二点是这种财我曾经遇到过好几个案例比较特殊，其中有一个案例很经典，就是一个客户在城里租了一个房子，然后听了我的课程，跑到西北方放了一个保险柜，然后不到半个月，出现了一件让他哭笑不得的事情，就是房东跑来告诉他，他的房子被人买了，而且价格还不低。那边买家急着搬过来，所以需要他尽快搬走。为了表示歉意，房东愿意在支付合同违约金的同时，再赔偿给他三个月的房租作为补偿。那他这算了。小，虽然麻烦一点，得重新找地方，但是白做了几个月，还倒赚了一笔钱。走。所以他跑来问我说：老师，这个在出租房西北方放保险柜，是不是把房东的财运给吹起来了？房东卖了这个房子，应该是赚了不少钱。那我听完后，我也调侃他，我说：你不是自己也赚了一笔钱吗？是不是皆大欢喜？所以在出租房的西北方放保险柜可能会有这么一种情况出现，那也就是说西北方的财可能会有被共享的情况共享的情况。那还遇到过一个案例，就是什么租客前脚刚升职、加薪，这房东后脚马上就涨房租。所以后来同学问我这个问题的时候，我都会跟他们讲，稳妥起见，如果你自己租房子住。要在西北方放保险柜，那你就在保险柜的上面这个外面的这个顶上，你放一个跟你相同生肖的摆件，然后头对着你睡觉的主卧方向，比如说你属牛，对吧那你就放一只牛上去，头朝着你睡觉的地方。代表说这个保险柜是给属牛的人用，相当于是认个主人。好了，我们继续来讲。那对于出租房来讲，还有一点需要注意，就是我以前课程中讲到的进宅，那也就是需要简单的净化一下房子，那最好是挑这个黄道吉日中的除日去做这件事情。那这些都是不复杂、又实用的风水处理方法。所以这里还要讲到一点，就是租房最忌急迫搬家。也就是你不要急着搬进去，不要前租客前脚刚走，你后脚就急着搬进去。那说难听一点，这屁股刚离开凳子还会有余热，对吧？你总得晾一会儿，所以你不要急着搬家。那除日这一天除了适合做进展以外，除还有去除、扫除的意思，所以这一天特别适合搞卫生。那如果正好有空，你在搬进来之前，你就彻底的来一次大扫除，给房子洗个澡。特别是对于出租房来讲，很多人因为不是自己的房子，所以可能没有太多热情去收拾家里的卫生，那这种形态其实不太好。那除了搬家之前，平时家里脏了也适合选厨子搞一下大扫除，既来之则安之，你只要还住在这里一天。那这里就是你的家。咱们俗话也说，房子在哪儿不重要，家人在哪儿？哪儿就是家。那最近也有很多人在谈论房子，说这个房价太高，买房还不如租房住，然后还仔细的算了一笔经济账，算下来确实很划算。不过我个人觉得抛开经济原因不说，如果一辈子都租房住，你避不开一个很重要的问题，就是对家的认同感和归属感。你如果对一个房子没有认同感和归属感，那这个房子肯定也不会任你做主人，自然就成了无主之地，你对这个房子来说仅仅也是过客而已。所以说一句站着说话不腰疼的话，有条件的话，趁现在年轻努力工作，拥有一套自己的房子，金窝、银窝不如自己的狗窝，房子永远是最可靠的。转弯，祝大家都能够拥有一个自己温馨、甜蜜的房子。好了，今天的课程就讲到这里，谢谢大家，我们下期节目再见。'
    corrected_sent, detail = pycorrector.correct(aa)
    print(corrected_sent, detail)
    exit(0)
    mid = "245E055883F34DB63C6FE3B039C130B5"
    id = 459619196
    audio = get_audio(id)
    if audio is None:
        exit(0)
    text = audio2text(audio)


    def clean_txt(data):
        data = re.sub("(哎|呢|哈|啊|啊、|呐|呀|那么|呃|嘛|诶)", "", data)
        return data


    text = clean_txt(text)
    print(text)
