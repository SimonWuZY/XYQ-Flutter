import asyncio
import concurrent.futures
import logging
import os
import time
import uuid
from http import HTTPStatus
from typing import Optional

import requests
from dotenv import load_dotenv

from tools.auth_util import *

from dashscope import ImageSynthesis
from langchain_core.language_models import LLM
from openai import OpenAI

import tools.tmpCache
from tools.xyqStoryUtils import prompt

load_dotenv()

DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
DEEPSEEK_BASE_URL = 'https://api.deepseek.com'
MOONSHOT_API_KEY = os.getenv('MOONSHOT_API_KEY')
MOONSHOT_BASE_URL = "https://api.moonshot.cn/v1"
DASHSCOPE_API_KEY = os.getenv('DASHSCOPE_API_KEY')

demoPrompt = "近景镜头，18岁的中国女孩，古代服饰，圆脸，正面看着镜头，民族优雅的服装，商业摄影，室外，电影级光照，半身特写，精致的淡妆，锐利的边缘。"

# vivo蓝心模型相关配置
BLUE_LM_APP_ID = '2025384457'
BLUE_LM_API_KEY = 'jdjqtVSKvSznkEgM'
BLUE_LM_URL = '/vivogpt/completions'
BLUE_LM_DOMAIN = 'api-ai.vivo.com.cn'


# 蓝心模型接口
# def prompt_LLM(general_prompt: str, message_mode: bool = False) -> str:
#     params = {
#         'requestId': str(uuid.uuid4()),
#     }
#
#     if message_mode:
#         data = {
#             'message': general_prompt,
#             'model': 'vivo-BlueLM-TB-Pro',
#             'sessionId': str(uuid.uuid4()),
#             'extra': {
#                 'temperature': 0.7
#             }
#         }
#     else:
#         data = {
#             'prompt': general_prompt,
#             'model': 'vivo-BlueLM-TB-Pro',
#             'sessionId': str(uuid.uuid4()),
#             'extra': {
#                 'temperature': 0.7
#             }
#         }
#     headers = gen_sign_headers(BLUE_LM_APP_ID, BLUE_LM_API_KEY, 'POST', BLUE_LM_URL, params)
#     headers['Content-Type'] = 'application/json'
#     url = 'https://{}{}'.format(BLUE_LM_DOMAIN, BLUE_LM_URL)
#     response = requests.post(url, headers=headers, json=data, params=params)
#
#     if response.status_code != HTTPStatus.OK:
#         print(response.status_code, response.text)
#         return response.text
#     else:
#         res_obj = response.json()
#         if res_obj['code'] == 0 and res_obj.get('data'):
#             content = res_obj['data']['content']
#             return content
#         return ""


# def prompt_LLM(general_prompt: str, message_mode: bool = False) -> str:
#     """
#     Post a single prompt to LLMs
#     向大模型发送prompt
#
#     Args:
#         general_prompt (string): any prompt
#         message_mode (bool, optional): prompt message是否是正确的格式
#
#     Returns:
#         str: the response content of the LLMs
#     """
#     client = OpenAI(
#         api_key=DEEPSEEK_API_KEY,
#         base_url=DEEPSEEK_BASE_URL
#     )
#
#     if message_mode:
#         response = client.chat.completions.create(
#             model="deepseek-chat",
#             messages=general_prompt,
#             stream=False  # True if implemented
#         )
#     else:
#         response = client.chat.completions.create(
#             model="deepseek-chat",
#             messages=[
#                 # {"role": "system", "content": ""},
#                 {"role": "user", "content": general_prompt}
#             ],
#             stream=False  # True if implemented
#         )
#
#     print(response)
#     response = response.choices[0].message.content
#     print(response)
#     return response

def prompt_LLM(general_prompt: str, message_mode: bool = False) -> str:
    """
    Post a single prompt to LLMs
    向大模型发送prompt

    Args:
        general_prompt (string): any prompt
        message_mode (bool, optional): prompt message是否是正确的格式

    Returns:
        str: the response content of the LLMs
    """
    client = OpenAI(
        api_key=MOONSHOT_API_KEY,
        base_url=MOONSHOT_BASE_URL
    )

    if message_mode:
        response = client.chat.completions.create(
            model="moonshot-v1-32k",
            messages=general_prompt,
            stream=False  # True if implemented
        )
    else:
        response = client.chat.completions.create(
            model="moonshot-v1-32k",
            messages=[
                # {"role": "system", "content": ""},
                {"role": "user", "content": general_prompt}
            ],
            stream=False  # True if implemented
        )

    print(response)
    response = response.choices[0].message.content
    print(response)
    return response


def create_story(question: str) -> str:
    """
    Create a story through LLMs with the given question
    创建完整的故事

    Args:
        question (str): the input question
            for example: 创作一部名为《小象的善良之旅》的儿童故事。故事的主人公，小象总是刻意去帮助她的动物朋友们，尽管他们并不总是友善。

    Returns:
        str: the story created by LLMs
    """
    story_prompt = prompt.story_prompt(question)
    story = prompt_LLM(story_prompt)

    return story


def create_story_red_ver(question: str) -> str:
    """
    Create a story through LLMs with the given question
    创建完整的故事

    Args:
        question (str): the input question
            for example: 创作一部名为《小象的善良之旅》的儿童故事。故事的主人公，小象总是刻意去帮助她的动物朋友们，尽管他们并不总是友善。

    Returns:
        str: the story created by LLMs
    """
    story_prompt = prompt.story_prompt_red_ver(question)
    story = prompt_LLM(story_prompt)

    return story


def enrich_fragment(enrich_prompt: str) -> str:
    """
    Enrich the fragment based on the given extracted fragment, using specified style if given.
    润色故事片段

    Args:
        enrich_prompt (str): prompt to enrich the fragment

    Returns:
        str: the fragment enriched by LLMs
    """
    enriched_fragment = prompt_LLM(enrich_prompt)

    return enriched_fragment


def split_story(story: str) -> str:
    """
    Using message method to slide the story without modifying
    将故事分段，方便进行文生图

    Args:
        story (str): the story generated by LLMs

    Returns:
        str: split story in which & symbol indicating the fragments
    """
    messages = [{
        "role": "user",
        "content": "帮我分割一个故事，每一个部分以&结尾，且不要有换行符，至少分出3部分，每部分大约35个字"
    }, {
        "role": "assistant",
        "content": "给我你的故事，我将割一个故事，每一个部分以&结尾，且不要有换行符，至少分出3部分，每部分大约35个字"
    }, {
        "role": "user",
        "content": "在遥远的森林深处，有一个被茂密树木和五彩斑斓的花朵环绕的村庄，这个村庄叫做“和谐村”。村里的居民们和睦相处，生活平静而幸福。然而，村庄里流传着一个古老而神秘的传说，关于一个拥有神奇力量的宝石——“和谐之心”。故事的主人公是一个名叫艾拉的小女孩，艾拉有着一头金色的长发和明亮的蓝眼睛，她对世界充满了好奇。她的父母都是村里的医生，经常帮助村民治疗疾病。艾拉从小就梦想着成为像父母一样的人，为村庄带来帮助和快乐。一天，艾拉在森林里探险时，无意中听到了关于“和谐之心”的传说，据说这颗宝石拥有实现愿望的力量，但只有心怀善意的人才能够找到它。艾拉被这个传说深深吸引，她决定踏上寻找宝石的旅程。艾拉的旅程并不容易，森林里充满了未知的危险，她遇到了各种各样的困难。有一次，她差点被一只凶猛的野狼攻击，幸好一只勇敢的狐狸出现，帮助她摆脱了危险。艾拉感激地向狐狸道谢，并与它成为了朋友。在旅途中，艾拉遇到了一位智慧的老猫头鹰，猫头鹰告诉她，要找到“和谐之心”，她必须通过三个考验：勇气、智慧和爱心。艾拉铭记在心，继续她的旅程。第一个考验是勇气，艾拉必须穿过一片被称为“恐惧之谷”的地方，谷中充满了迷雾和奇怪的声音，让人不寒而栗。但艾拉鼓起勇气，坚定地走了过去，她发现，恐惧只是自己内心的幻象。第二个考验是智慧，艾拉来到了一个巨大的迷宫，迷宫的出口就是宝石的所在地。她仔细观察迷宫的布局，运用逻辑思维，最终找到了出口。最后一个考验是爱心，艾拉遇到了一个受伤的小鹿，它无法行走。艾拉没有犹豫，她停下来照顾小鹿，用自己的衣服为它包扎伤口。小鹿康复后，带领艾拉找到了隐藏在瀑布后的“和谐之心”。艾拉找到了“和谐之心”，她许下了一个愿望：希望村庄永远和平，所有的居民都能幸福安康。宝石发出了耀眼的光芒，然后化作一道光，飞向了天空，照亮了整个村庄。艾拉带着宝石的力量回到了村庄，她的经历激励了所有的村民，她的勇气、智慧和爱心成为了村庄的传奇。艾拉没有保留宝石的力量，而是选择将它分享给了每一个人。从此，和谐村变得更加和谐，村民们的生活更加幸福。艾拉成为了村庄的英雄，她的故事被传唱了很多年，而“和谐之心”的传说也永远地留在了人们的心中。"
    }, {
        "role": "assistant",
        "content": "《和谐村的传说 —— 艾拉的奇幻之旅》&在一片神秘的森林中，隐藏着一个和谐的小村庄。村庄里的人们和睦相处，生活平静而幸福。&艾拉，一个有着金色长发和蓝眼睛的小女孩，梦想着成为像父母一样的医生，帮助所有人。&一天，艾拉在森林里听到了关于“和谐之心”的传说，她决定去寻找这颗能实现愿望的宝石。&艾拉的旅程开始了，她遇到了勇敢的狐狸，它帮助她逃离了凶猛的野狼。&智慧的老猫头鹰告诉艾拉，要找到宝石，她必须通过勇气、智慧和爱心的考验。&艾拉勇敢地穿过了充满迷雾和奇怪声音的“恐惧之谷”，克服了内心的恐惧。&在巨大的迷宫中，艾拉用她的智慧找到了通往宝石的出口。&艾拉展现了她的爱心，照顾了一只受伤的小鹿，并在它的帮助下找到了“和谐之心”。&艾拉许下了愿望，宝石发出耀眼的光芒，化作一道光飞向了天空，照亮了整个村庄。&艾拉带着宝石的力量回到了村庄，她的勇气、智慧和爱心激励了所有的村民。&艾拉成为了村庄的英雄，她的故事和“和谐之心”的传说被永远地留在了人们的心中。"
    }, {
        "role": "user",
        "content": "在一个遥远的国度里，有一片被阳光照耀的金色麦田，麦田中坐落着一个名叫“风车村”的小村庄。村庄里住着一个好奇心旺盛的小男孩，他的名字叫杰米。杰米有着一头乌黑的头发和明亮的大眼睛，他总是梦想着探索未知的世界。一天，杰米在村边的小溪旁捡到了一张古老的地图，地图上标记着一条通往神秘宝藏的路线。杰米的心中燃起了冒险的火焰，他决定踏上寻宝之旅。他告别了父母和朋友们，带着地图和一背包的必需品，向着地图上的“X”标记出发了。杰米的旅程充满了挑战。他首先穿过了一片幽暗的森林，森林里住着各种各样的动物，有的友好，有的则不那么友好。一只狡猾的狐狸试图骗走他的背包，但杰米机智地用一串葡萄和狐狸交换了平安通过森林的路线。接着，杰米来到了一片广阔的草原，草原上空飞翔着各种奇异的鸟类。一只巨大的鹰在天空中盘旋，它看到了杰米，便俯冲下来，想要将他抓走。杰米不慌不忙，从背包中拿出一张彩色的布，在空中挥舞，成功地分散了鹰的注意力，趁机逃离了草原。最后，杰米到达了一片崎岖的山脉，山脉中隐藏着许多秘密的洞穴。在洞穴中，杰米遇到了一个古老的守护者，守护者问他三个谜题，只有答对了才能继续前进。杰米凭借他的智慧和勇气，一一解开了谜题，守护者满意地点了点头，为他打开了通往宝藏的大门。当杰米走进藏宝室，他惊讶地发现，所谓的宝藏并不是金银财宝，而是满屋子的书籍和知识。杰米意识到，真正的宝藏是知识和智慧。他带着满载书籍的背包回到了村庄，与村民们分享了他的发现。从此，风车村成为了一个充满知识和智慧的地方，而杰米的故事也激励着每一个孩子去勇敢地追求自己的梦想。"
    }, {
        "role": "assistant",
        "content": "《杰米的宝藏之旅》&在一个遥远的国度里，有一片被阳光照耀的金色麦田，麦田中坐落着一个名叫“风车村”的小村庄。&村庄里住着一个好奇心旺盛的小男孩，他的名字叫杰米。杰米有着一头乌黑的头发和明亮的大眼睛，他总是梦想着探索未知的世界。&一天，杰米在村边的小溪旁捡到了一张古老的地图，地图上标记着一条通往神秘宝藏的路线。&杰米的心中燃起了冒险的火焰，他决定踏上寻宝之旅。他告别了父母和朋友们，带着地图和一背包的必需品，向着地图上的“X”标记出发了。&杰米的旅程充满了挑战。他首先穿过了一片幽暗的森林，森林里住着各种各样的动物，有的友好，有的则不那么友好。&一只狡猾的狐狸试图骗走他的背包，但杰米机智地用一串葡萄和狐狸交换了平安通过森林的路线。&接着，杰米来到了一片广阔的草原，草原上空飞翔着各种奇异的鸟类。&一只巨大的鹰在天空中盘旋，它看到了杰米，便俯冲下来，想要将他抓走。&杰米不慌不忙，从背包中拿出一张彩色的布，在空中挥舞，成功地分散了鹰的注意力，趁机逃离了草原。&最后，杰米到达了一片崎岖的山脉，山脉中隐藏着许多秘密的洞穴。&在洞穴中，杰米遇到了一个古老的守护者，守护者问他三个谜题，只有答对了才能继续前进。&杰米凭借他的智慧和勇气，一一解开了谜题，守护者满意地点了点头，为他打开了通往宝藏的大门。&当杰米走进藏宝室，他惊讶地发现，所谓的宝藏并不是金银财宝，而是满屋子的书籍和知识。&杰米意识到，真正的宝藏是知识和智慧。他带着满载书籍的背包回到了村庄，与村民们分享了他的发现。&从此，风车村成为了一个充满知识和智慧的地方，而杰米的故事也激励着每一个孩子去勇敢地追求自己的梦想。&杰米的故事告诉我们，最宝贵的财富不是金银财宝，而是我们心中的梦想和不懈追求。"
    }, {
        "role": "user",
        "content": "在一个遥远的国度里，有一个被郁郁葱葱的森林和蜿蜒的河流环绕的小镇，名叫“彩虹镇”。小镇上的居民们生活得很和谐，他们的房子涂着各种鲜艳的颜色，就像彩虹一样美丽。在彩虹镇的边缘，住着一个叫莉莉的小女孩。莉莉有着一头金色的卷发和充满好奇的大眼睛。她最喜欢的事就是探索森林，寻找新奇的植物和动物。一天，莉莉在森林里发现了一朵会唱歌的神奇花朵。这朵花唱着悦耳的旋律，莉莉听得入了迷。花朵唱完后，告诉莉莉一个秘密：森林深处有一个被遗忘的宝藏，它属于那些勇敢和善良的孩子们。莉莉决定踏上寻宝之旅。她带上了自己的小背包，里面装着水、面包和一张手绘的地图。在旅途中，她帮助了一只受伤的小鸟，找到了丢失的小猫，并与一只友好的松鼠成为了朋友。经过一系列的冒险，莉莉终于来到了宝藏的所在地。她发现宝藏其实是一间充满书籍和玩具的小屋。小屋的墙上写着：“真正的宝藏是好奇心和乐于助人的心。”莉莉明白了，这次旅行中最宝贵的是她所经历的冒险和所交的朋友。她带着满心的喜悦和小屋里的一些书籍回到了彩虹镇，与所有的孩子们分享了她的故事和宝藏。从那以后，莉莉成了彩虹镇的英雄，她的故事激励着每个孩子去探索未知，去帮助他人，并珍惜生活中的每一份美好。"
    }, {
        "role": "assistant",
        "content": "《彩虹镇的宝藏》&在一个遥远的国度里，有一个被郁郁葱葱的森林和蜿蜒的河流环绕的小镇，名叫“彩虹镇”。小镇上的居民们生活得很和谐，他们的房子涂着各种鲜艳的颜色，就像彩虹一样美丽。&在彩虹镇的边缘，住着一个叫莉莉的小女孩。莉莉有着一头金色的卷发和充满好奇的大眼睛。她最喜欢的事就是探索森林，寻找新奇的植物和动物。&一天，莉莉在森林里发现了一朵会唱歌的神奇花朵。这朵花唱着悦耳的旋律，莉莉听得入了迷。&花朵唱完后，告诉莉莉一个秘密：森林深处有一个被遗忘的宝藏，它属于那些勇敢和善良的孩子们。莉莉的心中燃起了希望的火花，她决定踏上寻宝之旅。&莉莉带上了自己的小背包，里面装着水、面包和一张手绘的地图。在旅途中，她帮助了一只受伤的小鸟，找到了丢失的小猫，并与一只友好的松鼠成为了朋友。&经过一系列的冒险，莉莉终于来到了宝藏的所在地。她发现宝藏其实是一间充满书籍和玩具的小屋。小屋的墙上写着：“真正的宝藏是好奇心和乐于助人的心。”&莉莉带着满心的喜悦和小屋里的一些书籍回到了彩虹镇，与所有的孩子们分享了她的故事和宝藏。她的故事迅速传遍了整个小镇，激励着每一个孩子去探索未知，去帮助他人。&从那以后，莉莉成了彩虹镇的英雄，她的故事告诉大家，最宝贵的财富不是金银财宝，而是我们心中的梦想、勇气和乐于助人的精神。彩虹镇的每个孩子都被莉莉的勇气所鼓舞，他们知道，只要拥有一颗善良和好奇的心，每个人都能找到属于自己的宝藏。"
    }, {
        "role": "user",
        "content": story
    }]

    response = prompt_LLM(messages, message_mode=True)

    return response


def obtain_pic_LLM_prompt(fragment: str, question: Optional[str] = None) -> str:
    """
    Call the API to obtain the prompt with the given enriched fragment
    根据故事片段生成文生图prompt

    Args:
        fragment (str): the extracted fragment that enriched by LLM
        question (str, optional): the style needed. Defaults to None.

    Returns:
        str: the LLM generated picture prompt
    """
    demos = prompt.demo_pic_prompt()
    if question is None:
        prompt_question = prompt.pic_prompt_question(fragment)
    else:
        prompt_question = prompt.pic_prompt_question(fragment, question)

    LLM_prompt = prompt_LLM(demos + prompt_question)

    return LLM_prompt


def obtain_pic_LLM_prompt_red_ver(fragment: str, question: Optional[str] = None) -> str:
    """
    Call the API to obtain the prompt with the given enriched fragment
    根据故事片段生成文生图prompt

    Args:
        fragment (str): the extracted fragment that enriched by LLM
        question (str, optional): the style needed. Defaults to None.

    Returns:
        str: the LLM generated picture prompt
    """
    demos = prompt.demo_pic_prompt()
    if question is None:
        prompt_question = prompt.pic_prompt_question_red_ver(fragment)
    else:
        prompt_question = prompt.pic_prompt_question_red_ver(fragment, question)

    LLM_prompt = prompt_LLM(demos + prompt_question)

    return LLM_prompt


def extract_fragments(original_fragments: str) -> list[str]:
    """
    Extract the fragments
    提取片段关键信息

    Args:
        original_fragments (str): the original fragments without splitting

    Returns:
        extracted_fragments (str): string format extracted fragments
        extracted_fragments_list (list[str]): string list format extracted fragments
    """
    extract_prompt = prompt.extract_prompt(original_fragments)
    extracted_fragments = prompt_LLM(extract_prompt)
    extracted_fragments_list = extracted_fragments.split("&")

    return extracted_fragments_list


def extract_fragments_red_ver(original_fragments: str) -> list[str]:
    """
    Extract the fragments
    提取片段关键信息

    Args:
        original_fragments (str): the original fragments without splitting

    Returns:
        extracted_fragments (str): string format extracted fragments
        extracted_fragments_list (list[str]): string list format extracted fragments
    """
    extract_prompt = prompt.extract_prompt_red_ver(original_fragments)
    extracted_fragments = prompt_LLM(extract_prompt)
    extracted_fragments_list = extracted_fragments.split("&")

    return extracted_fragments_list


def polish_fragment(extracted_fragment: str) -> str:
    """
    polish the fragment
    再次打磨并精简提取出的片段

    Args:
        extracted_fragment (str): fragment that have been extracted

    Returns:
        str: fragment that have been polished
    """
    polish_prompt = prompt.polish_prompt(extracted_fragment)
    polished_fragment = prompt_LLM(polish_prompt)
    print(polished_fragment)

    return polished_fragment


def polish_fragment_red_ver(extracted_fragment: str) -> str:
    """
    polish the fragment
    再次打磨并精简提取出的片段

    Args:
        extracted_fragment (str): fragment that have been extracted

    Returns:
        str: fragment that have been polished
    """
    polish_prompt = prompt.polish_prompt_red_ver(extracted_fragment)
    polished_fragment = prompt_LLM(polish_prompt)
    print(polished_fragment)

    return polished_fragment


def enrich(original_fragment: str, story: str, index: str, flag: bool = False) -> str:
    """
    Enrich a single original fragment
    丰富一个给定的故事片段

    Args:
        original_fragment (str): the original fragment
        story (str): the original story
        index (int): the fragment number
        flag (bool, optional): true when repeatedly receives unsuccessful, modifying the prompt. Defaults to False.

    Returns:
        str: the enriched fragment
    """
    enrich_prompt = prompt.enrich_fragment_prompt(fragment=original_fragment, story=story, flag=flag)
    print(f"\n{enrich_prompt}   \nindex = {index}   enriching---------------------------------")
    enriched_fragment = enrich_fragment(enrich_prompt)
    print(f"\n{enriched_fragment}   \nindex = {index}   enriched-------------------------------")

    return enriched_fragment


def enrich_red_ver(original_fragment: str, story: str, index: str, flag: bool = True) -> str:
    """
    Enrich a single original fragment
    丰富一个给定的故事片段

    Args:
        original_fragment (str): the original fragment
        story (str): the original story
        index (int): the fragment number
        flag (bool, optional): true when repeatedly receives unsuccessful, modifying the prompt. Defaults to False.

    Returns:
        str: the enriched fragment
    """
    enrich_prompt = prompt.enrich_fragment_prompt_red_ver(fragment=original_fragment, story=story, flag=flag)
    print(f"\n{enrich_prompt}   \nindex = {index}   enriching---------------------------------")
    enriched_fragment = enrich_fragment(enrich_prompt)
    print(f"\n{enriched_fragment}   \nindex = {index}   enriched-------------------------------")

    return enriched_fragment


def obtain_pic_prompt(enriched_fragment: str, index: int) -> str:
    """
    Obtain a txt_to_img prompt based on the given fragment by calling API and concatenate it with consistent style
    生成最终的用于生成图片的prompt

    Args:
        enriched_fragment (str): an enriched fragment
        index (int): the fragment number

    Returns:
        string: the corresponding txt_to_img prompt
    """
    print(f"\nindex = {index} obtaining pic prompt-------------------------------------")
    pic_LLM_prompt = obtain_pic_LLM_prompt(enriched_fragment)
    print(f"\nindex = {index}   LLM_prompt---------------------------------------------\n{pic_LLM_prompt}")
    pic_prompt = prompt.pic_prompt(pic_LLM_prompt)
    print(f"\nindex = {index}   pic_prompt---------------------------------------------\n{pic_prompt}")

    return pic_prompt


def obtain_pic_prompt_red_ver(enriched_fragment: str, index: int) -> str:
    """
    Obtain a txt_to_img prompt based on the given fragment by calling API and concatenate it with consistent style
    生成最终的用于生成图片的prompt

    Args:
        enriched_fragment (str): an enriched fragment
        index (int): the fragment number

    Returns:
        string: the corresponding txt_to_img prompt
    """
    print(f"\nindex = {index} obtaining pic prompt-------------------------------------")
    pic_LLM_prompt = obtain_pic_LLM_prompt_red_ver(enriched_fragment)
    print(f"\nindex = {index}   LLM_prompt---------------------------------------------\n{pic_LLM_prompt}")
    pic_prompt = prompt.pic_prompt_red_ver(pic_LLM_prompt)
    print(f"\nindex = {index}   pic_prompt---------------------------------------------\n{pic_prompt}")

    return pic_prompt


async def create_async_task(prompt=demoPrompt):
    parameters = {
        "api_key": DASHSCOPE_API_KEY,
        # "model": ImageSynthesis.Models.wanx_v1,
        "model": "wanx2.1-t2i-turbo",
        "prompt": prompt,
        "n": 1,
        "style": '<watercolor>',
        "size": '1280*720'
    }

    print(parameters["prompt"])
    rsp = ImageSynthesis.async_call(**parameters)  # 发送绘图请求给模型，返回图像生成任务的ID

    print("SUBMIT TASK" + "=" * 100)
    print(rsp)
    print("SUBMIT TASK" + "=" * 100)

    if rsp.status_code == HTTPStatus.OK:
        print(rsp.output)
    else:
        print('Failed, status_code: %s, code: %s, message: %s' %
              (rsp.status_code, rsp.code, rsp.message))

    return rsp


async def wait_async_task(task):
    rsp = ImageSynthesis.wait(task, api_key=DASHSCOPE_API_KEY)  # 发送查询请求，等待返回绘图结果

    print("TASK RESULT" + "=" * 100)
    print(rsp)
    print("TASK RESULT" + "=" * 100)

    if rsp.status_code == HTTPStatus.OK:
        print(rsp.output)
        return rsp.output.results[0].url
    else:
        print('Failed, status_code: %s, code: %s, message: %s' %
              (rsp.status_code, rsp.code, rsp.message))


async def draw_cover(title: str, story: str, style='水彩风格') -> tuple:
    """
    draw the cover
    异步进行封面绘制

    Args:
        title (str): title of the story
        story (str): original story
        style (str): the specific style. Defaults to 水彩风格
    Returns:
        str: cover prompt
        str: cover url
    """

    prompt_template = f"""角色：现在你是一个midjourney格式提示词生成大师
    任务：我需要你为我撰写用于生成绘本封面的midjourney形式的提示词
    详细说明：
    1. 请根据标题和完整故事，捕捉整个故事的主要人物，情节和风格
    2. 根据主要人物，情节和风格生成midjourney形式的提示词
    3. 完整故事在<完整故事>处给出，标题<标题>处给出
    4. 请不要为角色命名
    5. 请不要使用会触发审核机制的文字描述，避免使用政治敏感词汇！
    6. 使用{style}
    <完整故事>: {story}
    <标题> : {title}
    """
    cover_pic_prompt = prompt_LLM(prompt_template)
    pic_task = await create_async_task(cover_pic_prompt)
    print(pic_task.output)
    url = await wait_async_task(pic_task)
    print(url)

    return cover_pic_prompt, url


class QPSController:
    def __init__(self, qps_limit):
        self.qps_limit = qps_limit
        self.requests = []

    async def wait(self):
        current_time = time.time()
        self.requests[:] = [t for t in self.requests if t + 1 >= current_time]  # 检查列表中的请求是否超过了1秒，若超过则视为过期
        if len(self.requests) >= self.qps_limit:  # 如果列表中请求超出限制
            oldest_request_time = self.requests[0]
            sleep_time = oldest_request_time + 1 - current_time  # 为列表中最早的请求留出时间执行，确保列表中请求数量不超过限制数量
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
        self.requests.append(time.time())


# 异步提交封装
async def async_cv_submit_task(form, qps_controller):
    await qps_controller.wait()
    try:
        result = await create_async_task(**form)  # 调用创建绘图任务的异步函数
        return result
    except Exception as e:
        logging.error(f"Error submitting task: {e}")
        return None


# 异步获得url封装
async def async_cv_get_result(form, qps_controller):
    await qps_controller.wait()
    try:
        result = await wait_async_task(form)  # 调用获取结果的异步函数
        return result
    except Exception as e:
        logging.error(f"Error getting result: {e}")
        return None


# 生产者
async def producer(queue, qps_controller, data_list, index):
    for data, idx in zip(data_list, index):
        form = {
            "prompt": data,
        }
        try:
            resp = await async_cv_submit_task(form, qps_controller)
            if resp:
                resp["idx"] = idx
                await queue.put(resp)
            else:
                logging.warning(f"Failed to submit task: {resp}")
        except Exception as e:
            logging.error(f"Error in producer: {e}")
    await queue.put(None)  # 表示生产结束


# 消费者
async def consumer(queue, qps_controller, image_list):
    while True:
        try:
            task = await queue.get()
            if task is None:
                queue.task_done()
                break  # 消费结束
            task_id = task["output"]["task_id"]
            result = await async_cv_get_result(task, qps_controller)
            image_list.append((result, task["idx"]))
            logging.info(f"Result for task_id {task_id}: {result}")
            queue.task_done()
        except Exception as e:
            logging.error(f"Error in consumer: {e}")
            queue.task_done()


# 消费者,带缓存
async def consumer_async(queue, qps_controller, image_list, storyId):
    while True:
        try:
            task = await queue.get()
            if task is None:
                queue.task_done()
                break  # 消费结束
            task_id = task["output"]["task_id"]
            result = await async_cv_get_result(task, qps_controller)

            # 设置缓存
            tools.tmpCache.setUrl(storyId, result, task["idx"])

            image_list.append((result, task["idx"]))
            logging.info(f"Result for task_id {task_id}: {result}")
            queue.task_done()
        except Exception as e:
            logging.error(f"Error in consumer: {e}")
            queue.task_done()


# 执行内容绘制的主函数
async def draw_image_list(prompt_list):
    qps_controller = QPSController(qps_limit=2)
    image_list = []

    queue = asyncio.Queue()

    num_producers = 3
    num_consumers = 3
    chunk_size = len(prompt_list) // num_producers

    producer_tasks = []

    for i in range(num_producers):
        start = i * chunk_size
        end = (i + 1) * chunk_size if i < num_producers - 1 else len(prompt_list)
        sub_list = prompt_list[start:end]
        producer_tasks.append(asyncio.create_task(producer(queue, qps_controller, sub_list, range(start, end + 1))))

    consumer_tasks = [asyncio.create_task(consumer(queue, qps_controller, image_list)) for _ in range(num_consumers)]

    await asyncio.gather(*producer_tasks)  # 等待生产者结束
    await queue.join()  # 等到队列为空
    await asyncio.gather(*consumer_tasks)  # 等待消费者结束

    print(image_list)
    return image_list


# 执行内容绘制的主函数,带缓存
async def draw_image_list_async(prompt_list, storyId):
    qps_controller = QPSController(qps_limit=2)
    image_list = []

    queue = asyncio.Queue()

    num_producers = 3
    num_consumers = 3
    chunk_size = len(prompt_list) // num_producers

    producer_tasks = []

    for i in range(num_producers):
        start = i * chunk_size
        end = (i + 1) * chunk_size if i < num_producers - 1 else len(prompt_list)
        sub_list = prompt_list[start:end]
        producer_tasks.append(asyncio.create_task(producer(queue, qps_controller, sub_list, range(start, end + 1))))

    consumer_tasks = [asyncio.create_task(consumer_async(queue, qps_controller, image_list, storyId)) for _ in range(num_consumers)]

    await asyncio.gather(*producer_tasks)  # 等待生产者结束
    await queue.join()  # 等到队列为空
    await asyncio.gather(*consumer_tasks)  # 等待消费者结束

    print(image_list)
    return image_list


def threading_query(query_function, *args):
    """
    Threading query models using thread pool
    使用线程池并发执行任务

    Args:
        query_function (function): query function for threading
        *args : the args passing to the function

    Returns:
        generator: threads results
    """
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = executor.map(query_function, *args)

    return results


def enrich_and_draw(extracted_fragments: list[str], story: str):
    """
    Encapsulate enriching the drawing function for multi-threading
    并发执行对故事片段的丰富，并进行绘制

    Args:
        extracted_fragments (list[str]): extracted fragments
        story (str): original story

    Returns:
        tuple: (pic_url, fragment number)
    """
    enriched_fragments = list(threading_query(enrich, extracted_fragments,
                                              [story for _ in range(len(extracted_fragments))],
                                              range(len(extracted_fragments))))
    pic_prompts = list(threading_query(obtain_pic_prompt, enriched_fragments,
                                       range(len(enriched_fragments))))
    pic_urls = asyncio.run(draw_image_list(pic_prompts))
    return enriched_fragments, pic_urls


def enrich_and_draw_red_ver(extracted_fragments: list[str], story: str):
    """
    Encapsulate enriching the drawing function for multi-threading
    并发执行对故事片段的丰富，并进行绘制

    Args:
        extracted_fragments (list[str]): extracted fragments
        story (str): original story

    Returns:
        tuple: (pic_url, fragment number)
    """
    enriched_fragments = list(threading_query(enrich_red_ver, extracted_fragments,
                                              [story for _ in range(len(extracted_fragments))],
                                              range(len(extracted_fragments))))
    pic_prompts = list(threading_query(obtain_pic_prompt_red_ver, enriched_fragments,
                                       range(len(enriched_fragments))))
    pic_urls = asyncio.run(draw_image_list(pic_prompts))
    # return enriched_fragments, pic_urls
    return extracted_fragments, pic_urls


def enrich_and_draw_async(extracted_fragments: list[str], story: str, storyId: str):
    enriched_fragments = list(threading_query(enrich, extracted_fragments,
                                              [story for _ in range(len(extracted_fragments))],
                                              range(len(extracted_fragments))))
    pic_prompts = list(threading_query(obtain_pic_prompt, enriched_fragments,
                                       range(len(enriched_fragments))))
    pic_urls = asyncio.run(draw_image_list_async(pic_prompts, storyId))
    return enriched_fragments, pic_urls


# TODO : function for draw with judge
def enrich_and_draw_with_judge(extracted_fragment: str, story: str, index: int, step: int = 3) -> tuple:
    """
    enrich the fragment and draw its picture with judgement

    Args:
        extracted_fragment (str): the fragment that has been extracted
        story (str): original story
        index (int): number for threading
        step (Optional[int], optional): the times to evaluate. Defaults to 3.

    Returns:
        tuple: (pic prompt, pic url)
    """

    # @retry(HTTPError, tries=5, delay=1)
    # def kind_mode():
    #     enriched_fragment = enrich(extracted_fragment, story, index, flag=True)
    #     pic_prompt = obtain_pic_prompt(enriched_fragment, index=index)
    #     pic_task = create_async_task(pic_prompt, index=index)
    #     enriched_fragment = enrich(extracted_fragment, story, index, flag=True)
    #     pic_prompt = obtain_pic_prompt(enriched_fragment, index)
    #     pic_task = create_async_task(pic_prompt, index=index)
    #     if pic_task['msg'] != 'successful':
    #         print(pic_task['msg'])
    #         raise HTTPError
    #     return pic_task
    #
    # enriched_fragment = enrich(extracted_fragment, story, index)
    #
    # def Create_generator():
    #     system_prompt_template = """你是一个midjourney格式的提示词生成大师，你十分擅长根据以下样例生成用于绘制儿童绘本的提示词
    #     样例：{demos}
    #     """
    #     prompt_generator = ChatPromptTemplate.from_messages(
    #         [
    #             ("system", system_prompt_template),
    #             MessagesPlaceholder(variable_name="messages"),
    #         ]
    #     )
    #     demos = prompt.demo_pic_prompt()
    #     prompt_generator = prompt_generator.partial(demos=demos)
    #     llm = BlueLM(temperature=0.7, model='vivo-BlueLM-TB')
    #     generator = prompt_generator | llm
    #     return generator
    #
    # def Create_rater():
    #     system_prompt_template = """你是一个客观的提示词打分器，你十分擅长为midjourney形式的提示词进行打分
    #     评分依据：{instructions}
    #     评分规则：{rules}
    #     请根据评分依据为提供的midjourney形式的提示词打分。
    #     """
    #     prompt = ChatPromptTemplate.from_messages(
    #         [
    #             ("system", system_prompt_template),
    #             MessagesPlaceholder(variable_name="messages"),
    #         ]
    #     )
    #     instructions = f"""
    #     评分依据共有三点，分别是风格，忠实度，一致性，定义如下
    #     1. 风格：指提示词的风格是否符合<完整故事>的风格，越符合的提示词得分越高
    #     2. 忠实度：指提示词内容和<提示词对应文本>是否相符，越符合的提示词得分越高
    #     3. 一致性：指提示词中出现的角色和人物和完整故事中的角色和人物是否一致，越一致得分越高
    #     <完整故事>: {story}
    #     <提示词对应文本>: {extracted_fragment}
    #     """
    #     rules = f"""
    #     1. 分析给定的提示词，为每个点分别给分，风格<s>，忠实度<f>，一致性<c>，分数在(0,1)之间
    #     2. 总分<k> = <s> + <f> + <c>
    #     4. 输出风格分数<s>,忠实度分数<f>, 一致性分数<c>, 总分<s> + <f> + <c> = <k>
    #     5. 结果保留一位小数
    #     6. 样例 : 风格分数：0.6，忠实度分数：0.5，一致性分数：0.7，总分：1.8分
    #     """
    #
    #     prompt = prompt.partial(instructions=instructions, rules=rules)
    #     llm = BlueLM(temperature=0.7, model='vivo-BlueLM-TB')
    #     rater = prompt | llm
    #     return rater
    #
    # generator = Create_generator()
    # rater = Create_rater()
    #
    # def generator_node(messages):
    #     print(messages)
    #     response = generator.invoke({"messages": messages})
    #     print(response)
    #     return response[3:]
    #
    # def rater_node(messages):
    #     print(messages)
    #     response = rater.invoke({"messages": messages})
    #     print(response)
    #     return response
    #
    # graph_builder = MessageGraph()
    # graph_builder.add_node("generator", generator_node)
    # graph_builder.add_node("rater", rater_node)
    #
    # graph_builder.add_edge("generator", "rater")
    #
    # graph_builder.add_edge(START, "generator")
    # graph_builder.add_edge("rater", END)
    # judgement = graph_builder.compile()
    #
    # messages = HumanMessage(content=enriched_fragment)
    #
    # rate: str = '0.0分'
    # pic_prompt: str = ''
    # while step > 0:
    #     for result in judgement.stream(messages):
    #         if result.get('generator') != None:
    #             pic_prompt_tmp = result.get('generator')
    #             print(pic_prompt_tmp)
    #         else:
    #             rate_tmp = result.get('rater')[-5:]
    #             print(rate_tmp)
    #         if pic_prompt == '':
    #             pic_prompt = pic_prompt_tmp
    #         elif rate_tmp > rate:
    #             pic_prompt = pic_prompt_tmp
    #             rate = rate_tmp
    #         time.sleep(1)
    #
    #     time.sleep(1)
    #
    #     step -= 1
    # print(rate)
    # print(pic_prompt)
    #
    # pic_prompt = prompt.pic_prompt(pic_prompt)
    #
    # #绘图请求
    # pic_task = create_async_task(pic_prompt, index=index)
    #
    # #如果触发审核
    # if pic_task['msg'] == 'successful':
    #     pic_task = kind_mode()
    #
    # # 获取url
    # pic_url = wait_async_task(pic_task, index)
    # return pic_prompt, pic_url


def create_modified_story(outline: str, story: str, requirement: str) -> str:
    """
    using the requirement to create a new story based on the original outline and story

    """

    prompt_template = f"""
    ## 角色：现在你是儿童故事大王，擅长写简单但富有哲理和教育意义的儿童故事。
    ## 任务：对<原故事>进行修改
    ## 要求：
    1. 根据<故事大纲>和<要求>对<原故事>进行修改
    2. 要求遵循<故事大纲>的发展
    3. 字数与原故事相近
    <故事大纲> {outline}
    <原故事> {story}
    <要求> {requirement}

    """

    modified_story = prompt_LLM(prompt_template)
    return modified_story


class XYQ_DeepseekLLM(LLM):
    """
        encapsulation of XYQ_DeepseekLLM using langchain LLM class
        used to create chain of judgement
    """
    model: str = "deepseek-chat"
    temperature: Optional[float] = 0.7
    key: Optional[str] = DEEPSEEK_API_KEY


def workflow(outline: str, judge: bool = False):
    """
        The basic work flow used in the beginning

        Args:
            outline (str): the user input, outline of the story
            judge (Optional[bool], optional): _description_. Defaults to False.

        Returns:
            tuple: _description_
    """
    try:
        # 故事生成
        story = create_story(outline)
        # 故事分段
        original_fragments = split_story(story)
        print(original_fragments)
        # 故事提炼
        extracted_fragments_list = extract_fragments(original_fragments)
        # print(extracted_fragments_list)
        # 封面绘制
        cover_pic_prompt, cover_url = asyncio.run(draw_cover(original_fragments, story))
        # 创建列表用于保存绘图prompt和url
        pic_prompts = [cover_pic_prompt]
        pic_urls = [cover_url]
        # 并发执行故事分段润色
        polished_results = list(threading_query(polish_fragment, extracted_fragments_list[1:]))  # 提取后片段的第一个元素是标题，无需润色
        polished_fragments = extracted_fragments_list[0:1] + polished_results
        print(polished_fragments)
        # 内容图片绘制
        if judge:
            # TODO : draw with judgement
            return False
        else:
            results = enrich_and_draw(extracted_fragments_list[1:], story)
        pic_prompts = pic_prompts + results[0]
        sorted_pic_urls = sorted(results[1], key=lambda x: x[1])
        for pic_url in sorted_pic_urls:
            pic_urls.append(pic_url[0])
        print([outline, story, pic_prompts, polished_fragments, pic_urls])
        return [outline, story, pic_prompts, polished_fragments, pic_urls], True

    except Exception as e:
        print("Workflow Error:",e)
        return [], False


# 疑似不可用
def stream_workflow(outline: str, judge: bool = False):
    # 异步返回信息
    try:
        # 故事生成
        story = create_story(outline)
        # 故事分段
        original_fragments = split_story(story)
        # 故事提炼
        extracted_fragments_list = extract_fragments(original_fragments)
        # 封面绘制
        cover_pic_prompt, cover_url = asyncio.run(draw_cover(original_fragments, story))
        # Stage 0: 标题和封面
        yield [extracted_fragments_list[0], cover_url]
        # 创建列表用于保存绘图prompt和url
        pic_prompts = [cover_pic_prompt]
        pic_urls = [cover_url]
        # 并发执行故事分段润色
        polished_results = list(threading_query(polish_fragment, extracted_fragments_list[1:]))  # 提取后片段的第一个元素是标题，无需润色
        polished_fragments = extracted_fragments_list[0:1] + polished_results
        print(polished_fragments)
        # Stage 1: 片段内容
        yield [polished_fragments]
        # 内容图片绘制
        if judge:
            # TODO : draw with judgement
            return False
        else:
            results = enrich_and_draw(extracted_fragments_list[1:], story)
        pic_prompts = pic_prompts + results[0]
        sorted_pic_urls = sorted(results[1], key=lambda x: x[1])
        for pic_url in sorted_pic_urls:
            pic_urls.append(pic_url[0])
        print([outline, story, pic_prompts, polished_fragments, pic_urls])
        # Stage 2: 所有内容
        yield [outline, story, pic_prompts, polished_fragments, pic_urls], True

    except Exception as e:
        print(e)
        return [], False


def async_workflow(outline: str):
    try:
        # 故事生成
        story = create_story(outline)
        # 故事分段
        original_fragments = split_story(story)
        # 故事提炼
        extracted_fragments_list = extract_fragments(original_fragments)
        # 封面绘制
        cover_pic_prompt, cover_url = asyncio.run(draw_cover(original_fragments, story))
        # 创建列表用于保存绘图prompt和url
        pic_prompts = [cover_pic_prompt]
        pic_urls = [cover_url]
        # 并发执行故事分段润色
        polished_results = list(threading_query(polish_fragment, extracted_fragments_list[1:]))  # 提取后片段的第一个元素是标题，无需润色
        polished_fragments = extracted_fragments_list[0:1] + polished_results
        print(polished_fragments)
        return [outline, story, pic_prompts, polished_fragments, pic_urls, extracted_fragments_list], True

    except Exception as e:
        print(e)
        return [], False


def async_workflow_process(res, storyId, judge: bool = False):
    outline = res[0]
    extracted_fragments_list = res[5]
    story = res[1]
    pic_prompts = res[2]
    pic_urls = res[4]
    polished_fragments = res[3]
    try:
        # 内容图片绘制
        if judge:
            # TODO : draw with judgement
            return False
        else:
            results = enrich_and_draw_async(extracted_fragments_list[1:], story, storyId)
        pic_prompts = pic_prompts + results[0]
        sorted_pic_urls = sorted(results[1], key=lambda x: x[1])
        for pic_url in sorted_pic_urls:
            pic_urls.append(pic_url[0])
        print([outline, story, pic_prompts, polished_fragments, pic_urls])
        return [outline, story, pic_prompts, polished_fragments, pic_urls], True
    except Exception as e:
        print(e)
        return [], False


def workflow_red_ver(outline: str, judge: bool = False):
    try:
        # 故事生成
        story = create_story_red_ver(outline)
        # 故事分段
        original_fragments = split_story(story)
        print(original_fragments)
        # 故事提炼
        extracted_fragments_list = extract_fragments_red_ver(original_fragments)
        # print(extracted_fragments_list)
        # 封面绘制
        cover_pic_prompt, cover_url = asyncio.run(draw_cover(original_fragments, story, "油画风格"))
        # 创建列表用于保存绘图prompt和url
        pic_prompts = [cover_pic_prompt]
        pic_urls = [cover_url]
        # 并发执行故事分段润色 此处放弃润色
        # polished_results = list(threading_query(polish_fragment_red_ver, extracted_fragments_list[1:]))  # 提取后片段的第一个元素是标题，无需润色
        # polished_fragments = extracted_fragments_list[0:1] + polished_results
        polished_fragments = extracted_fragments_list
        print(polished_fragments)
        # 内容图片绘制
        if judge:
            # TODO : draw with judgement
            return False
        else:
            results = enrich_and_draw_red_ver(extracted_fragments_list[1:], story)
        pic_prompts = pic_prompts + results[0]
        sorted_pic_urls = sorted(results[1], key=lambda x: x[1])
        for pic_url in sorted_pic_urls:
            pic_urls.append(pic_url[0])
        print([outline, story, pic_prompts, polished_fragments, pic_urls])
        return [outline, story, pic_prompts, polished_fragments, pic_urls], True

    except Exception as e:
        print("Workflow Error:",e)
        return [], False



def modify_flow(outline: str, story: str, requirement: str, judge: bool = False):
    try:
        # 重写故事
        modified_story = create_modified_story(outline, story, requirement)
        # 故事分段
        original_fragments = split_story(modified_story)
        # 故事提炼
        extracted_fragments_list = extract_fragments(original_fragments)
        # 封面绘制
        cover_pic_prompt, cover_url = asyncio.run(draw_cover(original_fragments, story))
        # 创建列表用于保存绘图prompt和url
        pic_prompts = [cover_pic_prompt]
        pic_urls = [cover_url]
        # 并发执行故事分段润色
        polished_results = list(threading_query(polish_fragment, extracted_fragments_list[1:]))  # 提取后片段的第一个元素是标题，无需润色
        polished_fragments = extracted_fragments_list[0:1] + polished_results
        print(polished_fragments)
        # 内容图片绘制
        if judge:
            # TODO : draw with judgement
            return False
        else:
            results = enrich_and_draw(extracted_fragments_list[1:], story)
        pic_prompts = pic_prompts + results[0]
        sorted_pic_urls = sorted(results[1], key=lambda x: x[1])
        for pic_url in sorted_pic_urls:
            pic_urls.append(pic_url[0])
        return [outline, modified_story, pic_prompts, polished_fragments, pic_urls], True

    except Exception as e:
        print(e)
        return [], False


async def redraw_pic(pic_prompt: str):
    task = await create_async_task(pic_prompt)
    url = await wait_async_task(task)
    return url


# 重绘一张图片
def roll_pic(pic_prompt: str):
    url = asyncio.run(redraw_pic(pic_prompt))
    return url


# 重绘封面
def roll_cover(pic_prompt: str):
    url = asyncio.run(redraw_pic(pic_prompt))
    return url
