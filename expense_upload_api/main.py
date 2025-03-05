from flask import Flask
from db import init_db, close_db
from api import api_bp
import os


app = Flask(__name__)

app.config["MYSQL_HOST"] = os.getenv("MYSQL_HOST", "34.93.134.131")
app.config["MYSQL_PORT"] = int(os.getenv("MYSQL_PORT", 3306))
app.config["MYSQL_USER"] = os.getenv("MYSQL_USER", "remote_user")
app.config["MYSQL_PASSWORD"] = os.getenv("MYSQL_PASSWORD", "Str0ng@Pass123")
app.config["MYSQL_DB"] = os.getenv("MYSQL_DB", "expense_insights")

init_db(app)
app.register_blueprint(api_bp, url_prefix="/api")


@app.route('/health')
def home():
    return "Hello, Flask!"

# app.teardown_appcontext(close_db)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8081, debug=False)
