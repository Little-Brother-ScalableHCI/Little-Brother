import cv2
import pickle
import socket
import struct
import redis

# Set the IP address and port for the server
SERVER_IP = "0.0.0.0"  # Listen on all available interfaces
SERVER_PORT = 8554

def main():
    while True:
        # Create a socket object
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Bind the socket to a specific address and port
        server_socket.bind((SERVER_IP, SERVER_PORT))

        # Listen for incoming connections (maximum 1 connection in the queue)
        server_socket.listen(1)
        print(f"[*] Listening as {SERVER_IP}:{SERVER_PORT}")

        # Accept a connection from a client
        client_socket, client_address = server_socket.accept()
        print(f"[*] Accepted connection from {client_address[0]}:{client_address[1]}")

        # Start capturing video from the webcam (camera index 0)
        cam = cv2.VideoCapture(0)
        db = redis.Redis(host="0.0.0.0", port=6379, db=0)

        try:
            while True:
                # Read a frame from the camera
                ret, frame = cam.read()
                if not ret:
                    print("Failed to grab frame")
                    break

                # Encode the frame as JPEG
                result, encoded_image = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
                if not result:
                    print("Failed to encode image")
                    break

                db.set("camera-feed", pickle.dumps(frame))
                db.publish("camera-feed", pickle.dumps(frame))

                # Convert the image data to a byte string
                data = encoded_image.tobytes()

                # Send the size of the data first (using a 4-byte header)
                # '<L' means little-endian unsigned long (4 bytes)
                size = struct.pack('<L', len(data))

                try:
                    # Send the size followed by the actual image data
                    client_socket.sendall(size + data)
                except ConnectionResetError:
                    print("Client disconnected.")
                    break

        except KeyboardInterrupt:
            print("Stopping the server.")
        finally:
            # Clean up: release the camera and close the sockets
            cam.release()
            client_socket.close()
            server_socket.close()

if __name__ == "__main__":
    main()
