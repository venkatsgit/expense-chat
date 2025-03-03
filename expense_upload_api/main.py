from flask import Flask
from db import init_db, close_db
from api import api_bp
import os


app = Flask(__name__)

app.config["MYSQL_HOST"] = os.getenv("MYSQL_HOST", "localhost")
app.config["MYSQL_PORT"] = int(os.getenv("MYSQL_PORT", 3306))
app.config["MYSQL_USER"] = os.getenv("MYSQL_USER", "root")
app.config["MYSQL_PASSWORD"] = os.getenv("MYSQL_PASSWORD", "root")
app.config["MYSQL_DB"] = os.getenv("MYSQL_DB", "expense_insights")

init_db(app)
app.register_blueprint(api_bp, url_prefix="/api") 



@app.route('/health')
def home():
    return "Hello, Flask!"

app.teardown_appcontext(close_db)

if __name__ == '__main__':
    app.run(debug=True)
