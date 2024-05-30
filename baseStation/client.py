import socket
import os
import time

def send_file(filename, server_ip, server_port=12345):
    if not os.path.exists(filename):
        print(f"File not found: {filename}")
        return

    file_size = os.path.getsize(filename)

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_ip, server_port))
    print(f"Connected to server {server_ip}:{server_port}")

    # Send the file metadata
    metadata = f"{os.path.basename(filename)}|{file_size}"
    client_socket.send(metadata.encode())
    
    time.sleep(3)

    # Send the file data
    with open(filename, 'rb') as f:
        while (chunk := f.read(4096)):
            client_socket.send(chunk)
    
    print(f"File sent: {filename}")
    client_socket.close()

if __name__ == "__main__":
    send_file('/home/guilherme/Uni/RSA/heatmaps/network_quality_heatmap_DIRECT-epson-026d-0-001.html', '192.168.3.11') #  TODO Change the path to the heatmap file
