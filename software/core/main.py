import pickle
import redis
import threading

import cv2

from server import sio, app

db = redis.Redis(host="redis", port=6379, db=0)


#* Setting up camera feed forwarding
cam_img = None
cam_sent = False
@sio.on('get-camera-feed')
def sio_camera_feed():
    global cam_sent
    if not cam_img and cam_sent:
        return
    _, buffer = cv2.imencode('.png', cam_img)
    buffer = buffer.tobytes()
    sio.emit('camera-feed', buffer)
    cam_sent = True


def update_camera():
    global cam_img
    global cam_sent
    ps = db.pubsub()
    ps.subscribe("camera-feed")
    for binary_data in ps.listen():
        try:
            cam_img = pickle.loads(bytes(binary_data["data"]))
            print("New frame")
            cam_sent = False
        except pickle.UnpicklingError:
            pass
        except Exception as e:
            print(e)
threading.Thread(target=update_camera).start()



#* Managing inventory
items = []
items_sent = False
@sio.on('get-items')
def sio_items():
    global items_sent
    if not cam_img or items_sent:
        return
    _, buffer = cv2.imencode('.png', cam_img)
    buffer = buffer.tobytes()
    sio.emit('items', buffer)
    items_sent = True


def update_items():
    global items
    global items_sent
    ps = db.pubsub()
    ps.subscribe("items")
    for binary_data in ps.listen():
        try:
            items = pickle.loads(bytes(binary_data["data"]))
            print("Updated items")
            items_sent = False
        except pickle.UnpicklingError:
            pass
        except Exception as e:
            print(e)
threading.Thread(target=update_items).start()



#* Managing commands
command = ""
command_sent = False
@sio.on('get-commands')
def sio_commands_feed():
    global command_sent
    if not command or command_sent:
        return
    _, buffer = cv2.imencode('.png', cam_img)
    buffer = buffer.tobytes()
    sio.emit('commands', buffer)
    command_sent = True


def update_commands():
    global command
    global command_sent
    ps = db.pubsub()
    ps.subscribe("command")
    for binary_data in ps.listen():
        try:
            command = pickle.loads(bytes(binary_data["data"]))
            print("Updated command")
            command_sent = False
        except pickle.UnpicklingError:
            pass
        except Exception as e:
            print(e)
threading.Thread(target=update_commands).start()






# items = db.get("items")

# db.set("items", items)
# db.publish("items", pickle.dumps(items))

# ps = db.pubsub()
# ps.subscribe("items")
# for binary_data in ps.listen():
#     print(pickle.loads(bytes(binary_data["data"])))

print("Starting server")

sio.run(app, host="0.0.0.0", port=5000)
