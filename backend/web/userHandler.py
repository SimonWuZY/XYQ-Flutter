import re

from flask import Blueprint, json, request, jsonify
from service.user import service
from tools.jwt import generate
from tools.jwt.verify import verify
from domain.user import User
from service import story

userBlueprint = Blueprint('user', __name__, url_prefix='/users')


@userBlueprint.route('/signup', methods=['POST'])
def signup():
    # 获取前端json数据
    data = json.loads(request.get_data())
    # 获取数据
    name = data["userName"]
    password = data["password"]
    print(name, password)

    # 校验数据
    res = re.search('^[a-zA-Z0-9]{6,20}$', name)
    # 不符合规则
    if not res:
        return jsonify({"message": "Username must be 6-20 digits of letters or numbers"})
    res = re.search('^[a-zA-Z0-9@#$%^&*]{8,20}$', password)
    if not res:
        return jsonify({"message": "Password must be 8-20 digits of letters or numbers"})

    # 调用 service 服务
    res = service.signup(User(name, password, ""))
    if res:
        story.service.initUserStory(name)
        return jsonify({"message": "signup success"})
    else:
        return jsonify({"message": "duplicate userName"})


@userBlueprint.route('/login', methods=['POST'])
def login():
    data = json.loads(request.get_data())
    userName = data["userName"]
    password = data["password"]
    res = service.login(userName, password)
    if res:
        jwt_token = generate.generate_jwt_token(userName)
        print(jwt_token)
        return jsonify({"message": "login success","token": jwt_token})
    else:
        return jsonify({"message": "username not found or invalid password"})


@userBlueprint.route('/profile', methods=['GET'])
def getProfile():
    data = json.loads(request.get_data())
    jwt_token = data['token']
    userName, ok = verify(jwt_token)
    if ok:
        print(userName)
    else:
        print("invalid")
    return jsonify({"userName": userName})


@userBlueprint.route('/upload', methods=['POST'])
def upload():
    if 'token' not in request.files:
        return jsonify("{'message': 'token is empty'}")
    jwt_token = request.files['token'].read()
    print(jwt_token)
    # data = json.loads(request.get_data())
    # if len(data) == 0:
    #     return jsonify({"message": "token is empty"})
    # jwt_token = data['token']
    userName, ok = verify(jwt_token)
    if ok:
        if 'image' not in request.files:
            return jsonify({"message": "No file part"})
        image = request.files['image']
        if image.filename == '':
            return jsonify({"message": "No selected file"})
        ok = service.upload(userName, image)
        if ok:
            return jsonify({"message": "uploaded successfully"})
        return jsonify({"message": "fail"})
    return jsonify({"message": "fail"})
