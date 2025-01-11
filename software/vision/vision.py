import cv2
from ultralytics import YOLO
import time

# Our "database" of recognized tool/machine names. 
# (In a real system, this might include synonyms or specialized items.)
TOOL_DB = {
    "hammer", "wrench", "drill", "saw", "knife", "lathe", 
    "milling machine", "drill press", "pliers", "chisel",
    # Add any additional classes that your YOLO model can detect.
}

# Initialize YOLO model (example: YOLOv8n)
# If you want YOLOv5, you can do from ultralytics import YOLO and load "yolov5s.pt"
model = YOLO("yolov8n.pt")  # or "yolov5s.pt", etc.

def main():
    cap = cv2.VideoCapture(0)  # 0 for default camera

    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("No frame captured from camera. Exiting...")
            break

        # Inference
        # Results come back as a list of "Boxes" with .boxes property
        # on each frame. For YOLOv8, you do:
        results = model(frame, verbose=False)[0]  # take first result

        # Prepare a structure to hold the recognized objects
        recognized_objects = []

        for box in results.boxes:
            # box.xyxy: bounding box [x1, y1, x2, y2]
            # box.cls: class index
            # box.conf: confidence
            class_id = int(box.cls[0].item())
            class_name = model.names[class_id]  # e.g., "person", "hammer", ...
            confidence = float(box.conf[0].item())
            
            # We only keep objects if the label is in our known TOOL_DB 
            # and the confidence is above a threshold
            if class_name in TOOL_DB and confidence > 0.3:
                x1, y1, x2, y2 = box.xyxy[0]
                
                # Convert to int
                x1, y1, x2, y2 = map(int, (x1, y1, x2, y2))
                
                # Compute centroid (local location within the image)
                cx = (x1 + x2) // 2
                cy = (y1 + y2) // 2
                
                # We'll draw a bounding box and centroid for visualization
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.circle(frame, (cx, cy), 4, (0, 0, 255), -1)
                cv2.putText(
                    frame,
                    f"{class_name} {confidence:.2f}",
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2
                )

                # For global location, we only store a placeholder for now
                # e.g., `global_x` and `global_y` might come from the gantry's 
                # known position plus the local camera offset.
                global_x, global_y = None, None

                # Save recognized objects to a list or database
                recognized_objects.append({
                    "label": class_name,
                    "confidence": confidence,
                    "local_coords": (cx, cy),
                    "global_coords": (global_x, global_y)  # placeholder
                })

        # Show the annotated frame
        cv2.imshow("Detection", frame)
        
        # For demonstration, just print the recognized objects
        # In a real system, you might store them in a DB, send to a server, etc.
        if recognized_objects:
            print("Recognized objects:")
            for obj in recognized_objects:
                print(f"  - {obj}")

        # Break on 'q' key
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
