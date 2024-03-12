import streamlit as st
import random
import time
import uuid

from database import SupabaseDB
from message import Message
from utils import display_feedback_buttons

supabase_db = SupabaseDB(st.secrets.get('SUPABASE_URL'), st.secrets.get('SUPABASE_KEY'))

st.title("Text to SQL Chatbot")
st.markdown("This is a demo of a chatbot that can answer questions about a database schema."
            "The chatbot is a llama-2 7B model, fine-tuned on bmc2")

# Initialize chat history
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []

for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message.role):
        st.markdown(message.content)
        if message.role == "assistant":
            if not supabase_db.has_feedback(message.id):
                user_message = st.session_state.messages[i-1]
                display_feedback_buttons(message, user_message, supabase_db)
            else:
                st.write(f"Feedback given: {'👍' if supabase_db.get_feedback(message.id) else '👎'}")


if prompt := st.chat_input("What is up?"):
    user_message = Message(role="user", content=prompt, conversation_id=st.session_state.conversation_id)
    supabase_db.insert_message(user_message)
    st.session_state.messages.append(user_message)

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        assistant_response = random.choice(
            [
                "Hello there! How can I assist you today?",
                "Hi, human! Is there anything I can help you with?",
                "Do you need help?",
            ]
        )
        # Simulate stream of response with milliseconds delay
        for chunk in assistant_response.split():
            full_response += chunk + " "
            time.sleep(0.05)
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)

    assistant_message = Message(role="assistant", content=full_response, conversation_id=st.session_state.conversation_id)
    supabase_db.insert_message(assistant_message)
    st.session_state.messages.append(assistant_message)
    st.rerun()
