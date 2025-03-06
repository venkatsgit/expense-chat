import streamlit as st
import requests
import pandas as pd
from menu import menu_with_redirect
from config import UPLOAD_HISTORY_URL

menu_with_redirect()

st.header("Upload History")

try:

    headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}
    response = requests.get(UPLOAD_HISTORY_URL, headers=headers)

    if response.status_code == 200:
        response_data = response.json()
        df = pd.DataFrame(response_data["data"])
        if not df.empty:
            df = df[["file_name", "status", "message", "uploaded_at"]]
            df.rename(columns={
                "file_name": "File",
                "status": "Status",
                "message": "Message",
                "uploaded_at": "Upload Date"
            }, inplace=True)
            df = df.reset_index(drop=True)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.warning("No upload history found.")
    else:
        st.error("Error fetching upload history!")
except Exception as e:
    st.error(f"An error occurred: {str(e)}")
