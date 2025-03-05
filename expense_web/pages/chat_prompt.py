import streamlit as st
import requests
from menu import menu_with_redirect
from config import CHAT_URL

menu_with_redirect()

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

messages = st.container(height=400)

for msg in st.session_state["chat_history"]:
    messages.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("Say something"):
    st.session_state["chat_history"].append(
        {"role": "user", "content": prompt})
    messages.chat_message("user").write(prompt)

    headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}
    data = {"question": prompt , "userID": "1"}
    response = requests.post(CHAT_URL, json=data, headers=headers)

    if response.status_code == 200:
        response_data = response.json()
        ai_reply = response_data['answer']
        st.session_state["chat_history"].append(
            {"role": "assistant", "content": ai_reply})
        messages.chat_message("assistant").write(ai_reply)
    else:
        st.error("Query submission failed!")
