import bcrypt
from repository.user import userRepo
import os
from werkzeug.utils import secure_filename
from tools.saveImageToLocal import saveImageToLocal
from tools.saveImageToRemote import saveImageToRemote

def signup(user):
    # 加密密码
    user.password = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt(rounds=10))
    # 调用repository服务
    res = userRepo.create(user)
    if res == "OK":
        # 注册成功
        return True
    else:
        # 用户名重复
        return False


def login(name, password):
    user, ok = userRepo.findByName(name)
    if ok and bcrypt.checkpw(password.encode(), user.password.encode()):
        return True
    return False


def upload(userName, image):
    # 找到对应的用户
    user, ok = userRepo.findByName(userName)
    # 将图片保存到本地
    path = saveImageToLocal(image)
    if ok and len(path) != 0:
        # 将图片上传至七牛云并获取其URL
        avatar_url = saveImageToRemote(path)
        # 设置用户的头像URL数据
        user.avatar = avatar_url
        message, ok = userRepo.update(user)
        return ok
    return False
