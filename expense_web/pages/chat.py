import streamlit as st
import requests
from menu import menu_with_redirect
from config import CHAT_URL

menu_with_redirect()

st.header("Chat")
query = st.text_area(label="Queries", value="")
if st.button("Submit Query"):
    headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}
    data = {"query": query}
    response = requests.post(CHAT_URL, json=data, headers=headers)

    if response.status_code == 200:
        response = response.json()
        st.write("Response:", response['reply'])
    else:
        st.error("Query submission failed!")
