import streamlit as st
from streamlit_oauth import OAuth2Component
import requests
import json
from db_util import update_user_db

CLIENT_ID = "1095140358158-ct17rj6hkj4i45kvvspt2l7hknim2ecd.apps.googleusercontent.com"
CLIENT_SECRET = "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"
AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
REVOKE_URL = "https://oauth2.googleapis.com/revoke"
REDIRECT_URI = "http://localhost:8501"
SCOPE = "openid email profile"

oauth2 = OAuth2Component(CLIENT_ID, CLIENT_SECRET, AUTHORIZE_URL, TOKEN_URL, REVOKE_URL)

def get_user_info(token):
    headers = {
        "Authorization": f"Bearer {token['access_token']}"
    }
    response = requests.get("https://www.googleapis.com/oauth2/v1/userinfo", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to fetch user information.")
        return None

if 'token' in st.query_params:
    token_json = st.query_params['token']
    token_json = json.loads(token_json)
    st.session_state.token = token_json
    st.session_state.access_token = token_json['access_token']

if 'token' not in st.session_state:
    st.markdown("<h1>Welcome to <b style='color: #ff4b4b;'>Expense insight</b></h1>", unsafe_allow_html=True)
    result = oauth2.authorize_button(
        name="Login with Google",
        redirect_uri=REDIRECT_URI,
        scope=SCOPE,
        key="google_login"
    )

    if result and 'token' in result:
        st.session_state.token = result['token']
        st.session_state.access_token =  result['token']['access_token']
        st.query_params['token'] = json.dumps(result['token'])
        st.rerun()
else:
    token = st.session_state.token
    user_info = get_user_info(token)

    if user_info:
        update_user_db(user_info)
        st.switch_page("pages/chat_prompt.py")

    if st.button("Logout"):
        del st.session_state.token
        del st.session_state.access_token
        del st.query_params['token']
        st.rerun()