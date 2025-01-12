import asyncio
import base64
import cv2
import pickle
import redis
import websockets

async def send(uri, img):
    async with websockets.connect(uri) as websocket:
        _, buffer = cv2.imencode('.jpg', img)
        jpg_as_text = base64.b64encode(buffer).decode('utf-8')

        event = {
            "type": "image",
            "data": jpg_as_text
        }


        await websocket.send(str(event))

        response = await websocket.recv()
        return response


async def main():
    cap = cv2.VideoCapture(0)
    db = redis.Redis(host="0.0.0.0", port=6379, db=0)

    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    uri = "ws://0.0.0.0:5050/"

    print("Streaming camera feed to", uri)
    while True:
        ret, frame = cap.read()

        if not ret:
            print("No frame captured from camera. Exiting...")
            break

        response = await send(uri, frame)
        db.set("camera-feed", pickle.dumps(frame))
        db.publish("camera-feed", pickle.dumps(frame))
        db.set("items", pickle.dumps(response))
        db.publish("items", pickle.dumps(response))


    cap.release()

if __name__ == "__main__":
    asyncio.run(main())
