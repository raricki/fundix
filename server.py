import socket
import threading
import json
import sqlite3
import hashlib
import os

# Configuration
HOST = '127.0.0.1'
PORT = 55556
DB_NAME = "chat_users.db"

# Global list of connected clients (sockets)
clients = []
clients_lock = threading.Lock()

def init_db():
    """Initialize the SQLite database for users."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password_hash TEXT,
            salt TEXT
        )
    ''')
    conn.commit()
    conn.close()

def hash_password(password, salt=None):
    """Hash a password with a salt."""
    if not salt:
        salt = os.urandom(16).hex()
    # Use sha256 with the salt
    hashed = hashlib.sha256((password + salt).encode()).hexdigest()
    return hashed, salt

def handle_client(client_socket, addr):
    """Handle a single client connection."""
    print(f"[NEW CONNECTION] {addr} connected.")
    
    # Create a file-like object for easier reading of lines
    # valid for text-based protocols (like our JSON lines)
    f = client_socket.makefile('r')
    
    user_authenticated = False
    current_username = None

    try:
        while True:
            # 1. Authentication Loop
            while not user_authenticated:
                # Wait for login/signup request
                line = f.readline()
                if not line:
                    return # Client disconnected
                
                try:
                    data = json.loads(line)
                    command = data.get('command')
                    username = data.get('username')
                    password = data.get('password')
                    
                    response = {"status": "error", "message": "Unknown error"}

                    if command == 'signup':
                        conn = sqlite3.connect(DB_NAME)
                        c = conn.cursor()
                        try:
                            pwd_hash, salt = hash_password(password)
                            c.execute("INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)", 
                                      (username, pwd_hash, salt))
                            conn.commit()
                            response = {"status": "success", "message": "Account created successfully. You are now logged in."}
                            user_authenticated = True
                            current_username = username
                        except sqlite3.IntegrityError:
                            response = {"status": "fail", "message": "Username already taken."}
                        finally:
                            conn.close()

                    elif command == 'login':
                        conn = sqlite3.connect(DB_NAME)
                        c = conn.cursor()
                        c.execute("SELECT password_hash, salt FROM users WHERE username=?", (username,))
                        row = c.fetchone()
                        conn.close()

                        if row:
                            stored_hash, stored_salt = row
                            check_hash, _ = hash_password(password, stored_salt)
                            if check_hash == stored_hash:
                                response = {"status": "success", "message": "Login successful."}
                                user_authenticated = True
                                current_username = username
                            else:
                                response = {"status": "fail", "message": "Incorrect password."}
                        else:
                            response = {"status": "fail", "message": "User not found."}

                    # Send auth result back to client
                    client_socket.sendall((json.dumps(response) + "\n").encode())
                
                except json.JSONDecodeError:
                    pass # Ignore garbage data

            # 2. Chat Loop (Once authenticated)
            # Add to broadcast list
            with clients_lock:
                if client_socket not in clients:
                    clients.append(client_socket)
            
            # Announce arrival
            broadcast_message("Server", f"{current_username} has joined the chat.")

            # Listen for messages
            while True:
                line = f.readline()
                if not line:
                    break # Disconnected
                
                data = json.loads(line)
                if data.get('command') == 'message':
                    content = data.get('content')
                    broadcast_message(current_username, content)
            
            break # Exit outer loop if inner loop breaks

    except Exception as e:
        print(f"[ERROR] {addr}: {e}")
    finally:
        # Cleanup
        with clients_lock:
            if client_socket in clients:
                clients.remove(client_socket)
        
        if current_username:
            broadcast_message("Server", f"{current_username} has left the chat.")
        
        client_socket.close()
        print(f"[DISCONNECT] {addr} disconnected.")

def broadcast_message(sender, message):
    """Send a message to all connected clients."""
    payload = json.dumps({"sender": sender, "content": message}) + "\n"
    print(f"[BROADCAST] {sender}: {message}")
    
    with clients_lock:
        for c in clients:
            try:
                c.sendall(payload.encode())
            except:
                # If sending fails, assume dead connection (cleanup happens in thread)
                pass

def start_server():
    init_db()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"[LISTENING] Server is listening on {HOST}:{PORT}")

    while True:
        client_socket, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(client_socket, addr))
        thread.start()

if __name__ == "__main__":
    start_server()
