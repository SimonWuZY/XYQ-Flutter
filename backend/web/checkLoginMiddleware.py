from tools.jwt.verify import verify


# 充当中间件，AOP
def checkLoginMiddleware(data):
    jwt_token = data["token"]
    return verify(jwt_token)
