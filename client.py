import socket
import threading
import json
import sys

# Configuration
HOST = '127.0.0.1'
PORT = 55556

def receive_messages(sock):
    """Thread function to listen for incoming messages from server."""
    f = sock.makefile('r')
    while True:
        try:
            line = f.readline()
            if not line:
                print("\n[!] Disconnected from server.")
                sys.exit()
            
            data = json.loads(line)
            sender = data.get('sender')
            content = data.get('content')
            print(f"\r[{sender}]: {content}")
            print("You: ", end="", flush=True) # Reprompt for input
        except Exception:
            break

def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((HOST, PORT))
    except ConnectionRefusedError:
        print("Could not connect to server. Is it running?")
        return

    # --- Authentication Phase ---
    authenticated = False
    f_reader = client.makefile('r')

    while not authenticated:
        print("\n--- Welcome to PythonChat ---")
        print("1. Login")
        print("2. Signup")
        choice = input("Select an option (1/2): ").strip()

        if choice not in ['1', '2']:
            print("Invalid choice.")
            continue

        username = input("Enter Username: ").strip()
        password = input("Enter Password: ").strip()

        command = "login" if choice == '1' else "signup"
        
        # Send auth request
        auth_payload = {
            "command": command,
            "username": username,
            "password": password
        }
        client.sendall((json.dumps(auth_payload) + "\n").encode())

        # Wait for response
        response_line = f_reader.readline()
        if not response_line:
            print("Server closed connection.")
            return
        
        response = json.loads(response_line)
        
        if response['status'] == 'success':
            print(f"\n[+] {response['message']}")
            authenticated = True
        else:
            print(f"\n[-] Error: {response['message']}")

    # --- Chat Phase ---
    print(f"--- Joined Public Chat as {username} ---")
    print("Type your message and press Enter to send.")

    # Start a thread to listen for messages from the server
    receive_thread = threading.Thread(target=receive_messages, args=(client, ), daemon=True)
    receive_thread.start()

    # Main thread handles sending messages
    try:
        while True:
            msg = input("You: ")
            if msg.lower() == 'exit':
                break
            
            # Send message
            msg_payload = {
                "command": "message",
                "content": msg
            }
            client.sendall((json.dumps(msg_payload) + "\n").encode())
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        client.close()

if __name__ == "__main__":
    start_client()
