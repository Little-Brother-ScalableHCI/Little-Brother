import asyncio
import pickle
import redis
import websockets

async def send(uri, cmd):
    async with websockets.connect(uri) as websocket:

        event = {
            "type": "command",
            "data": cmd
        }

        await websocket.send(str(event))

        response = await websocket.recv()
        return response


async def main():
    db = redis.Redis(host="0.0.0.0", port=6379, db=0)

    uri = "ws://0.0.0.0:5050/"

    print("Listening for commands...")
    ps = db.pubsub()
    ps.subscribe("serial-command")
    for binary_data in ps.listen():
        try:
            cmd = pickle.loads(bytes(binary_data["data"]))
        except pickle.UnpicklingError:
            continue
        except Exception as e:
            print(e)
            continue
        print("Sending command:", cmd)
        response = await send(uri, cmd)
        print("Received response:", response)
        db.set("serial-command-response", pickle.dumps(response))
        db.publish("serial-command-response", pickle.dumps(response))

if __name__ == "__main__":
    asyncio.run(main())
