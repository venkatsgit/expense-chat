import streamlit as st

def authenticated_menu():
    with st.sidebar:
        st.title("Navigation")
        st.sidebar.page_link("pages/chat_prompt.py", label="Chat")
        st.sidebar.page_link("pages/upload.py", label="Upload")
        st.sidebar.page_link("pages/upload_history.py", label="Upload History")

        st.write("")
        st.write("")

        logout_placeholder = st.empty()

        if logout_placeholder.button("Logout"):
            del st.session_state["access_token"]
            st.rerun()


def unauthenticated_menu():
    st.sidebar.page_link("main.py", label="Log in")

def menu():
    if "access_token" not in st.session_state:
        unauthenticated_menu()
        return
    authenticated_menu()


def menu_with_redirect():
    if "access_token" not in st.session_state:
        st.switch_page("main.py")
    menu()