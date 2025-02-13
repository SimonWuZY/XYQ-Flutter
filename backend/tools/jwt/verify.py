import jwt
from repository.dao import userDAO

def verify(jwt_token):
    token_dict = None
    try:
        token_dict = jwt.decode(jwt_token, "zhananbudanchou1234678", algorithms=['HS256'])
        userName = token_dict['userName']
        if userName == "":
            return "", False
        user, ok = userDAO.findByName(userName)
        if ok and userName == user[1]:
            return userName, True
        else:
            return "", False
    except Exception as e:
        print(e)
        return "", False
