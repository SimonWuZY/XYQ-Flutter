from flask import Flask
from web import userHandler, storyHandler

app = Flask(__name__)
app.register_blueprint(storyHandler.storyBlueprint)
app.register_blueprint(userHandler.userBlueprint)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1888)
