import socket
import os

def start_server(host='0.0.0.0', port=12345, save_directory='/home/guilherme/Uni/RSA/heatmaps'):
    # Ensure the save directory exists
    os.makedirs(save_directory, exist_ok=True)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Listening on {host}:{port}")

    while True:
        client_socket, address = server_socket.accept()
        print(f"Connection from {address}")

        metadata = client_socket.recv(1024).decode()
        if not metadata:
            print("No metadata received.")
            client_socket.close()
            continue

        # Use pipe ('|') as the delimiter for metadata
        try:
            filename, file_size = metadata.split('|')
            filename = os.path.join(save_directory, filename)
            file_size = int(file_size)
            print(f"Receiving file: {filename} ({file_size} bytes)")
        except ValueError as e:
            print(f"Error parsing metadata: {e}")
            client_socket.close()
            continue

        with open(filename, 'wb') as file:
            bytes_received = 0  
            while bytes_received < file_size:
                chunk = client_socket.recv(4096)
                if not chunk:
                    break
                file.write(chunk)
                bytes_received += len(chunk)

        print(f"File received: {bytes_received} bytes")
        client_socket.close()

if __name__ == '__main__':
    start_server()
