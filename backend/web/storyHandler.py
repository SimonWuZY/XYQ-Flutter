import time
from functools import update_wrapper

from flask import Blueprint, request, json, jsonify, current_app, Response

import tools.tmpCache
from service.story import service
from web.checkLoginMiddleware import checkLoginMiddleware


class StreamView(object):
    """A decorator for flask view."""

    def __init__(self, view_function):
        self.view_function = view_function
        update_wrapper(self, self.view_function)

    def __call__(self, *args, **kwargs):
        return_value = self.view_function(*args, **kwargs)
        try:
            response = iter(return_value)
        except TypeError:
            # the return value is not iterable
            response = return_value
            current_app.logger.warning(
                "The stream view %r isn't iterable." % self)
        else:
            # the return value is iterable
            response = Response(return_value, direct_passthrough=True)
        return response


stream_view = StreamView

storyBlueprint = Blueprint('story', __name__, url_prefix='/story')


# 生成故事，前端传来故事大纲
# 返回值： 故事id， True
#         None， False
@storyBlueprint.route('/generateStory', methods=['POST'])
def generateStory():
    data = json.loads(request.get_data())
    userName, ok = checkLoginMiddleware(data)
    if not ok:
        return jsonify({"message": "false"})

    # 调用service服务
    a = time.time()
    storyId, ok = service.generateStory(userName, data['outline'])
    if ok:
        #with open(r"C:\Users\22305\Desktop\hhh.txt", mode='a') as filename:
        #with open(r"D:\CodeRepository\Python\PyCharm\xyq\hhh.txt", mode='a') as filename:
        with open(r"\www\wwwroot\xyq\hhh.txt", mode='a') as filename:
            filename.write((time.time() - a).__str__())
            filename.write('\n')
        print({"storyId": storyId, "message": "true"})
        return jsonify({"storyId": storyId, "message": "true"})
    print({"storyId": None, "message": "false"})
    return jsonify({"storyId": None, "message": "false"})


# 生成故事，前端传来故事大纲
# 返回值： 故事id， True
#         None， False
@storyBlueprint.route('/generateStoryStream', methods=['POST'])
@stream_view
def generateStoryStream():
    data = json.loads(request.get_data())
    userName, ok = checkLoginMiddleware(data)
    if not ok:
        return jsonify({"message": "false"})

    # 调用service服务
    a = time.time()
    generator = service.generateStoryStream(userName, data['outline'])
    # Stage 0
    res0, ok = next(generator)
    if not ok:
        return jsonify({"message": "false"})
    storyId = res0[0]
    title = res0[1]
    cover_url = res0[2]
    yield jsonify({"storyId": storyId, "title": title, "cover_url": cover_url, "message": "true"})
    # Stage 1
    res1, ok = next(generator)
    if not ok:
        return jsonify({"message": "false"})
    texts = res1[1]
    yield jsonify({"storyId": storyId, "texts": texts, "message": "true"})
    # Stage 2
    res2, ok = next(generator)
    if ok:
        #with open(r"C:\Users\22305\Desktop\hhh.txt", mode='a') as filename:
        #with open(r"D:\CodeRepository\Python\PyCharm\xyq\hhh.txt", mode='a') as filename:
        with open(r"\www\wwwroot\xyq\hhh.txt", mode='a') as filename:
            filename.write((time.time() - a).__str__())
            filename.write('\n')
        print({"storyId": storyId, "message": "true"})
        yield jsonify({"storyId": storyId, "message": "true"})
    print({"storyId": None, "message": "false"})
    yield jsonify({"storyId": None, "message": "false"})


@storyBlueprint.route('/generateStoryAsync', methods=['POST'])
def generateStoryAsync():
    data = json.loads(request.get_data())
    userName, ok = checkLoginMiddleware(data)
    if not ok:
        return jsonify({"message": "false"})

    # 调用service服务
    a = time.time()
    storyId, ok = service.generateStoryAsync(userName, data['outline'])
    if ok:
        #with open(r"C:\Users\22305\Desktop\hhh.txt", mode='a') as filename:
        with open(r"D:\CodeRepository\Python\PyCharm\xyq\hhh.txt", mode='a') as filename:
        # with open(r"\www\wwwroot\xyq\hhh.txt", mode='a') as filename:
            filename.write((time.time() - a).__str__())
            filename.write('\n')
        print({"storyId": storyId, "message": "true"})
        return jsonify({"storyId": storyId, "message": "true"})
    print({"storyId": None, "message": "false"})
    return jsonify({"storyId": None, "message": "false"})


# 通过id检查任务情况
@storyBlueprint.route('checkGenerateStatus', methods=['POST'])
def checkGenerateStatus():
    data = json.loads(request.get_data())
    userName, ok = checkLoginMiddleware(data)
    if not ok:
        return jsonify({"message": "false"})

    storyId = data["storyId"]
    return jsonify(tools.tmpCache.getTaskCache(storyId))


# 通过id保存指定的故事
@storyBlueprint.route('/saveStory', methods=['POST'])
def saveStory():
    data = json.loads(request.get_data())
    userName, ok = checkLoginMiddleware(data)
    if not ok:
        return jsonify({"message": "false"})

    # 调用service服务
    storyId = data["storyId"]
    ok = service.saveStory(storyId)
    if ok:
        return jsonify({"message": "true"})
    return jsonify({"message": "false"})


# 通过id删除指定的故事
@storyBlueprint.route('/deleteStory', methods=['POST'])
def deleteStory():
    data = json.loads(request.get_data())
    userName, ok = checkLoginMiddleware(data)
    if not ok:
        return jsonify({"message": "false"})
    # 调用service服务
    storyId = data["storyId"]
    ok = service.deleteStory(storyId)
    if ok:
        return jsonify({"message": "true"})
    return jsonify({"message": "false"})


# 通过故事id查找
# 返回值： 润色文本， 图片, 消息
@storyBlueprint.route('/getByStoryId', methods=['POST'])
def getByStoryId():
    data = json.loads(request.get_data())
    userName, ok = checkLoginMiddleware(data)
    if not ok:
        return jsonify({"message": "false"})
    # 调用service服务
    storyId = data["storyId"]
    texts, urls, ok = service.getStory(storyId)
    if ok:
        return jsonify({"texts": texts, "urls": urls, "message": "true"})
    return jsonify({"texts": None, "urls": None, "message": "false"})


# 重画当前页
# 参数：故事id，当前页数（标题为第0页）
@storyBlueprint.route('/updateCurrentPicture', methods=['POST'])
def updateCurrentPicture():
    data = json.loads(request.get_data())
    userName, ok = checkLoginMiddleware(data)
    if not ok:
        return jsonify({"message": "false"})
    # 调用service服务
    storyId = data["storyId"]
    current = data['current']
    # 重画当前页————(新的页面，是否成功)
    newPage, ok = service.updateCurrentPicture(storyId, int(current))
    if ok:
        return jsonify({"newPage": newPage[0], "message": "true"})
    return jsonify({"newPage": None, "message": "false"})


# 大纲+用户需求重新制作，类似generateStory函数
# 参数：用户名+用户的需求
# 返回值：(新故事id, true)
#       (None, false)
@storyBlueprint.route('/generateNewStory', methods=['POST'])
def generateNewStory():
    data = json.loads(request.get_data())
    userName, ok = checkLoginMiddleware(data)
    if not ok:
        return jsonify({"message": "false"})
    # 调用service服务
    storyId = data["storyId"]
    requirement = data['requirement']
    storyId, ok = service.generateNewStory(userName, storyId, requirement)
    if ok:
        print(jsonify({"storyId": storyId, "message": "true"}))
        return jsonify({"storyId": storyId, "message": "true"})
    print(jsonify({"storyId": None, "message": "false"}))
    return jsonify({"storyId": None, "message": "false"})


# 获取用户所有的故事id
@storyBlueprint.route('/getAllStory', methods=['POST'])
def getAllStory():
    data = json.loads(request.get_data())
    userName, ok = checkLoginMiddleware(data)
    print(userName)
    if not ok:
        return jsonify({"message": "false"})
    # 调用service服务
    res, ok = service.getAllStory(userName)
    if ok:
        return jsonify({"title": res[0], "cover": res[1], "message": "true", "storyId": res[2]})
    return jsonify({"title": "", "cover": "", "message": "false", "storyId": None})
