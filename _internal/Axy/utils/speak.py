# axy/utils/speak.py
def Speak(text: str, sender: str = "Axy"):
    import streamlit as st
    if "messages" not in st.session_state:
        return
    st.session_state.messages.append({
        "role": "assistant",
        "content": text
    })
    # Auto-scroll handled by Streamlit