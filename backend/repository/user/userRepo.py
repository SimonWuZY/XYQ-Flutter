from repository.dao import userDAO
from domain.user import User


def create(user):
    res = userDAO.insert(userDAO.User(user.userName, user.password, ""))
    return res


def findByName(name):
    res, ok = userDAO.findByName(name)
    if ok:
        # 用户名   密码  头像
        return User(res[1], res[2], res[3]), True
    return None, False


def update(user):
    print(user.userName, user.password, user.avatar, end='\n')
    return userDAO.update(userDAO.User(user.userName, user.password, user.avatar))
