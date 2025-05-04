import cv2
from app.deep_sort.tracker import Tracker
from app.deep_sort.detection import Detection
from app.deep_sort.nn_matching import NearestNeighborDistanceMetric

# Initialize Deep SORT tracker
metric = NearestNeighborDistanceMetric("cosine", 0.5, 100)
tracker = Tracker(metric)

def initialize_tracker(frame):
    bbox = cv2.selectROI("Select Object", frame, fromCenter=False, showCrosshair=True)
    cv2.destroyWindow("Select Object")
    return bbox

def track_video(video_path):
    cap = cv2.VideoCapture(video_path)
    ret, frame = cap.read()
    if not ret:
        print("Failed to read video")
        return

    bbox = initialize_tracker(frame)
    detection = Detection(bbox, 1.0, None)
    tracker.predict()
    tracker.update([detection])

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        tracker.predict()
        tracker.update([])  # Since no detector, you can optionally add custom detections

        for track in tracker.tracks:
            if not track.is_confirmed() or track.time_since_update > 1:
                continue
            x1, y1, w, h = track.to_tlwh()
            x2, y2 = x1 + w, y1 + h
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
            cv2.putText(frame, f"ID: {track.track_id}", (int(x1), int(y1) - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        cv2.imshow("Tracking", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()