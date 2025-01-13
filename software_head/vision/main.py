import socket
import subprocess

# Streaming port
PORT = 8554

# Command to start the libcamera-vid stream
libcamera_cmd = ["libcamera-vid", "-t", "0", "--inline", "--listen", "-o", f"tcp://0.0.0.0:{PORT}"]

# Start the libcamera-vid process
process = subprocess.Popen(libcamera_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# Create a socket object
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to a specific address and port
server_socket.bind(('0.0.0.0', PORT))

# Listen for incoming connections
server_socket.listen(1)

print(f"Server listening on port {PORT}")

while True:
    try:
        # Accept a connection from a client
        client_socket, addr = server_socket.accept()
        print(f"Accepted connection from {addr}")

        # Continuously read from the libcamera-vid process and send to the client
        while True:
            data = process.stdout.read(4096)
            if not data:
                break
            client_socket.sendall(data)

    except (socket.error, KeyboardInterrupt) as e:
        print(f"Error: {e}")
        break

    finally:
        # Close the client socket
        if client_socket:
            client_socket.close()

# Close the server socket and terminate the libcamera-vid process
server_socket.close()
process.terminate()
