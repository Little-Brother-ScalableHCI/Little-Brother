import asyncio
import base64
import cv2
import json
import numpy as np
import serial
import websockets
from ultralytics import YOLO


TOOL_DB = {
    "hammer", "wrench", "drill", "saw", "knife", "lathe",
    "milling machine", "drill press", "pliers", "chisel",
    "person", "bottle", "cell phone", "keyboard", "mouse"
}

model = YOLO("yolov8n.pt")


port = "/dev/ttyUSB0"
baudrate = 115200

# Create a serial object
# ser = serial.Serial(port, baudrate)


async def process_image(websocket, data):
    try:
        # Decode the base64-encoded image data
        image_data = base64.b64decode(data)
        # Convert the image data to a NumPy array
        nparr = np.frombuffer(image_data, np.uint8)
        # Decode the NumPy array into an OpenCV image
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        recognized_objects = []

        results = model(img, verbose=False)[0]


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

        await websocket.send(str(recognized_objects))
    except Exception as e:
        print(f"Error processing image: {e}")
        await websocket.send(f"Error: {e}")

async def send_command(websocket, data):
    try:
        command = data + "\n"
        response = ""
        # ser.write(command.encode())
        # response = ser.readline().decode().strip()
        await websocket.send(f"Response: {response}")

    except Exception as e:
        print(f"Error processing command: {e}")
        await websocket.send(f"Error: {e}")

async def handler(websocket):
    # Determine which endpoint to use based on the path
    message = await websocket.recv()
    event = json.loads(message.replace("'", '"'))
    type = event.get("type")
    data = event.get("data")

    if type == "image":
        await process_image(websocket, data)
    elif type == "command":
        await send_command(websocket, data)
    else:
        await websocket.send("Unknown event type")


async def main():
    async with websockets.serve(handler, "0.0.0.0", 5050):
        print("WebSocket server started on ws://0.0.0.0:5050")
        await asyncio.Future()  # Run forever

    ser.close()


if __name__ == "__main__":
    asyncio.run(main())
