import streamlit as st
import requests
import pandas as pd
from menu import menu_with_redirect
from config import UPLOAD_HISTORY_URL

menu_with_redirect()

st.header("Upload History")

try:
    headers = {
        "Authorization": f"Bearer {st.session_state['access_token']}"}
    response = requests.get(UPLOAD_HISTORY_URL, headers=headers)
    if response.status_code == 200:
        response_data = response.json()
        df = pd.DataFrame(response_data["data"])
        df = df[["file_name", "status", "message", "uploaded_at"]]
        df = df.rename(columns={
            "file_name": "File",
            "status": "Status",
            "message": "Message",
            "uploaded_at": "Upload date"
        })
        st.dataframe(df, width=900, height=600)
    else:
        st.error("error!")
except Exception as e:
    print(e)
    st.error("error!")
