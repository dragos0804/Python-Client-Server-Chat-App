import streamlit as st
import requests
import time
from datetime import datetime

class HttpClient:
    def __init__(self, base_url):
        self.base_url = base_url

    def get(self, endpoint, params=None):
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            st.error(f"Error connecting to server: {str(e)}")
            return None

    def post(self, endpoint, data=None, json=None):
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.post(url, data=data, json=json)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            st.error(f"Error connecting to server: {str(e)}")
            return None

def send_message(client, from_user, to_user, message_text):
    if message_text.strip():
        payload = {
            "from": from_user,
            "to": to_user,
            "message": message_text
        }
        response = client.post("/messages", json=payload)
        if response and response.status_code == 200:
            return True
    return False

def main():
    st.title("WhatsApp Clone")

    # Initialize session state
    if 'user_id' not in st.session_state:
        st.session_state.user_id = ''

    base_url = "http://localhost:5000/api"
    client = HttpClient(base_url)

    # User registration
    if not st.session_state.user_id:
        st.subheader("Register")
        user_id = st.text_input("Choose your User ID")
        if st.button("Register"):
            response = client.post("/users", json={"user_id": user_id})
            if response and response.status_code == 200:
                st.session_state.user_id = user_id
                st.success(f"Registered as {user_id}")
                st.rerun()

    else:
        # Chat interface
        st.sidebar.write(f"Logged in as: {st.session_state.user_id}")
        
        # Get available users
        response = client.get("/users")
        if response:
            available_users = [user for user in response.json() if user != st.session_state.user_id]
            
            # Select chat partner
            chat_with = st.sidebar.selectbox("Chat with:", available_users) if available_users else None

            if chat_with:
                # Message input and send button
                st.subheader(f"Chat with {chat_with}")
                
                # Create a form for message input
                with st.form(key='message_form'):
                    message = st.text_input("Type your message")
                    submit_button = st.form_submit_button("Send")
                    
                    if submit_button:
                        if send_message(client, st.session_state.user_id, chat_with, message):
                            st.success("Message sent!")
                
                # Display messages
                response = client.get(f"/messages/{st.session_state.user_id}")
                if response:
                    messages = response.json()
                    
                    # Filter messages for current chat
                    chat_messages = [
                        msg for msg in messages 
                        if (msg['from'] == st.session_state.user_id and msg['to'] == chat_with) or 
                           (msg['from'] == chat_with and msg['to'] == st.session_state.user_id)
                    ]
                    
                    # Display messages in a container
                    message_container = st.container()
                    with message_container:
                        for msg in reversed(chat_messages):
                            is_user = msg['from'] == st.session_state.user_id
                            st.write(
                                f"<div style='text-align: {'right' if is_user else 'left'};'>"
                                f"<div style='background-color: {'#274e13' if is_user else '#444444'}; "
                                f"padding: 10px; border-radius: 10px; display: inline-block; max-width: 70%;'>"
                                f"<small>{'You' if is_user else msg['from']}</small><br>"
                                f"{msg['message']}<br>"
                                f"<small>{datetime.fromisoformat(msg['timestamp']).strftime('%H:%M')}</small>"
                                f"</div></div>",
                                unsafe_allow_html=True
                            )

                # Auto-refresh
                time.sleep(10)
                st.rerun()
            else:
                st.info("No other users available to chat with.")
        else:
            st.error("Could not connect to server")

if __name__ == "__main__":
    main()