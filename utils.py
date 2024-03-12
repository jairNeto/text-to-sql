import streamlit as st
from message import MessageFeedback

def insert_feedback(id, user_message, model_response, was_helpful, supabase_db) -> None:
    if was_helpful:
        feedback_content = ''
    else:
        feedback_content = st.session_state.feedback_content
    
    message_feedback = MessageFeedback(assistant_id=id,
                                        user_message=user_message,
                                        model_response=model_response,
                                        was_helpful=was_helpful,
                                        feedback_content=feedback_content)
    supabase_db.insert_message(message_feedback, 'MessageFeedback')

def display_feedback_buttons(message, user_message, supabase_db):
    col1, col2 = st.columns([0.1, 0.9])
    if col1.button("👍", key=f"thumbs_up_{message.id}"):
        insert_feedback(message.id, user_message.content, message.content, True, supabase_db) 
    if col2.button("👎", key=f"thumbs_down_{message.id}"):
        st.text_input("Please provide additional feedback:", on_change=insert_feedback, args=(message.id, user_message.content, message.content, False, supabase_db), key='feedback_content')
