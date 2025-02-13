import time
from qiniu import Auth, put_file


def saveImageToRemote(localPath):
    q = Auth('cM6U33jhHN7AUD8rRvDD5_Zlwz-f6D3bjNkA3XbS', 'opTDfX8pX20YLEz1GM0_j8GJB50PE5VitRTmKC-Z')
    bucket_name = 'aigcpic'
    # 唯一命名图片
    key = time.time().__str__() + '.jpg'
    token = q.upload_token(bucket_name, key)
    ret, info = put_file(token, key, localPath)
    # 获取图片url
    image_url = 'http://sgn5bipd4.hn-bkt.clouddn.com/' + ret.get('key')
    return image_url
