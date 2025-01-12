import json
import math
import pickle
import redis
import threading
import time

import cv2

from server import sio, app

db = redis.Redis(host="redis", port=6379, db=0)


#* Setting up camera feed forwarding
cam_img = None
cam_sent = False
@sio.on('get-camera-feed')
def sio_camera_feed():
    global cam_sent
    if cam_img is None or len(cam_img) == 0 or cam_sent:
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
            # print("New frame")
            cam_sent = False
        except pickle.UnpicklingError:
            pass
        except Exception as e:
            print(e)
threading.Thread(target=update_camera).start()



#* Managing inventory
items = {}  # Use a dictionary to store items by label
items_sent = False

@sio.on('get-items')
def sio_items():
    global items_sent
    if not items or items_sent:
        return
    sio.emit('items', list(items.values()))  # Send a list of items
    items_sent = True

def update_items():
    global items
    global items_sent
    ps = db.pubsub()
    ps.subscribe("items")
    for binary_data in ps.listen():
        try:
            new_items = json.loads(pickle.loads(bytes(binary_data["data"])).replace("'", '"'))

            for new_item in new_items:
                label = new_item["lbl"]
                items[label] = new_item
                items[label]["world"] = camera_to_world(new_item["coords"][0], new_item["coords"][1])
            items_sent = False
        except pickle.UnpicklingError:
            pass
        except Exception as e:
            print(e)
threading.Thread(target=update_items).start()


current_activity = "None"
activity_data = {}

#* Managing commands
commands = []
@sio.on('get-commands')
def sio_commands_feed():
    if not commands:
        return
    sio.emit('commands', commands)

@sio.on('send-command')
def sio_send_command(data):
    db.set("speech-to-text", pickle.dumps(data))
    db.publish("speech-to-text", pickle.dumps(data))

def update_commands():
    global commands
    global current_activity
    ps = db.pubsub()
    ps.subscribe("command")
    for binary_data in ps.listen():
        try:
            command = pickle.loads(bytes(binary_data["data"]))
            commands.append(command)
            if command["intent"] == "find_location":
                target_item = command["object"]
                if target_item not in items:
                    print(f"Item '{target_item}' not found in inventory")
                    current_activity = "Not found"
                    continue
                target_coords = items[target_item]["world"]
                move_to_coords(target_coords)
        except pickle.UnpicklingError:
            pass
        except Exception as e:
            print(e)
threading.Thread(target=update_commands).start()


@sio.on('send-serial-command')
def sio_send_command(data):
    db.set("serial-command", pickle.dumps(data))
    db.publish("serial-command", pickle.dumps(data))

def send_command(command):
    db.set("serial-command", pickle.dumps(command))
    db.publish("serial-command", pickle.dumps(command))

def offset_items(offset):
    for item in items.values():
        item["world"] = (item["world"][0] - offset[0], item["world"][1] - offset[1])

#* CBPR Pulleys coords
L1 = 2.4
L2 = 3.26
L3 = 3.05
p = (L1 + L2 + L3) / 2
s = math.sqrt(p * (p - L1) * (p - L2) * (p - L3))
h = 2 * s / L2
A1 = [0, L2, 0]
A2 = [h, math.sqrt(L1**2 - h**2), 0]
A3 = [0, 0, 0]
initial_position = [1, 1.5, 0.5]
initial_cable_lengths = [
    math.sqrt((initial_position[0] - A1[0])**2 + (initial_position[1] - A1[1])**2 + (initial_position[2] - A1[2])**2),
    math.sqrt((initial_position[0] - A2[0])**2 + (initial_position[1] - A2[1])**2 + (initial_position[2] - A2[2])**2),
    math.sqrt((initial_position[0] - A3[0])**2 + (initial_position[1] - A3[1])**2 + (initial_position[2] - A3[2])**2)
]
current_position = initial_position
is_moving = False
STEPS = 10

def move_to_coords(object_offset):
    global is_moving
    global current_position
    global current_activity

    if is_moving:
        print("Already moving")
        return
    print(f"Moving to coordinates {object_offset}")
    is_moving = True
    current_activity = "Moving"
    activity_data["angle"] = math.degrees(math.atan2(object_offset[1], object_offset[0]));
    for i in range(STEPS):
        target_position = [
            current_position[0] + i * object_offset[0] / STEPS,
            current_position[1] + i * object_offset[1] / STEPS,
            initial_position[2]
        ]

        # current_c1 = math.sqrt((current_position[0] - A1[0])**2 + (current_position[1] - A1[1])**2 + (current_position[2] - A1[2])**2)
        target_c1 = math.sqrt((target_position[0] - A1[0])**2 + (target_position[1] - A1[1])**2 + (target_position[2] - A1[2])**2)
        delta_c1 = target_c1 - initial_cable_lengths[0]

        # current_c2 = math.sqrt((current_position[0] - A2[0])**2 + (current_position[1] - A2[1])**2 + (current_position[2] - A2[2])**2)
        target_c2 = math.sqrt((target_position[0] - A2[0])**2 + (target_position[1] - A2[1])**2 + (target_position[2] - A2[2])**2)
        delta_c2 = target_c2 - initial_cable_lengths[1]

        # current_c3 = math.sqrt((current_position[0] - A3[0])**2 + (current_position[1] - A3[1])**2 + (current_position[2] - A3[2])**2)
        target_c3 = math.sqrt((target_position[0] - A3[0])**2 + (target_position[1] - A3[1])**2 + (target_position[2] - A3[2])**2)
        delta_c3 = target_c3 - initial_cable_lengths[2]

        send_command(f"G0 X{-1*int(1000*delta_c2)} Y{-1*int(1000*delta_c3)} Z{-1*int(1000*delta_c1)}")

        # while not pickle.loads(db.get("serial-command-response")).strip() == "ok":
        #     time.sleep(0.1)
        # db.set("serial-command-response", pickle.dumps({"ok": False}))

        offset_items([object_offset[0] / STEPS, object_offset[1] / STEPS])

        time.sleep(1)

    current_position = [
        current_position[0] + object_offset[0],
        current_position[1] + object_offset[1],
    ]
    is_moving = False
    current_activity = "Found"

def camera_to_world(x, y):
    # Convert camera coordinates to world coordinates for the logitech C270 camera
    Z = 1.5  # Height of the cameras from the table
    F = 55  # Diagonal ield of view of the camera
    image_width = 640
    image_height = 480
    diagonal_pixels = math.sqrt(image_width**2 + image_height**2)
    f = (diagonal_pixels / 2) / math.tan(math.radians(F / 2))

    # Calculate the center of the image
    cx = image_width / 2
    cy = image_height / 2

    # Convert camera coordinates to world coordinates
    X = (x - cx) * Z / f
    Y = (y - cy) * Z / f

    return (X, Y)

@sio.on('get-activity')
def sio_activity():
    sio.emit('activity', {
        "activity": current_activity,
        "data": activity_data
    })

# items = db.get("items")

# db.set("items", items)
# db.publish("items", pickle.dumps(items))

# ps = db.pubsub()
# ps.subscribe("items")
# for binary_data in ps.listen():
#     print(pickle.loads(bytes(binary_data["data"])))

print("Starting server")

sio.run(app, host="0.0.0.0", port=5000)
