# Fundix


A robust, multi-threaded, terminal-based chat room application built with Python. This project features a full client-server architecture where multiple clients can connect to a central server, authenticate (Sign Up/Login), and exchange messages in a unified public chat room in real-time.

## Features

### Core Functionality

* **Centralized Server:** A single server acts as the hub, managing all connections and broadcasting messages to active users.
* **Real-Time Messaging:** Messages are delivered instantly to all connected clients using TCP sockets.
* **Multi-User Support:** The server uses **threading** to handle multiple clients simultaneously without blocking.

### User Management & Security

* **Persistent Accounts:** User credentials are stored in a local SQLite database (`chat_users.db`), meaning accounts survive server restarts.
* **Unique Usernames:** The server enforces username uniqueness, rejecting registration attempts for names that already exist.
* **Secure Authentication:** Passwords are **never** stored in plain text. The application uses **SHA-256 hashing with unique salts** for every user, following security best practices.
* **Login/Signup Flow:** A strict "gatekeeper" mechanism ensures users cannot access the chat room or see messages until they successfully authenticate.

### Technical Implementation

* **JSON Protocol:** Communication between client and server uses a custom line-delimited JSON protocol, ensuring structured and reliable data exchange.
* **Standard Library Only:** Built entirely with Python's standard library (`socket`, `threading`, `sqlite3`, `json`, `hashlib`)—no `pip install` required!

---

## Prerequisites

* **Python 3.x** installed on your system.
* A terminal or command prompt (Command Prompt, PowerShell, Terminal, etc.).

---

## Installation & Setup

1. **Clone or Download the Code:**
You can clone the repository or save the server code as `server.py` and the client code as `client.py`.
2. **Directory Structure:**
Ensure both files are in the same directory.
```text
/fundix
├── server.py
└── client.py

```



---

## Usage Guide

### 1. Starting the Server

The server must be running before any clients can connect.

1. Open your terminal.
2. Navigate to the directory containing the scripts.
3. Run the server:
```bash
python server.py

```


*You will see a message: `[LISTENING] Server is listening on 127.0.0.1:55555*`
*Note: On the first run, this will automatically create the `chat_users.db` file.*

### 2. Connecting a Client

1. Open a **new** terminal window (keep the server running in the first one).
2. Run the client:
```bash
python client.py

```


3. You will be greeted with the authentication menu.

### 3. Authentication (Login / Signup)

The app restricts chat access until you authenticate.

* **To Create an Account:**
* Select option `2` (Signup).
* Enter a unique **Username**.
* Enter a **Password**.
* *If the username is available, you will be automatically logged in and redirected to the chat.*


* **To Login:**
* Select option `1` (Login).
* Enter your existing credentials.
* *If valid, you will join the chat room.*



### 4. Chatting

* Once logged in, simply type your message and press **Enter**.
* Your message will appear on all other connected clients' screens instantly.
* Incoming messages appear with the sender's username: `[Alice]: Hello everyone!`
* Type `exit` to leave the chat and close the program.

---

## Technical Architecture

### The Protocol

The application uses a **Line-Delimited JSON** protocol over TCP sockets.

* **Why JSON?** It allows us to send complex data structures (like distinguishing between a `login` command and a `message` command) easily.
* **Why Line-Delimited?** TCP is a stream protocol; it doesn't know where one message ends and another begins. We use the newline character `\n` as a delimiter so the receiver knows exactly when a packet is complete.

**Example Packet (Client -> Server):**

```json
{"command": "login", "username": "admin", "password": "secretpassword"}

```

**Example Packet (Server -> Client):**

```json
{"sender": "server", "content": "Welcome to the chat!"}

```

### Database Schema

The SQLite database `chat_users.db` contains a single table `users`:

| Column | Type | Description |
| --- | --- | --- |
| `username` | TEXT (PK) | The unique identifier for the user. |
| `password_hash` | TEXT | The SHA-256 hash of the password + salt. |
| `salt` | TEXT | A random 16-byte hex string generated per user. |

### Concurrency Model

* **Server:** Uses `threading.Thread` to spawn a new thread for every connected client `handle_client()`. This ensures that one user's slow network doesn't block others.
* **Client:** Uses two threads:
1. **Main Thread:** Handles user input and sending messages.
2. **Listener Thread:** Constantly waits for incoming data from the server and prints it to the screen.



---

## Troubleshooting

**Issue: "ConnectionRefusedError: [WinError 10061] No connection could be made..."**

* **Cause:** The client is trying to connect, but the server isn't running.
* **Fix:** Ensure you ran `python server.py` in a separate terminal window first.

**Issue: "Address already in use"**

* **Cause:** You closed the server script abruptly, but the OS hasn't released the port (55555) yet, or another instance is running.
* **Fix:** Wait a minute and try again, or manually kill the lingering python process.

**Issue: Messages are overwriting the input line**

* **Cause:** This is a limitation of standard terminal I/O. When an incoming message arrives while you are typing, it might visually disrupt your current input line.
* **Fix:** The code includes a reprompt `You: ` after every message to minimize this, but a full TUI (Text User Interface) library like `curses` would be needed to fix it completely (outside the scope of a standard-library-only project).

---

## License

This project is open-source and free to use for educational purposes. Feel free to modify and expand upon it!
