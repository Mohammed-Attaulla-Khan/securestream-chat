# 🌐 SecureStream: Real-Time Encrypted Chat
**Live Demo:** [View SecureStream on Render](https://securestream-chat.onrender.com)

## Overview
SecureStream is a real-time, multithreaded group communication server engineered to handle concurrent user connections with ultra-low latency. It bridges responsive frontend design with persistent backend TCP/IP routing using WebSockets.

## 🚀 Key Features
* **Persistent Connections:** Replaces standard HTTP polling with WebSockets (`Flask-SocketIO`) for instantaneous, two-way data flow.
* **Asynchronous Multithreading:** Utilizes the `gevent` worker class to effortlessly manage dozens of concurrent user threads without blocking the main server loop.
* **Payload Security:** Implements a client-side encoding layer to simulate secure data transmission, safely handling complex Unicode characters and preventing raw-text interception.
* **State Synchronization:** Features an efficient in-memory data queue to cache the last 50 network messages, ensuring state synchronization for newly connected clients.

## 🛠️ Technical Stack
* **Backend:** Python 3, Flask, Flask-SocketIO
* **Cloud Deployment:** Render (AWS Infrastructure), Gunicorn, Gevent Worker Class
* **Frontend:** HTML5, CSS3, JavaScript, Socket.IO Client
