from expense_web.main import web_app
from expense_chat_api.main import chat_app
from expense_upload_api.main import upload_app
from multiprocessing import Process

def run_web_app():
    web_app.run(host='0.0.0.0', port=5000)

def run_chat_app():
    chat_app.run(host='0.0.0.0', port=5001)

def run_upload_app():
    upload_app.run(host='0.0.0.0', port=5002)

if __name__ == '__main__':
    # Start web on port 5000
    p1 = Process(target=run_web_app)
    p1.start()

    # Start chat on port 5001
    p2 = Process(target=run_chat_app)
    p2.start()

    # Start file upload on port 5002
    p3 = Process(target=run_upload_app)
    p3.start()