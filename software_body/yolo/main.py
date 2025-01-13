import cv2
import numpy as np
import socket
import time

from ultralytics import YOLO
import socketio

# Replace with your Raspberry Pi's IP address and port
RPI_IP = "172.20.10.3"
RPI_PORT = 8554

TOOL_DB = {
    "hammer", "wrench", "drill", "saw", "knife", "lathe",
    "milling machine", "drill press", "pliers", "chisel",
    "person", "bottle", "cell phone", "keyboard", "mouse"
}
model = YOLO("yolov8n.pt")
data = b''


while True:
    try:
        # Create a Socket.IO client
        sio = socketio.Client(
            reconnection=True,  # Equivalent to upgrade: false
            ssl_verify=False,     # Equivalent to rejectUnauthorized: false
        )

        connected = False
        # Connect to the server
        while not connected:
            try:

                sio.connect(
                    'http://127.0.0.1:5000',
                    socketio_path="/Little-Brother/socket.io",
                    headers={'Origin': '*'},  # For CORS
                    auth={'source': 'display'},  # Equivalent to query
                    transports=['websocket']
                )
                connected = True
            except Exception as e:
                print(e)
                print("Retrying in 5 seconds...")
                time.sleep(5)

        # Create a socket object
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connect to the server
        client_socket.connect((RPI_IP, RPI_PORT))


        while True:
            try:
                # Receive data from the socket
                packet = client_socket.recv(4096)
                if not packet: break
                data += packet

                # Find the start and end markers for the JPEG images
                a = data.find(b'\xff\xd8')
                b = data.find(b'\xff\xd9')
                if a != -1 and b != -1:
                    # Extract the JPEG image data
                    jpg = data[a:b+2]
                    data = data[b+2:]

                    # Decode the JPEG image
                    image = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)

                    results = model(image, verbose=False)[0]

                    recognized_objects = []

                    for box in results.boxes:
                        class_id = int(box.cls[0].item())
                        class_name = model.names[class_id]  # e.g., "person", "hammer", ...
                        confidence = float(box.conf[0].item())

                        if confidence > 0.3 and class_name in TOOL_DB:
                            x1, y1, x2, y2 = box.xyxy[0]

                            # Convert to int
                            x1, y1, x2, y2 = map(int, (x1, y1, x2, y2))
                            w, h = x2 - x1, y2 - y1

                            cx = (x1 + x2) // 2
                            cy = (y1 + y2) // 2

                            # Save recognized objects to a list or database
                            recognized_objects.append({
                                "lbl": class_name,
                                "conf": confidence,
                                "coords": [cx, cy],
                                "size": [w, h],
                            })


                    sio.emit('yolo-items', recognized_objects)

                    if cv2.waitKey(1) == ord('q'):
                        break
            except (socket.error, KeyboardInterrupt) as e:
                print(f"Error: {e}")
                break

    except Exception as e:
        print(e)
        print("Retrying in 5 seconds...")
        time.sleep(5)

# Close the connection and cleanup
client_socket.close()
