import time
import jwt


def generate_jwt_token(userName):
    token_dict = {
        'userName': userName
    }
    headers = {
        'alg': "HS256",  # 声明所使用的算法
    }
    jwt_token = jwt.encode(token_dict,  # payload, 有效载体
                       "zhananbudanchou1234678",  # 进行加密签名的密钥
                       algorithm="HS256",  # 指明签名算法方式, 默认也是HS256
                       headers=headers  # json web token 数据结构包含两部分, payload(有效载体), headers(标头)
                       )  # python3 编码后得到 bytes, 再进行解码(指明解码的格式), 得到一个str
    return jwt_token
