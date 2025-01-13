import asyncio
import json
import serial
import time
import websockets

baudrate = 115200

ser = None
serial_connected = False
while not serial_connected:
    # Create a serial object
    for i in range(10):
        try:
            ser = serial.Serial(f"/dev/ttyUSB{i}", baudrate)
            serial_connected = True
            break
        except Exception as e:
            pass

    if ser is None:
        print("Serial port not found")
        time.sleep(5)


async def send_command(websocket, data):
    try:
        command = data + " F1000\n"
        response = ""
        ser.write(command.encode())
        response = ser.readline().decode().strip()
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

    if type == "command":
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
