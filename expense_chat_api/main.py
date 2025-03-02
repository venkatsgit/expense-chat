from flask import Flask

chat_app = Flask(__name__)

@chat_app.route('/')
def home():
    return "This is chat"