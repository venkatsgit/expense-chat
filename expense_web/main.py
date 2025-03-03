import streamlit as st
import requests

# Keycloak Configuration
KEYCLOAK_SERVER = "http://localhost:8080"
REALM_NAME = "myrealm"
CLIENT_ID = "myclient"

TOKEN_URL = f"{KEYCLOAK_SERVER}/realms/{REALM_NAME}/protocol/openid-connect/token"
USERINFO_URL = f"{KEYCLOAK_SERVER}/realms/{REALM_NAME}/protocol/openid-connect/userinfo"
UPLOAD_URL = "http://127.0.0.1:5000/api/csv/expenses"
CHAT_URL = "http://127.0.0.1:5000/api/chat"

st.title("Expense Insight")

if "access_token" not in st.session_state:

    username = st.text_input("Username", placeholder="Enter your username")
    password = st.text_input("Password", type="password", placeholder="Enter your password",
                             help="Your credentials will be securely sent to Keycloak.")
  
    if st.button("Login"):
        data = {
            "client_id": CLIENT_ID,
            "grant_type": "password",
            "username": username,
            "password": password,
        }

        st.session_state["access_token"] = "test_token"
        st.success("Login successful!")
        st.rerun()
        # response = requests.post(TOKEN_URL, data=data)

        # if response.status_code == 200:
        #     token_data = response.json()
        #     access_token = token_data.get("access_token")
        #     st.session_state["access_token"] = "access_token"
        #     st.success("Login successful!")
        #     st.rerun()
        # else:
        #     st.error("Login failed! Please check your username and password.")
else:
    st.switch_page("pages/chat_prompt.py")
    