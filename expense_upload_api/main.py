from flask import Flask

upload_app = Flask(__name__)

@upload_app.route('/')
def home():
    return "This is upload"