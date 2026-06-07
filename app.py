from flask import Flask, render_template_string
from flask_socketio import SocketIO, emit
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cisco-fy27-socket-secret'

# Initialize SocketIO to handle real-time WebSockets with Cross-Origin support
socketio = SocketIO(app, cors_allowed_origins="*")

# The unified HTML/CSS/JS frontend interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>SecureStream | Team Chat</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #1e1e1e; color: #d4d4d4; margin: 0; padding: 0; display: flex; justify-content: center; align-items: center; height: 100vh; }
        #chat-container { width: 100%; max-width: 700px; background-color: #252526; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); display: flex; flex-direction: column; height: 85vh; overflow: hidden; border: 1px solid #333; }
        #header { background-color: #007acc; color: white; padding: 15px; text-align: center; font-weight: bold; letter-spacing: 1px; }
        #messages { flex: 1; padding: 20px; overflow-y: auto; display: flex; flex-direction: column; gap: 10px; }
        .message { background-color: #3e3e42; padding: 10px 15px; border-radius: 5px; word-wrap: break-word; }
        .system-msg { color: #4CAF50; font-size: 0.85em; text-align: center; font-style: italic; }
        .user-tag { font-weight: bold; color: #569cd6; margin-right: 5px; }
        .time-tag { font-size: 0.75em; color: #858585; float: right; }
        #input-area { display: flex; padding: 15px; background-color: #2d2d30; border-top: 1px solid #3e3e42; }
        input[type="text"] { flex: 1; padding: 10px; border: 1px solid #3e3e42; border-radius: 4px; background-color: #1e1e1e; color: #d4d4d4; outline: none; }
        input[type="text"]:focus { border-color: #007acc; }
        button { padding: 10px 20px; margin-left: 10px; background-color: #007acc; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; }
        button:hover { background-color: #005f9e; }
    </style>
    <!-- Load the Socket.IO client library -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
</head>
<body>

<div id="chat-container">
    <div id="header">SecureStream - Global Engineering Channel</div>
    <div id="messages"></div>
    <div id="input-area">
        <input type="text" id="username" placeholder="Your Name" style="width: 20%; margin-right: 10px;">
        <input type="text" id="message" placeholder="Type a secure message...">
        <button onclick="sendMessage()">Send</button>
    </div>
</div>

<script>
    const socket = io();
    const messagesDiv = document.getElementById('messages');
    const msgInput = document.getElementById('message');
    const userInput = document.getElementById('username');

    // Secure Coding Practice: Simulate client-side payload encoding
    function encodePayload(str) { return btoa(str); }
    function decodePayload(str) { try { return atob(str); } catch(e) { return str; } }

    socket.on('connect', () => {
        appendSystemMessage('System: TCP connection established. WebSockets active.');
    });

    socket.on('disconnect', () => {
        appendSystemMessage('System: Connection to routing server lost.');
    });

    // Listen for incoming broadcast messages from the server
    socket.on('broadcast_message', (data) => {
        const decodedMsg = decodePayload(data.payload);
        const msgElement = document.createElement('div');
        msgElement.className = 'message';
        msgElement.innerHTML = `<span class="time-tag">${data.timestamp}</span><span class="user-tag">${data.user}:</span> ${decodedMsg}`;
        messagesDiv.appendChild(msgElement);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    });

    function sendMessage() {
        const user = userInput.value.trim() || 'Guest_Engineer';
        const msg = msgInput.value.trim();
        if (msg) {
            const encodedMsg = encodePayload(msg);
            // Push the data packet to the server via WebSocket
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
    }
</script>
</body>
</html>
"""

@app.route('/')
def home():
    # Serve the frontend interface to the user's browser
    return render_template_string(HTML_TEMPLATE)

@socketio.on('send_message')
def handle_message(data):
    # Server receives the incoming packet, tags it with a timestamp,
    # and instantly broadcasts it to every single connected client thread.
    timestamp = datetime.now().strftime('%H:%M:%S')
    
    emit('broadcast_message', {
        'user': data.get('user', 'Unknown'),
        'payload': data.get('payload', ''),
        'timestamp': timestamp
    }, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
