from flask import Flask, request, jsonify,g
from db import init_db, close_db
from db import get_db
import os
import jwt
import requests
import json
import config
from sqlchain import get_few_shot_db_chain

app = Flask(__name__)

app.config["MYSQL_HOST"] = os.getenv("MYSQL_HOST", "mysql")
app.config["MYSQL_PORT"] = int(os.getenv("MYSQL_PORT", 3306))
app.config["MYSQL_USER"] = os.getenv("MYSQL_USER", "remote_user")
app.config["MYSQL_PASSWORD"] = os.getenv("MYSQL_PASSWORD", "Str0ng@Pass123")
app.config["MYSQL_DB"] = os.getenv("MYSQL_DB", "expense_insights")

init_db(app)


@app.route('/health')
def home():
    return "Hello, Flask!"


#@app.before_request
def check_token():
    if request.endpoint != "health":
        try:
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return jsonify({"error": "Missing or invalid Authorization header"}), 401
            token = auth_header.split(" ")[1]
            headers = {
                "Authorization": f"Bearer {token}"
            }
            response = requests.get(
                "https://www.googleapis.com/oauth2/v1/userinfo", headers=headers)
            if response.status_code == 200:
                response_json = response.json()
                g.user_id = response_json['id']
            else:
                return jsonify({"error": "Missing or invalid Authorization header"}), 401

        except Exception as e:
            return jsonify({"error": "Invalid or missing token"}), 401


@app.route('/chatbot', methods=['POST'])
def chat():
    print ("chatbot api endpoint invoked")
    if request.json and request.json['question']: # and g.get('user_id'):

        user_id = g.get('user_id')
        user_query = request.json['question']
        question = f"""  
            You are an AI assistant. Convert DB responses into human-like summaries.  

            **TABLE:** `expense_insights.expenses`  
            - Tracks `expense`, `currency_code`, `description`, `category`, and `date`.  

            **Question:** "{user_query}, for user_id={user_id}?"  

            **Rules (STRICTLY FOLLOW):**  
            - **Return only executable SQL queries, no full data dumps.**  
            - **NO UPDATE/DELETE queries.**  
            - **Apply `currency_code` as a dimension, not as a filter in WHERE.**  
            - **Apply `date` filter ONLY IF the user explicitly mentions a date range or specific date.**  
            - **Restrict strictly to `user_id={user_id}`.**  
            - **Use `category` when relevant.**  
            - **Convert timestamps to GMT for date queries.**  
            - **Use regex for `description` if needed.**  
            - **NEVER query without a limit.**  
            - **STRICTLY follow response format.**  

            **Response Format:**  
            - **Valid query → \"{{\\\"query\\\":\\\"SQL_QUERY\\\"}}\"**  
            - **Invalid question → \"{{\\\"error_message\\\":\\\"Error message\\\"}}\"**  

            Now, generate the response:
        """

    response = google_ai(question)
    initial_resp_text = response.text
    data = json.loads(response.text)
    data = data["candidates"][0]["content"]
    query_text = data["parts"][0]["text"]

    query_text = query_text.replace("```sql", "").replace("```", "").strip()
    query_text = query_text.replace("```json", "").replace("```", "").strip()
    query_text = query_text.replace("json", "").replace("```", "").strip()
    query_json = json.loads(query_text)
    if 'query' in query_json:
        query_text = query_json['query']
    elif 'error_message' in query_json:
        return jsonify({'status': 'success', 'answer': query_json['error_message']}), 200
    else:
        return jsonify({'status': 'success', 'answer': 'Error occured'}), 200
    db, cursor = get_db()
    query_response = cursor.execute(query_text)
    query_response = cursor.fetchall()
    cursor.close()

    formatted_response = f"""
    You are an AI assistant. Convert the database response into a natural, human-readable summary.

    ### Database Table: `expenses`
    The database stores user expenses with details like amount, currency, description, category, and date.

    ### Instructions:
    - **Do NOT return the SQL query.**
    - **Do NOT disclose SQL column names or database structure.**
    - **Do NOT include `user_id` in the response.**
    - Keep the response conversational, concise, and user-friendly.
    - **Strictly restrict `UPDATE` and `DELETE` queries**—if detected, respond negatively.
    - If the query is unrelated to the question, do not return the database response.
    - Convert Unix timestamps into readable date formats.
    - The "description" field represents where the user spent money.
    - **Avoid making conclusions due to limited data.**
    - **Do NOT start responses with 'Okay'.**

    ### Example Behavior:
    - If expenses exist:  
      - **"You've spent $500 USD on food and rent."**
      - **"You've spent $500 USD and €300 EUR on food and rent."** (if multiple currencies)
    - If no expenses exist:  
      - **"Looks like you haven't recorded any expenses for food or rent yet."**

    ### Input:
    - **User Question:** {question}
    - **Database Response:** {query_response}

    Now, generate the response:
    """

    response = google_ai(formatted_response)
    data = json.loads(response.text)
    # print(data)
    data = data["candidates"][0]["content"]
    query_text = data["parts"][0]["text"]

    return jsonify({'status': 'success', 'answer': query_text}), 200


def google_ai(text):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=AIzaSyAetG3Sl0UVG3InmMLz0DWAPFJrG41sBJg"

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": text
                    }
                ]
            }
        ]
    }
    return requests.post(url, json=payload)

@app.route('/chatbot_v1', methods=['POST'])
def chat_v1():
    user_query = request.json['question']
    chain = get_few_shot_db_chain()
    response = chain.run("{user_query}, for user_id=106659949639075966002?")


app.teardown_appcontext(close_db)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8083, debug=False)
