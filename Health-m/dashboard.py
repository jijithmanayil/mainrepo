import streamlit as st
from app import app

st.set_page_config(page_title="Health Chatbot", layout="wide")
st.title("🚀 Multi-Team Health Chatbot")

team_id = st.selectbox("Team", ["app-team-1", "app-team-2", "app-team-3"])
if "messages" not in st.session_state:
    st.session_state.messages = []

prompt = st.chat_input("Ask about Splunk, Dynatrace, Stonebranch...")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.write(prompt)
    
    with st.chat_message("assistant"):
        config = {"configurable": {"team_id": team_id}}
        for chunk in app.stream({"messages": [{"role": "user", "content": prompt}]}, config):
            st.write(chunk["messages"][-1].content)
    
    st.session_state.messages.append({"role": "assistant", "content": "Response"})

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
