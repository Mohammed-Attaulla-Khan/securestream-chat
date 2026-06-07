from flask import Flask, render_template_string
from flask_socketio import SocketIO, emit
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cisco-fy27-socket-secret'
socketio = SocketIO(app, cors_allowed_origins="*")

# In-memory storage for chat history (holds the last 50 messages)
message_history = []

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0"> <!-- Added for mobile scaling -->
    <title>SecureStream | Team Chat</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #1e1e1e; color: #d4d4d4; margin: 0; padding: 0; display: flex; justify-content: center; align-items: center; height: 100vh; }
        #chat-container { width: 100%; max-width: 700px; background-color: #252526; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); display: flex; flex-direction: column; height: 100vh; max-height: 85vh; overflow: hidden; border: 1px solid #333; }
        #header { background-color: #007acc; color: white; padding: 15px; text-align: center; font-weight: bold; letter-spacing: 1px; }
        #messages { flex: 1; padding: 20px; overflow-y: auto; display: flex; flex-direction: column; gap: 10px; }
        .message { background-color: #3e3e42; padding: 10px 15px; border-radius: 5px; word-wrap: break-word; }
        .system-msg { color: #4CAF50; font-size: 0.85em; text-align: center; font-style: italic; margin-bottom: 5px; }
        .user-tag { font-weight: bold; color: #569cd6; margin-right: 5px; }
        .time-tag { font-size: 0.75em; color: #858585; float: right; margin-left: 10px; }
        #input-area { display: flex; padding: 15px; background-color: #2d2d30; border-top: 1px solid #3e3e42; gap: 10px; }
        input[type="text"] { padding: 10px; border: 1px solid #3e3e42; border-radius: 4px; background-color: #1e1e1e; color: #d4d4d4; outline: none; }
        #username { width: 80px; }
        #message { flex: 1; }
        input[type="text"]:focus { border-color: #007acc; }
        button { padding: 10px 20px; background-color: #007acc; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; }
        button:hover { background-color: #005f9e; }
        @media (max-width: 600px) {
            #chat-container { height: 100vh; max-height: 100vh; border-radius: 0; border: none; }
            #input-area { padding: 10px; }
            #username { width: 60px; }
        }
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
</head>
<body>

<div id="chat-container">
    <div id="header">SecureStream - Global Engineering Channel</div>
    <div id="messages"></div>
    <div id="input-area">
        <input type="text" id="username" placeholder="Name">
        <input type="text" id="message" placeholder="Type a secure message...">
        <button onclick="sendMessage()">Send</button>
    </div>
</div>

<script>
    const socket = io();
    const messagesDiv = document.getElementById('messages');
    const msgInput = document.getElementById('message');
    const userInput = document.getElementById('username');

    // Updated to handle emojis and unicode characters safely
    function encodePayload(str) { return btoa(encodeURIComponent(str)); }
    function decodePayload(str) { try { return decodeURIComponent(atob(str)); } catch(e) { return str; } }

    socket.on('connect', () => {
        appendSystemMessage('System: TCP connection established. WebSockets active.');
    });

    socket.on('disconnect', () => {
        appendSystemMessage('System: Connection to routing server lost. Retrying...');
    });

    // Load history when connecting
    socket.on('load_history', (history) => {
        history.forEach(data => {
            displayMessage(data);
        });
    });

    socket.on('broadcast_message', (data) => {
        displayMessage(data);
    });

    function displayMessage(data) {
        const decodedMsg = decodePayload(data.payload);
        const msgElement = document.createElement('div');
        msgElement.className = 'message';
        msgElement.innerHTML = `<span class="time-tag">${data.timestamp}</span><span class="user-tag">${data.user}:</span> ${decodedMsg}`;
        messagesDiv.appendChild(msgElement);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }

    function sendMessage() {
        const user = userInput.value.trim() || 'Guest';
        const msg = msgInput.value.trim();
        if (msg) {
            const encodedMsg = encodePayload(msg);
            socket.emit('send_message', { user: user, payload: encodedMsg });
            msgInput.value = '';
        }
    }

    msgInput.addEventListener('keypress', function (e) {
        if (e.key === 'Enter') sendMessage();
    });

    function appendSystemMessage(text) {
        const msgElement = document.createElement('div');
        msgElement.className = 'system-msg';
        msgElement.innerText = text;
        messagesDiv.appendChild(msgElement);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }
</script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@socketio.on('connect')
def handle_connect():
    # Send the stored history to the newly connected user
    emit('load_history', message_history)

@socketio.on('send_message')
def handle_message(data):
    timestamp = datetime.now().strftime('%H:%M:%S')
    msg_data = {
        'user': data.get('user', 'Unknown'),
        'payload': data.get('payload', ''),
        'timestamp': timestamp
    }
    
    # Save to history list
    message_history.append(msg_data)
    # Keep only the last 50 messages to save memory
    if len(message_history) > 50:
        message_history.pop(0)
        
    emit('broadcast_message', msg_data, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
