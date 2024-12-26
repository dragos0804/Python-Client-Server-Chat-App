from flask import Flask, request, jsonify
from datetime import datetime
import threading

app = Flask(__name__)

# In-memory storage
messages = []
users = set()

@app.route('/api/messages', methods=['POST'])
def send_message():
    data = request.json
    message = {
        'from': data['from'],
        'to': data['to'],
        'message': data['message'],
        'timestamp': datetime.now().isoformat()
    }
    messages.append(message)
    return jsonify({'status': 'success', 'message': 'Message sent'})

@app.route('/api/messages/<user_id>', methods=['GET'])
def get_messages(user_id):
    user_messages = [
        msg for msg in messages 
        if msg['to'] == user_id or msg['from'] == user_id
    ]
    return jsonify(user_messages)

@app.route('/api/users', methods=['POST'])
def register_user():
    data = request.json
    user_id = data['user_id']
    users.add(user_id)
    return jsonify({'status': 'success', 'message': f'User {user_id} registered'})

@app.route('/api/users', methods=['GET'])
def get_users():
    return jsonify(list(users))

if __name__ == '__main__':
    app.run(port=5000)