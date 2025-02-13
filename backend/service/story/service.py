import threading
import time

import tools.tmpCache
from tools.xyqStoryUtils import utils
from repository.dao import userStoryDAO
from repository.dao import totalStoryDAO
from repository.dao import paragraphsDAO


# 返回故事id， True
def generateStory(userName, outline):
    # res = (故事大纲，故事，绘画prompt, 润色，urls)
    res, ok = utils.workflow(outline)
    if not ok:
        return None, False
    # 唯一标识一个故事
    storyId = time.time().__str__()
    if len(res) < 4 or len(res[0]) < 2 or len(res[1]) < 2 or len(res[2]) < 2 or len(res[3]) < 2 or len(res[4]) < 2:
        return None, False
    # 对三个表插入数据, user_story, total_story, paragraphs
    ok = userStoryDAO.insert(userName, storyId) and totalStoryDAO.insert(storyId, res[0],
                                                                         res[1]) and paragraphsDAO.insert(storyId,
                                                                                                          res[2],
                                                                                                          res[3],
                                                                                                          res[4])
    if ok:
        return storyId, True
    return None, False


def generateStoryStream(userName, outline):
    # 创建工作流
    workflow = utils.stream_workflow(outline)
    # 唯一标识一个故事
    storyId = time.time().__str__()
    # Stage 0
    res0 = next(workflow)
    yield [storyId] + res0, True
    # Stage 1
    res1 = next(workflow)
    yield [storyId] + res1, True
    # Stage 2
    # res = (故事大纲，故事，绘画prompt, 润色，urls)
    res, ok = next(workflow)
    if not ok:
        yield None, False
    if len(res) < 4 or len(res[0]) < 2 or len(res[1]) < 2 or len(res[2]) < 2 or len(res[3]) < 2 or len(res[4]) < 2:
        yield None, False
    # 对三个表插入数据, user_story, total_story, paragraphs
    ok = userStoryDAO.insert(userName, storyId) and totalStoryDAO.insert(storyId, res[0],
                                                                         res[1]) and paragraphsDAO.insert(storyId,
                                                                                                          res[2],
                                                                                                          res[3],
                                                                                                          res[4])
    if ok:
        yield storyId, True
    return None, False


def generateStoryAsync(userName, outline):
    # res = (故事大纲，故事，绘画prompt, 润色，urls)
    res, ok = utils.async_workflow(outline)
    if not ok:
        return None, False
    # 唯一标识一个故事，同时作为任务id
    storyId = time.time().__str__()
    print("storyId:", storyId)
    # 在缓存中存储已生成内容，同时开始异步任务
    # res = ["", "", [""], [""], [""], [""]]
    tools.tmpCache.setTaskCache(storyId, res)
    generateThread = threading.Thread(target=generateStoryAsyncProcess, args=(storyId, userName, res))
    generateThread.start()

    return storyId, True


def generateStoryAsyncProcess(storyId, userName, context):
    res, ok = utils.async_workflow_process(context, storyId)
    # 更新缓存状态
    tools.tmpCache.setUrls(storyId, res[4])
    tools.tmpCache.finishTask(storyId)
    # 对三个表插入数据, user_story, total_story, paragraphs
    ok = userStoryDAO.insert(userName, storyId) and totalStoryDAO.insert(storyId, res[0],
                                                                         res[1]) and paragraphsDAO.insert(storyId,
                                                                                                          res[2],
                                                                                                          res[3],
                                                                                                          res[4])
    if not ok:
        raise Exception("数据库写入失败")


# 保存故事
def saveStory(storyId):
    return userStoryDAO.updateByStoryId(storyId, 'yes')


# 删除故事, 需要删除三个表的数据
def deleteStory(storyId):
    return (userStoryDAO.deleteByStoryId(storyId) and totalStoryDAO.deleteByStoryId(storyId) and
            paragraphsDAO.deleteByStoryId(storyId))


# 获取 （润色文本， url， bool）
def getStory(storyId):
    # 获取 (绘画prompt， 润色文本， url)
    result, ok = paragraphsDAO.findByStoryId(storyId)
    if ok:
        texts = []
        urls = []
        for i in result:
            texts.append(i[1])
            urls.append(i[2])
        return texts, urls, True
    return None, None, False


# 重画当前页
# 返回值：新的url
def updateCurrentPicture(storyId, current):
    # res = 绘画prompt， 润色文本， url
    # 找到当前页的数据
    res, ok = paragraphsDAO.findByStoryId(storyId)
    res = res[current]
    if not ok:
        return None, False
    # 通过当前页的绘画prompt进行重画
    if current == 0:
        newPage = utils.roll_cover(res[0])
    else:
        newPage = utils.roll_pic(res[0])
    return newPage, paragraphsDAO.updateByStoryId(storyId, res[0], res[1], newPage, current)


# 大纲+用户指令重新制作，类似generateStory函数
# 返回故事id
def generateNewStory(userName, storyId, requirement):
    # 获取之前的故事大纲
    res, ok = totalStoryDAO.findByStoryId(storyId)
    if not ok:
        return None, False
    # 生成新的故事
    newStory, ok = utils.modify_flow(res[0], res[1], requirement)
    if not ok:
        return None, False
    # 生成新的故事Id
    newStoryId = time.time().__str__()
    # 添加新生成的故事
    ok = userStoryDAO.insert(userName, newStoryId) and totalStoryDAO.insert(newStoryId, newStory[0],
                                                                            newStory[1]) and paragraphsDAO.insert(
        newStoryId, newStory[2], newStory[3], newStory[4])
    if ok:
        # 删除原来的故事
        deleteStory(storyId)
        return newStoryId, True
    return None, False


# 获取用户所有的故事标题，故事封面
def getAllStory(userName):
    # 获取用户名下所有的故事id
    allStoryId, ok = userStoryDAO.findByUserName(userName)
    if not ok:
        return None, False
    storyId = []
    title = []
    cover = []
    for i in allStoryId:
        # 找到每个故事的标题、方面url
        res, ok = paragraphsDAO.findByStoryId(i)
        if not ok:
            return None, False
        storyId.append(i)
        title.append(res[0][1])
        cover.append(res[0][2])
    return [title, cover, storyId], True


outline1 = '创作一部有关爱冒险的小男孩的故事'
originalStory1 = '在一个美丽的小镇上，住着一位爱冒险的小男孩。他总是充满好奇心，渴望探索未知的世界。一天，他听说了一个神秘的洞穴，据说里面藏有宝藏。小男孩兴奋不已，他决定前往洞穴探险。他准备好了装备，包括手电筒、绳索和一些食物。他来到洞穴口，深吸一口气，然后开始了他的探险之旅。洞穴里漆黑一片，小男孩打开手电筒，小心翼翼地往前走。他遇到了许多困难，有时候需要爬过陡峭的岩壁，有时候需要穿过狭窄的通道。但他并没有放弃，他一直在前进，直到他找到了宝藏。宝藏里有各种各样的宝贝，包括宝石、金币和古老的文物。小男孩欣喜若狂，他觉得自己获得了无价之宝。他把宝藏带回家，和家人分享自己的冒险经历。这个故事告诉我们，只要有勇气和决心，我们就可以克服任何困难，实现自己的梦想。'
prompt1 = [
    '水彩风格 , 汤姆仰望天空的冒险之旅,小男孩汤姆的纯真眼神，对世界的好奇和渴望，开启冒险的勇敢之心,动画电影风格,采用明亮的色彩和灵动的线条，展现小男孩的勇气和冒险精神，以及他对世界的向往和好奇心。',
    '水彩风格 , 小男孩与洞穴深处的冒险,洞穴巨口与黑暗深邃，手电筒照亮前方，勇气和好奇心驱使着小男孩前行,以2D或3D手绘动画风格，使用柔和的色彩和明暗对比，展现洞穴内的神秘与未知，',
    '水彩风格 , 小男孩勇敢探险,手电筒照亮漆黑的洞穴,安静的洞穴中呼吸和脚步声,发现闪闪发光的宝石和金币的惊喜,动画电影风格,使用精细的动画和细致的声音设计来传达小男孩的内心戏和洞穴的神秘感，',
    '水彩风格 , 小男孩与晶莹剔透的宝石，宝石在阳光下的闪烁与小男孩的惊喜,小男孩感受大自然的力量,小男孩的兴奋与家人的分享,动画电影风格,使用明亮鲜艳的色彩和细腻的动画效果来表现宝石的魔法和小男孩的惊奇，',
    '水彩风格 , 小男孩攀爬巨大石门的冒险场景，石门上刻着神秘的符咒和闪着金色光芒的小洞，小男孩掏出金色奖杯的惊喜与鼓舞，动画电影风格，采用明亮的色彩和细致的纹理来创造一个充满奇幻和深意的场景，',
]
text1 = ['《小男孩的洞穴探险》',
         '在一个漂亮的小镇上，住着一个爱冒险的小男孩。他总是很好奇，想要发现新的东西。',
         '有个小男孩，听说了神秘的洞穴，想去探险。他准备好了装备，还有吃的。',
         '他来到洞穴口，深吸一口气，然后开始了探险之旅！洞穴里好黑啊，小男孩打开手电筒，小心地往前走。他遇到了好多困难，有时候要爬过陡峭的岩壁，有时候要穿过窄窄的通道。但他没有放弃，他一直在前进，最后找到了宝藏！',
         '宝藏里有好多漂亮的宝石和金闪闪的金币，还有古老的文物哦！小男孩开心极了，他找到了无价之宝！他迫不及待地回家告诉了家人自己的冒险故事。'
         ]
url1 = ['https://ai-painting-image.vivo.com.cn/ai-painting/763783fbad79a8422fac51f99346ae864b2817ae-0.jpg',
        'https://ai-painting-image.vivo.com.cn/ai-painting/763783fb3468b765640b5b46a6177e95f23c385e-0.jpg',
        'https://ai-painting-image.vivo.com.cn/ai-painting/763783fb355213eafc81539899fed659f2b2662e-0.jpg',
        'https://ai-painting-image.vivo.com.cn/ai-painting/763783fb9889a9d16d9957f0bcefdc7e4dc197d6-0.jpg',
        'https://ai-painting-image.vivo.com.cn/ai-painting/763783fbff9e979140b85d87b0c419d48b20877d-0.jpg'
        ]

outline2 = '创作一部有关爱冒险的小男孩的故事'
originalStory2 = '在一个美丽的小镇上，住着一位爱冒险的小男孩。他总是充满好奇心，渴望探索未知的世界。一天，他听说了一个神秘的洞穴，据说里面藏有宝藏。小男孩兴奋不已，他决定去探险。他准备好了装备，包括手电筒、绳索和一些食物。他告诉他的父母他的计划，并得到了他们的允许。小男孩来到洞穴口，开始了他的冒险之旅。洞穴里漆黑一片，他打开手电筒，小心翼翼地往里走。他看到了许多奇怪的石头和岩石，还有一些蝙蝠。他并不害怕，反而觉得很有趣。他越走越深，终于来到了一个宽敞的地方。他看到了一些箱子和罐子，里面装满了金币和珠宝。小男孩高兴极了，他知道他找到了宝藏。但他也知道，现在不是带走宝藏的时候。他决定先回到家里，和家人分享这个好消息。小男孩的冒险之旅让他更加勇敢和自信。他明白，只要我们勇敢地面对未知，我们就能发现更多的奇迹。',
prompt2 = [
    "水彩风格 , 小镇尽头冒险的少年,夕阳下奔跑的剪影,闪烁的眼睛和期待的心,插画风格,使用温暖柔和的色彩和细腻的线条来描绘小镇和少年的形象，",
    "水彩风格 , 小男孩的床边地图,明天探险的计划与决心,好奇心的驱动与勇敢面对未知,插画风格,运用温馨的色彩和可爱的角色设计来创造一个充满童趣和冒险精神的世界，",
    "水彩风格 , 小男孩的洞穴探险之旅,手持手电筒在黑暗洞穴中前行,形状颜色各异的石头和岩石,盘旋的蝙蝠和刺激的冒险,动态镜头语言,运用逼真的3D渲染和光影效果,展现出洞穴的奇妙和神秘，",
    "水彩风格 , 小男孩发现宝藏的惊喜瞬间,满箱满罐的金币和珠宝闪耀着光芒,他拿起珠宝的满足微笑,家庭分享喜悦的决定,插画风格,使用明亮的色彩和柔和的线条来营造一个充满温情和幸福的画面，",
    "水彩风格 , 小男孩手电筒下的五彩斑斓洞穴,探险者勇气和自信的身影,运用细腻的线条和丰富的色彩表现，结合生动的角色动画和音效设计，营造出神秘而又充满惊喜的探险场景。",
    "水彩风格 , 小男孩在洞穴中面对宝藏的挑战,手电筒照亮箱子和珠宝的瞬间,兴奋和好奇与谨慎和思考的眼神,留在原地的决定和等待未来的勇气,以细腻的插画风格绘制,用柔和的色彩和细节描绘来表达小男孩的情感和决定，",
]
text2 = ['《小男孩的探险之旅》',
         '在一个漂亮的小镇上，住着一个爱冒险的小男孩。他总是超级好奇，想要发现更多奇妙的事情！',
         '有个小男孩，听说了神秘的洞穴，想去探险。他准备好了装备，告诉了父母，就去了。',
         '小男孩探险啦！走到黑黑的洞穴，用手电筒照照，看见好多奇怪的石头和岩石，还有蝙蝠飞来飞去。他好开心哦！走啊走，终于来到一个大大的地方。',
         '他看到好多箱子和罐子，里面有好多金币和珠宝，小男孩好开心哦！他找到宝藏了！但他知道现在不能拿走，要先回家告诉家人这个好消息！',
         '小男孩去冒险啦！他很勇敢，很自信。他知道，只要勇敢面对未知，就会有很多奇迹出现。小男孩的探险真好玩！',
         ]
url2 = ['https://ai-painting-image.vivo.com.cn/ai-painting/763783fb5b5141615cfe5e428bfba989cb522d56-0.jpg',
        'https://ai-painting-image.vivo.com.cn/ai-painting/763783fbdf1187aa5e3a5c6eb49af7963b6dce0a-0.jpg',
        'https://ai-painting-image.vivo.com.cn/ai-painting/763783fbfe4e2d4d57a25a4eb561ef761f390c50-0.jpg',
        'https://ai-painting-image.vivo.com.cn/ai-painting/763783fbdbfc3443b3165fb18cfa80e69f403e47-0.jpg',
        'https://ai-painting-image.vivo.com.cn/ai-painting/763783fbef0233e34f765db680d90c3ea836a3b5-0.jpg',
        'https://ai-painting-image.vivo.com.cn/ai-painting/763783fb54c1996d81345316934900715c85b2cc-0.jpg'
        ]

outline3 = '啊这这这个这个都可以直接去自习课'
originalStory3 = '好的，我将为您提供一个故事大纲，您可以根据需要为角色命名。故事大纲：1. 描述一位学生在学校中遇到的学习挑战；2. 描述该学生如何通过自己的努力和寻求帮助，克服了这些挑战；3. 强调学习的重要性和自我努力的回报。'
prompt3 = [
    "水彩风格 , 安慰他的小狗,落寞的眼泪与舔舐的安慰,充满温情的画面,以插画风格绘制,使用柔和的色彩和细节描绘来表达小明与小狗之间的互动和情感交流，",
    "水彩风格 , 妈妈一同学习的温馨画面,书桌前的愁容和笔的转动,妈妈的出现和温柔安慰,插画风格,以温馨的色彩和细节描绘来表达小明和妈妈之间的亲密关系和学习的陪伴，",
    "水彩风格 , 小明在老师指导下专注学习,课本和笔记本整齐排列,眼神中充满对知识的渴望,插画风格,以清新明亮的色彩和细腻的线条勾勒出小明专注的神态和整齐的学习环境，",
    "水彩风格 , 着满分的试卷,脸上露出开心笑容，眼中闪烁着自信的光芒,展现他的自豪和喜悦,动画电影风格,使用明亮的色彩和细节描绘来表达小明对成功的自信和自豪，同时展示他的努力和成就。",
    "水彩风格 , 小兔子阅读的温馨画面,斑驳光影中的草地上，小兔子捧着书，羽毛笔不时在墨水瓶中蘸一下，在书边上做些笔记。树叶间的阳光洒在小兔子身上，映衬出专注而愉悦的表情,画面中采用柔和的色彩和自然的纹理，营造出一种和谐而宁静的氛围，数字动画风格，通过细致的角色动画和光影效果来呈现小兔子的生动形象。",
]
text3 = ['《学习的勇气》',
         '小明是个棒棒的学生，可数学成绩下降让他难过。',
         '小明学数学，遇到了困难，尝试解决，却越做越错，让他很无助。',
         '小明不放弃，他去问老师，上补习班，还请了家教。他努力学习，虽然辛苦，但他相信自己能行！',
         '小明努力学习，数学成绩越来越好！他变得更自信勇敢了！'
         ]
url3 = ['https://ai-painting-image.vivo.com.cn/ai-painting/763783fb30e7b0b125385cb4b93f4f04e9beacbe-0.jpg',
        'https://ai-painting-image.vivo.com.cn/ai-painting/763783fb8f21d0138fa65f44ad0fbaf1986b22e7-0.jpg',
        'https://ai-painting-image.vivo.com.cn/ai-painting/763783fb020b7cd4e0975fb98c4ac509c168d19d-0.jpg',
        'https://ai-painting-image.vivo.com.cn/ai-painting/763783fb4ed7bbc1c35e581997368f818621c061-0.jpg',
        'https://ai-painting-image.vivo.com.cn/ai-painting/763783fbd654f49a9deb58de8265fed4bbda8714-0.jpg'
        ]

outline4 = '奇迹暖暖的时候。我们的歌谣哈哈哈哈哈'
originalStory4 = '''题目：春天的新装
暖暖是一个热爱生活的小女孩，她喜欢尝试各种不同的衣服，搭配出自己的风格。春天来了，暖暖决定为自己准备一些新的春装。

一天，暖暖和妈妈一起去了商场，看到了各种漂亮的春装。暖暖的眼睛都看花了，她试了一件又一件，每一件都让她觉得自己变得更漂亮了。最后，她挑选了几件自己最喜欢的衣服，高高兴兴地和妈妈回家了。

回到家，暖暖立刻开始试穿新衣服。第一件是一件淡绿色的连衣裙，上面绣着漂亮的小花，非常清新。第二件是一件粉色的短袖衬衫，上面印着彩色的图案，非常可爱。第三件是一件黄色的外套，上面有一些小动物的图案，非常有趣。暖暖穿上这些新衣服，觉得自己变得更美更好了。

晚上，暖暖和爸爸妈妈一起去公园散步。暖暖穿上新衣服，感觉自己像一个小公主一样。她走在路上，看到了许多美丽的花朵和树木，觉得春天真是太美好了。她一边走，一边唱着歌谣，心情格外愉快。

暖暖喜欢自己的新衣服，也喜欢春天的美好。她决定要好好珍惜这一切，让自己的生活变得更加美好。'''
prompt4 = [
    "水彩风格 , 色的春装和暖暖置身于美丽童话世界的感觉，商场中热闹的人群和缤纷的色彩，使用鲜艳的色彩和活泼的动画效果，展现出春季的清新和活力。",
    "水彩风格 , 斓的童话世界,暖暖穿上春装成为小公主,洋溢幸福微笑的美好春天,插画风格,采用明亮鲜艳的色彩和细腻的线条勾勒出暖暖和妈妈的形象，以及五彩缤纷的春装，营造出一个充满童趣和幸福感的画面。",
    "水彩风格 , 暖暖的穿衣镜前，淡绿色连衣裙与小花绣，眼睛里的欣喜，插画风格，利用清新明亮的色彩和精致的线条勾勒出暖暖的形象，展现出她青春和幸福的情感。",
    "水彩风格 , 暖暖在春天公园中的欢快行走,穿淡绿色绣花连衣裙的小公主,闪烁的眼睛和兴奋的光芒,路边花朵和树木散发的清新气息,插画风格,采用明亮温暖的色彩和精细的线条勾勒来表现春天的美好和暖暖的幸福之感,",
    "水彩风格 , 暖暖在公园中穿着新衣服跳舞,裙摆盛开的花朵,周围小鸟和蝴蝶的欢快飞舞,插画风格,使用鲜艳的色彩和柔和的线条来创造一个充满生机和幸福的场景，",
]
text4 = ['《春天的新装》',
         '暖暖是个爱美的小女孩，春天来了她想穿新衣服。',
         '暖暖和妈妈去商场买春装了，看到了好多漂亮衣服，试了又试，最后选了自己最喜欢的几件回家啦！',
         '回家后，暖暖迫不及待地试穿新衣服啦！第一件是淡绿的花朵裙，好漂亮啊！第二件是粉色的印花衬衫，超级可爱！第三件是黄色的动物外套，太好玩了！暖暖穿得美美哒，开心极了！',
         '晚上，暖暖和爸爸妈妈去公园散步了！暖暖穿了新衣服，觉得自己像小公主一样。她看到了许多美丽的花朵和树木，觉得春天真是太美好了！她一边走，一边唱着歌谣，心情格外愉快。', ]
url4 = ['https://ai-painting-image.vivo.com.cn/ai-painting/763783fbced4077c443f5abba11aa5993e067454-0.jpg',
        'https://ai-painting-image.vivo.com.cn/ai-painting/763783fbe19750a8f8085238af3c367180cf88a5-0.jpg',
        'https://ai-painting-image.vivo.com.cn/ai-painting/763783fbb9060b6487295da1b256acaa96d919ec-0.jpg',
        'https://ai-painting-image.vivo.com.cn/ai-painting/763783fbda252c83f7be51839e0acc1940bd6bab-0.jpg',
        'https://ai-painting-image.vivo.com.cn/ai-painting/763783fbe398c5637084527baa11413887aea9df-0.jpg',
        ]

outline5 = '爱学习的小男孩'
originalStory5 = '''小男孩自习课酷酷学框框学

小男孩自习课酷酷学框框学，他是一个热爱学习的孩子。在学校里，他总是认真地听老师讲课，课后也会认真完成作业。在家里，他常常会看书、做题，甚至会自己研究一些有趣的科学实验。

一天，学校组织了一次自习课，让学生们自由复习和预习。小男孩非常兴奋，他认为这是一个很好的机会，可以更加专注地学习。他早早地来到教室，准备开始自习。

小男孩首先把课本拿出来，认真地看了起来。他一边看，一边做笔记，很快就掌握了新的知识点。接着，他又拿出了一些练习册，开始做题。他沉醉在学习中，仿佛忘记了周围的一切。

不知不觉，自习课结束了。小男孩看了看窗外，发现天已经黑了。他惊讶地发现，他已经学习了整整一节课，而且学得非常充实。他感到非常满足，同时也感到非常自豪。

小男孩的自习课经历告诉我们，学习是一件非常有意义的事情。只要我们用心去学，就一定会有所收获。同时，学习也需要坚持和耐心，只有不断地努力，才能取得更好的成绩。'''
prompt5 = ['提示词：小男孩，自习课，课本，笔记，练习册，学习，充实，自豪，坚持，耐心，成绩，水彩风格。',
           "水彩风格 , 专注学习,聪明眼眸与窗外阳光相映,激励学习的温馨场景,动画电影风格,采用明亮柔和的色彩和细节描绘来表达小男孩对学习的热爱和对未来的期望，",
           "水彩风格 , 的教室学习时光,书页间跳跃的五彩笔记,窗外阳光洒在脸上的温暖,认真坚定的眼神,动画电影风格,采用明亮的色彩和灵动的线条来表现小男孩的学习场景，让观众感受到知识和希望的力量。",
           "水彩风格 , 专注阅读课本,探索知识的海洋,聪明的光芒和不停书写的笔,时间流逝与光明未来的期待,动画电影感,使用生动丰富的色彩和细节刻画来表现小男孩对知识的渴望和专注，以及他对未来的向往和期待。",
           "水彩风格 , 的自习课与星空畅想,夜色中的窗景与闪烁的星光，纸上的笔触和满天的收获，温馨的氛围和宁静的夜晚，动画电影构图，运用柔和的色彩和细节描绘来表达小男孩对知识的渴望和对未来的憧憬，",
           "水彩风格 , 在教室里专注学习,书桌上洒满阳光,认真脸庞沉浸在知识海洋,时间流逝被遗忘,动画电影构图,利用明亮的色彩和细节描绘来表达小男孩对知识的热爱和对未来的憧憬，",
           "水彩风格 , 独自坐在教室里,窗外微弱的灯光,照亮了手中的书本,专注读书和低头做笔记,宁静温暖的学习氛围,动画电影构图,使用柔和的色彩和细致的线条来创造一个充满温情和专注力的场景，"
           ]
text5 = ['《小男孩努力学习的成长历程》',
         '有个孩子，他很喜欢学习！在学校他听得认真，回家后还做很多练习。他还喜欢看书、做实验，真的很棒呢！',
         '一天，学校组织了一次自习课，让学生们自由复习和预习。小男孩很兴奋，觉得可以更专心学习。他早早来到教室，准备开始自习。',
         '小男孩拿起课本，认真看呀看，一边看一边做笔记，很快就学会了新知识！他又拿出了练习册，开始做题，学习让他好开心，好像周围一切都消失了。',
         '哎呀，小男孩不知不觉中上完了一节自习课！他抬头一看，天已经黑了。他惊讶地发现，他已经学到了好多东西，感觉棒极了！他感到很满足，也很自豪。',
         '小男孩的自习课经历告诉我们，学习很有趣哦！只要我们认真学习，就能学到很多东西。学习需要耐心和努力，这样我们才能成为学习的小能手！',
         '小男孩酷酷学框框学，喜欢学习就成功！'
         ]
url5 = ['https://ai-painting-image.vivo.com.cn/ai-painting/763783fb63a3e6c3655b5f63bb74100da3a3bad0-0.jpg',
        'https://ai-painting-image.vivo.com.cn/ai-painting/763783fb5b544267569c5e60bd4daef2dfd49784-0.jpg',
        'https://ai-painting-image.vivo.com.cn/ai-painting/763783fb3b1d7e60f88f5a098d52c935a721be09-0.jpg',
        'https://ai-painting-image.vivo.com.cn/ai-painting/763783fbf0dea62eef325ebea0ca7d9508746917-0.jpg',
        'https://ai-painting-image.vivo.com.cn/ai-painting/763783fbe5d80673153a598193331e8857e0a592-0.jpg',
        'https://ai-painting-image.vivo.com.cn/ai-painting/763783fb9b9ff7910b47577c9657b30002408860-0.jpg',
        'https://ai-painting-image.vivo.com.cn/ai-painting/763783fb7897673a69135dd3b5c03e8202d2cc26-0.jpg',
        ]

outline6 = '创作一部有关爱冒险的小男孩的故事'
originalStory6 = '在一个美丽的小镇上，住着一位爱冒险的小男孩。他总是充满好奇心，想要探索未知的世界。一天，他听说了一个神秘的洞穴，据说里面藏有宝藏。小男孩兴奋不已，他决定要去探险。他准备好了装备，包括手电筒、绳索和一些食物。他向家人告别，开始了他的冒险之旅。小男孩来到洞穴口，他用手电筒照进去，发现里面黑漆漆的，他有些害怕。但他想起了他的初衷，他要坚持下去。他慢慢地爬进洞穴，他发现这里的石头很滑，他需要小心谨慎地前行。他走了很久，终于看到了一道光亮，他加快了脚步，来到了一个宽敞的地方。他发现这里有一堆石头，他用手推开石头，发现下面有一扇门。他打开门，发现里面有一间房间，房间里有很多箱子。他打开了其中一个箱子，里面装满了金币和宝石。他感到非常兴奋，但他也知道，这些财宝并不属于他，而是属于其他人。他决定把财宝留在原地，他在离开洞穴之前，留下了他的感谢和尊重。小男孩回到家后，他告诉了他的家人他的冒险经历。他学到了很多东西，他知道了什么是勇气和坚持，他也知道了什么是尊重和感激。这次冒险之旅，让他变得更加成熟和聪明。'
prompt6 = [
    '''提示词：- 标题：《小男孩的探险之旅》- 艺术家：水彩画师- 场景：一个美丽的小镇，一个神秘的洞穴，一个宽敞的房间- 角色：小男孩- 风格：水彩画风，清新自然，温暖治愈- 细节：洞穴里的石头很滑，小男孩需要小心谨慎地前行；房间里有许多箱子，其中一个箱子里装满了金币和宝石；小男孩留下感谢和尊重，体现出他的善良和诚实。''',
    "水彩风格 , 小镇尽头的好奇小男孩,灿烂笑容和闪闪发光的眼睛,无尽冒险精神,手绘风格,采用清新的色彩和柔和的线条来创造一个充满童趣和梦想的场景，",
    "水彩风格 , 小男孩的探险之旅,手电筒照亮前行的道路,绳索克服崎岖地形,美味食物提供动力,动画电影构图,采用明亮的色彩和细致的线条描绘来表达小男孩的勇气和决心，同时表现出他在旅途中的艰辛和挑战，",
    "水彩风格 , 小男孩在洞穴中的冒险,手电筒照亮黑暗的洞穴,初心的坚持与勇气,石壁上的细微水流和凹凸不平的地面,光亮的出口和加速的脚步,冒险与探索的氛围,采用逼真的场景建模和细致的渲染技术来营造一个充满未知和挑战的洞穴环境。",
    "水彩风格 , 小男孩与箱子里的宝藏,金光闪闪的宝石映照着整个房间,男孩的坚定表情和感恩之心,电影画面感,以精细的细节描绘和光线效果来表现宝石的光芒和男孩的情感变化，",
    "水彩风格 , 小男孩的冒险故事,讲述时的眉飞色舞和家人们的专注倾听,亲情和爱的氛围,运用生动的角色表情和温馨的色调，将观众带入一个充满家庭温暖和关爱的场景之中。",
    "水彩风格 , 推开石头的瞬间,看到光亮的欣喜和希望,代表好奇与勇气的美好时刻,动画电影感,运用鲜艳的色彩和流畅的动画效果来表现小男孩的欣喜和希望，同时刻画出他挑战未知的勇气和决心。"
]
text6 = ['《探险之旅》',
         '在一个美丽的小镇上，住着一位勇敢的小男孩。他总是充满好奇心，想要探险。',
         '一天，他听说了神秘的洞穴，里面有宝藏哦！小男孩兴奋极了，他准备好了装备，向家人告别，开始了他的冒险之旅。',
         '小男孩来到洞穴口，用手电筒往里照，黑漆漆的，他有点害怕。但他想起初衷，决定继续前进。洞里的石头很滑，他小心翼翼地往前走。走了很久，终于看到一道光亮，他加快脚步，来到了一个宽敞的地方。',
         '小孩子，我告诉你一个故事。有个人发现一堆石头，下面有扇门。门里有个房间，里面有好多箱子。他打开一个箱子，里面全是金币和宝石！但他知道，这些财宝不是他的。他留下了感谢和尊重，离开了那个洞穴。',
         '小男孩回到家后，他告诉了家人他的冒险故事。他学到了很多东西，比如勇气和坚持，还有尊重和感激。这次旅行让他变得更聪明更成熟！',
         '小男孩的故事教我们勇敢面对困难，坚持到底。感谢和尊重也很重要哦！'
         ]
url6 = ['https://ai-painting-image.vivo.com.cn/ai-painting/763783fb0dbac003ddf05a888f4ae2df3ec8f8f2-0.jpg',
        'https://ai-painting-image.vivo.com.cn/ai-painting/763783fbcb2b64bb1e5e59ae93d7e19f40f9cb84-0.jpg',
        'https://ai-painting-image.vivo.com.cn/ai-painting/763783fbd2e35a79853d5db1a12bdf3004bd442c-0.jpg',
        'https://ai-painting-image.vivo.com.cn/ai-painting/763783fb7444f8f3dbd75e02880240c90c1e76dc-0.jpg',
        'https://ai-painting-image.vivo.com.cn/ai-painting/763783fba4b273d5a5365b06833b458161fa4c63-0.jpg',
        'https://ai-painting-image.vivo.com.cn/ai-painting/763783fbc33914dcfac85111a95ea68cfb1a5a10-0.jpg',
        'https://ai-painting-image.vivo.com.cn/ai-painting/763783fbf6f760330963557b91796a6ed35689e1-0.jpg'
        ]

outline7 = '创作一部爱读书的小男孩的故事'
originalStory7 = '在一个小城镇里，住着一位爱读书的小男孩。他住在一间小小的房子里，屋子里堆满了书。每天晚上，当其他孩子在外面玩耍时，他总是会坐在窗边，静静地阅读。有时候，他会读到很晚，但他从来不觉得疲倦。他的父母经常劝他早点睡觉，但他说他不想停下来。他说，书中的世界是如此神奇，他总是能在书中找到乐趣和启示。他的老师也很喜欢他，说他是一个聪明而勤奋的学生。他会认真听讲，做好每一道题目。他的同学们也很羡慕他，说他是一个真正的读书人。他的爱好也影响了他的朋友，他们也开始读书。他说，阅读是一种美好的享受，希望大家都能享受到这种乐趣。这个故事告诉我们，阅读是一种美好的习惯，它能带给我们知识，启迪我们的思想。我们应该像这位小男孩一样，热爱读书，不断学习，不断进步。'
prompt7 = ['提示词：一个男孩，坐在一堆书旁，窗外是城镇的景色，水彩画风，柔和色调，细节丰富，印象派风格。',
           "水彩风格 , 小男孩夜晚阅读的宁静场景,窗外朦胧夜景与窗内温暖灯光的对比,专注而好奇的眼神,洋溢满足和喜悦的面容,采用细腻的线条和柔和的色彩来表现这个场景，强调温暖和舒适的氛围，让观众感受到阅读所带来的美好体验。",
           "水彩风格 , 专注阅读的神情,被书本吸引的表情,月光洒在他身上的静谧氛围,动态的画面,使用柔和的色彩和精细的线条来描绘小男孩的阅读场景,并运用月光和环境音效来营造宁静的氛围。",
           "水彩风格 , 聪明勤奋的学生形象,课堂上的认真听讲和精准回答,沉浸在书海中的读书人,动画电影风格,利用明亮的色彩和细节描绘来表达这位学生的聪明才智和对知识的热爱，",
           "水彩风格 , 和朋友们沉浸在阅读的世界中,窗外阳光洒在脸上，映照出认真阅读的表情，微笑和皱眉的变化，展现了他们完全沉浸在书中的情景，动画电影感，通过细腻的面部表情和温馨的色调，表达出阅读所带来的美好感受和乐趣。",
           "水彩风格 , 小男孩与书海共眠,卧室墙上满是书架，堆满了他最爱的书，小男孩躺在床上，沉浸在书中的世界，幸福的微笑洋溢在他的脸上，父母温馨的催促，散发着家的温暖和舒适，动画电影风格，采用柔和的色彩和细节描绘来表达小男孩对书的热爱和家庭的温馨，",
           ]
text7 = ['《小城镇的读书人》',
         '在一个小镇上，有个爱看书的小男孩。他喜欢在晚上坐在窗边看书，而不是出去玩。',
         '他很喜欢读书，经常读到很晚。他的父母叫他早点睡觉，但他总是停不下来。因为他觉得书里的世界太神奇了，每次都能找到新的乐趣和启示。',
         '他的老师可喜欢他了！因为他聪明又勤奋，上课听得认真，作业做得棒棒的。他的同学们都羡慕他，说他是个真正的读书人。',
         '他喜欢读书，朋友也跟着读。读书好开心，大家一起来吧！',
         '这个故事告诉我们，读书是一件很棒的事情！我们可以学到很多知识，变得更聪明。就像这个小男孩一样，我们要爱读书，不断学习哦！'
         ]
url7 = ['https://ai-painting-image.vivo.com.cn/ai-painting/763783fb8303b1b8ed2f54bf932487969ad511d9-0.jpg',
        'https://ai-painting-image.vivo.com.cn/ai-painting/763783fb5a3e1d6df21a52e4b5fcf37806cbf2eb-0.jpg',
        'https://ai-painting-image.vivo.com.cn/ai-painting/763783fbd6bf6deda7f5510ba6509d49bd474b71-0.jpg',
        'https://ai-painting-image.vivo.com.cn/ai-painting/763783fb4ced4ee909815cc897c1e827a76dca99-0.jpg',
        'https://ai-painting-image.vivo.com.cn/ai-painting/763783fb202a7e619444595c9d6ddd8355652693-0.jpg',
        'https://ai-painting-image.vivo.com.cn/ai-painting/763783fbcd7faf90b99151238bc1d5d840599c54-0.jpg',
        ]

outline8 = '创作一部爱读书的小男孩的故事'
originalStory8 = '在一个小城镇里，住着一位热爱阅读的小男孩。他住在一间陈旧的小屋里，但他的心中却有一个广阔的世界，这个世界是由书本为他打开的。小男孩每天都会去图书馆，借阅各种类型的书籍。他喜欢读科学、历史、文学，甚至是哲学。他总是沉迷在书中的世界，忘记时间的流逝。他的父母并不理解他的爱好，他们认为读书浪费时间，不如去学习实用的技能。但小男孩并不在意，他仍然坚持自己的兴趣。一天，小男孩借到了一本关于天文学的书，书中详细介绍了宇宙的形成、行星的运行等等。小男孩被这些知识深深地吸引住了，他开始对天文学产生了浓厚的兴趣。他开始自学数学、物理，希望能够更深入地了解这个神秘的宇宙。几年后，小男孩成为了一名杰出的天文学家，他的研究成果在世界范围内引起了轰动。他的父母终于理解了他的兴趣，也为他感到骄傲。小男孩的成功告诉我们，只要我们坚持自己的兴趣，不断学习、探索，就一定能够取得成功。阅读是一种宝贵的习惯，它能够为我们打开一扇通往广阔世界的大门。'
prompt8 = [
    '提示词：一个男孩，陈旧的小屋，图书馆，书本，世界，科学，历史，文学，哲学，天文学，宇宙，行星，数学，物理，神秘，成功，阅读，水彩风格。',
    "水彩风格 , 杰克眺望远山,向往未知世界的眼神,森林与山峰的壮阔景观,穿越与攀登的想象之旅,采用宽广的镜头视角和逼真的自然景观渲染来展现杰克内心的冒险精神，",
    "水彩风格 , 杰克兴奋摊开神秘地图,仔细研究每一个标记，手指沿着地图上的路线滑动,下定决心踏上寻宝之旅，电影画面感,使用强烈的色彩和细节描绘来表现杰克的兴奋和决心,以及地图的神秘和冒险气息，",
    "水彩风格 , 杰克与小松鼠在森林中奔跑，小松鼠在树枝间穿梭，杰克紧随其后。小松鼠停在树枝上，杰克停下来，拿出纸和笔画迷宫。小松鼠看到迷宫，跃跃欲试，迅速找到出口。杰克高兴地抱起小松鼠，感谢它的帮助。动画电影风格，采用清新明亮的色彩和灵动的画面效果，呈现森林中的欢乐和友谊。",
    "水彩风格 , 杰克回乡赠予孩子们遗产,杰克脸上洋溢着自信和勇气，他回到家乡，看到那些孩子们，心里充满了感慨。他将遗产分给了每个孩子，并用自己的经历告诉他们，只要有勇气和智慧，就能够克服困难，实现梦想。他激励了所有的孩子，让他们明白了阅读的重要性。运用温暖的色调和细致的线条，描绘出杰克和孩子们之间的动人情感，以及孩子们在阅读中的成长和变化。",
    "水彩风格 , 杰克站在山顶上，眺望无垠大海,紧握父亲留下的地图,希望与勇气充满内心,踏上寻宝之旅,动画电影风格,运用宽广的视角和细致的情感描绘，展现杰克坚定前行的决心和勇气，",
]
text8 = ['《杰克的奇幻之旅》',
         '从前，有个男孩叫杰克，他喜欢冒险。他想去找神秘的地方。',
         '杰克发现了一张神秘的地图，上面有一条通往未知领域的路线。他决定去探险寻宝！',
         '杰克走过森林，遇见了聪明的小松鼠，在沙漠里遇见神秘的骆驼，它告诉杰克通往宝藏的秘密。最后，杰克来到山峰上的城堡，遇见神秘的老人，老人告诉他宝藏是一份珍贵的遗产，需要勇气和智慧去保护。',
         '杰克回家了，他好勇敢好聪明！孩子们都好喜欢他。',
         '杰克的故事告诉我们，最宝贵的财富是梦想和勇气。只要勇敢追梦，就能找到宝藏！',
         ]
url8 = ['https://ai-painting-image.vivo.com.cn/ai-painting/763783fb306a907945f459ccbf335fd686e47aa4-0.jpg',
        'https://ai-painting-image.vivo.com.cn/ai-painting/763783fb736c4708bdac5da8b0e0e40d938bff8d-0.jpg',
        'https://ai-painting-image.vivo.com.cn/ai-painting/763783fb42d8468369775ebda9a887c560b1bd0a-0.jpg',
        'https://ai-painting-image.vivo.com.cn/ai-painting/763783fb819974dbba0b5891bb802c7545d1271a-0.jpg',
        'https://ai-painting-image.vivo.com.cn/ai-painting/763783fb11c4209ee8b1524eac0d58edec6de404-0.jpg',
        'https://ai-painting-image.vivo.com.cn/ai-painting/763783fb5b904e4bf62155078efe817c7b6473be-0.jpg',
        ]

outline9 = '创作一部爱读书的小男孩的故事'
originalStory9 = '在一个小城镇里，住着一位爱读书的小男孩。他总是怀揣着书，无论是走在路上，还是坐在公园里，总是手不释卷。他的房间里堆满了各种各样的书籍，从童话故事到历史传记，从科幻小说到文学经典，他涉猎广泛，乐此不疲。他的父母一开始并不理解他的爱好，认为他应该多出去和同龄人玩耍。然而，小男孩并没有因此而放弃自己的兴趣。他依然每天坚持阅读，不断丰富自己的知识储备。渐渐地，他的父母也被他的热情所感染，开始支持他的爱好。小男孩的阅读面越来越广，他的思维也越来越开阔。他开始尝试写作，将自己的想法和感受记录下来。他的作品得到了老师和同学们的赞赏，他也因此变得更加自信和勇敢。小男孩的成长之路充满了书香，他通过阅读，拓宽了自己的视野，丰富了自己的生活。他明白了知识的力量，也体会到了阅读的乐趣。'
prompt9 = [
    "提示词：- 一个男孩，他手拿一本书，坐在公园的长椅上，背景是小镇的房屋和树木- 柔和的色调，水彩风格- 细节丰富，包括男孩的表情、书籍的封面、公园的景色等 - 强调阅读的主题，可以通过书脊上的文字、书的摆放方式等方式呈现- 画面中可以加入一些小动物或昆虫，增加趣味性- 标题《书香小镇》以流畅的字体呈现在画面上方或下方，颜色与画面相协调",
    "水彩风格 , 小男孩在公园里阅读的场景,长椅上阳光和微风的交织,沉浸在书的海洋中的专注,父母的不同意见,细腻的线条和柔和的色彩勾勒出小城镇的温馨氛围，同时通过小男孩的动作和表情展现他对阅读的热爱和坚持。",
    "水彩风格 , 的房间与知识的海洋,五彩斑斓的书籍堆砌在书架上，桌子上，甚至地上，小男孩在其中静静地阅读着,阳光透过窗户洒在书页上，映照出他专注而满足的面容，动画电影感，运用柔和的色彩和细致的细节描绘来展现小男孩与知识的互动，",
    "水彩风格 , 专注阅读的画面,书页翻动的声音和沉浸在书中的表情,父母的欣慰和支持,使用柔和的色彩和细致的线条来描绘小男孩和书本的细节,同时通过摄影的角度和光影处理来营造温馨和谐的氛围,",
    "水彩风格 , 专注写作的场景,温馨的光照和书架环绕,父母的骄傲与欣慰,儿童绘本风格,采用柔和的色彩和可爱的形象设计来创造一个充满童趣和温馨氛围的场景，",
    "水彩风格 , 的作品展示与成就感,班级展示中的赞赏与自信骄傲,决定继续努力的决心与憧憬,动画电影风格,采用明亮鲜艳的色彩和生动的角色动作来表达小男孩的成就感和自信心，同时刻画他对于创作的热爱和追求。",
    "水彩风格 , 与书的奇妙之旅,专注的神情和探索的光芒,照亮他的暖阳和身旁陪伴的小猫,阅读带来的快乐和满足,动画电影构图,使用柔和的色彩和细腻的线条勾勒出童趣和温馨的氛围，表达阅读带来的美好和力量。",
]
text9 = ['《书香小镇》',
         '在一个小镇上，住着一个爱看书的小男孩。他总是带着书，不论是在路上还是公园里，总是不离手。',
         '他的房间里有很多书，有好多好多故事呢！',
         '小男孩很喜欢阅读，但他的父母不理解。他还是每天坚持，看了很多书，学到了很多知识。',
         '小男孩非常喜欢阅读，他的父母也被他的热情所感染，开始支持他的爱好。他读了很多书，思维变得越来越开阔。他也开始写作，记录自己的想法和感受。',
         '小男孩的作品被大家夸奖了，他变得更自信和勇敢！他爱读书，通过读书，他看到了更多的世界，过上了更精彩的生活。',
         '小男孩爱读书，他发现知识的力量很大，阅读也很有趣。我们都要像他一样爱读书哦！',
         ]
url9 = ['https://ai-painting-image.vivo.com.cn/ai-painting/763783fbf4f8a683b7e654afba026d0305b9fb4a-0.jpg',
        'https://ai-painting-image.vivo.com.cn/ai-painting/763783fb4db3c0ffdbb5566ea8a82e89c27267be-0.jpg',
        'https://ai-painting-image.vivo.com.cn/ai-painting/763783fb2a796e3a55d95fd1b8b13c8b6ddfa4fb-0.jpg',
        'https://ai-painting-image.vivo.com.cn/ai-painting/763783fb5d718bdcafb85aafadc4c55f7ba69b56-0.jpg',
        'https://ai-painting-image.vivo.com.cn/ai-painting/763783fb85983bf5a218578cb4e5f187fe8d2bb8-0.jpg',
        'https://ai-painting-image.vivo.com.cn/ai-painting/763783fb00d83b50983c5d11bf08c04e3c6d2fda-0.jpg',
        'https://ai-painting-image.vivo.com.cn/ai-painting/763783fb27ab8c14717152649b9ca8f2fa1b0998-0.jpg'
        ]


# 初始化默认绘本
def initUserStory(userName):
    ok = initStory(userName, time.time().__str__(), outline1, originalStory1, prompt1, text1, url1)
    ok = ok and initStory(userName, time.time().__str__(), outline2, originalStory2, prompt2, text2, url2)
    ok = ok and initStory(userName, time.time().__str__(), outline3, originalStory3, prompt3, text3, url3)
    ok = ok and initStory(userName, time.time().__str__(), outline4, originalStory4, prompt4, text4, url4)
    ok = ok and initStory(userName, time.time().__str__(), outline5, originalStory5, prompt5, text5, url5)
    ok = ok and initStory(userName, time.time().__str__(), outline6, originalStory6, prompt6, text6, url6)
    ok = ok and initStory(userName, time.time().__str__(), outline7, originalStory7, prompt7, text7, url7)
    ok = ok and initStory(userName, time.time().__str__(), outline8, originalStory8, prompt8, text8, url8)
    ok = ok and initStory(userName, time.time().__str__(), outline9, originalStory9, prompt9, text9, url9)
    return ok


def initStory(userName, storyId, outline, originalStory, prompt, text, url):
    ok = userStoryDAO.insert(userName, storyId, 'yes')
    ok = ok and totalStoryDAO.insert(storyId, outline, originalStory)
    ok = ok and paragraphsDAO.insert(storyId, prompt, text, url)
    return ok
