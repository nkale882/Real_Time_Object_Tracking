import cv2
from ultralytics import YOLO
from deep_sort_realtime.deepsort_tracker import DeepSort

# Load YOLOv8 and Deep SORT
yolo = YOLO('yolov8n.pt')  # Replace with your custom model if needed
tracker = DeepSort(max_age=30)
cap = cv2.VideoCapture(0)  # Change to video file path if needed
names = yolo.model.names

print("[INFO] Starting video stream. Press 'q' to quit.")

selected_id = None
id_label_map = {}

while True:
    ret, frame = cap.read()
    if not ret:
        print("[ERROR] Failed to read frame")
        break

    resized = cv2.resize(frame, (640, 480))
    results = yolo(resized, verbose=False)[0]

    detections = []
    current_ids = {}

    for r in results.boxes.data.tolist():
        x1, y1, x2, y2, score, class_id = r
        detections.append(([x1, y1, x2 - x1, y2 - y1], score, class_id))

    tracks = tracker.update_tracks(detections, frame=resized)

    for track in tracks:
        if not track.is_confirmed():
            continue
        track_id = track.track_id
        l, t, r, b = track.to_ltrb()
        class_id = int(track.get_det_class())
        label = names[class_id]
        id_label_map[track_id] = label
        current_ids[track_id] = label

        color = (0, 255, 0) if track_id == selected_id else (255, 0, 0)
        cv2.rectangle(resized, (int(l), int(t)), (int(r), int(b)), color, 2)
        cv2.putText(resized, f"{label} #{track_id}", (int(l), int(t) - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    # Show detected object IDs
    y = 20
    cv2.rectangle(resized, (0, 0), (320, 100), (50, 50, 50), -1)
    cv2.putText(resized, "Detected Objects:", (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    y += 25
    for tid, lbl in current_ids.items():
        cv2.putText(resized, f"ID {tid}: {lbl}", (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 255, 200), 1)
        y += 20

    cv2.imshow("Live Object Detection & Tracking", resized)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key >= ord('0') and key <= ord('9'):
        num = int(chr(key))
        if num in id_label_map:
            selected_id = num
            print(f"[INFO] Tracking object #{selected_id} - {id_label_map[selected_id]}")

cap.release()
cv2.destroyAllWindows()
