import streamlit as st
import requests
from menu import menu_with_redirect
from config import UPLOAD_URL
import traceback

menu_with_redirect()

st.header("Upload")
uploaded_file = st.file_uploader("Choose a file", type=["csv"])
if uploaded_file is not None:
    try:
        files = {"file": (uploaded_file.name,
                          uploaded_file.getvalue(), uploaded_file.type)}
        headers = {
            "Authorization": f"Bearer {st.session_state['access_token']}"}
        data = {"file_name": "expenses"}
        response = requests.post(UPLOAD_URL, files=files,
                                 data=data, headers=headers)
        if response.status_code == 200:
            st.success("File uploaded successfully!")
        else:
            st.error(f"An error occurred: {str(response.status_code)}")
            st.error(" File upload failed! invalid response code")
    except Exception as e:
        st.error("File upload failed!")
        st.error(f"An error occurred: {str(e)}")
        st.text(traceback.format_exc())  # Display the full traceback
