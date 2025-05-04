import cv2
from ultralytics import YOLO
from deep_sort_realtime.deepsort_tracker import DeepSort

class VideoCamera:
    def __init__(self):
        self.cap = cv2.VideoCapture("Video Path")
        self.yolo = YOLO("yolov8n.pt")
        self.tracker = DeepSort(max_age=10, n_init=2, max_cosine_distance=0.3)
        self.selected_box = None
        self.track_id = None
        self.frame_skip = 2  # Skip every 1 frame (process every 2nd frame)
        self.frame_count = 0

    def set_manual_box(self, box):
        self.selected_box = box
        self.track_id = None

    def iou(self, boxA, boxB):
        xA = max(boxA[0], boxB[0])
        yA = max(boxA[1], boxB[1])
        xB = min(boxA[0] + boxA[2], boxB[0] + boxB[2])
        yB = min(boxA[1] + boxA[3], boxB[1] + boxB[3])
        interArea = max(0, xB - xA) * max(0, yB - yA)
        boxAArea = boxA[2] * boxA[3]
        boxBArea = boxB[2] * boxB[3]
        return interArea / float(boxAArea + boxBArea - interArea + 1e-5)

    def generate_frames(self):
        while True:
            success, frame = self.cap.read()
            if not success:
                break

            self.frame_count += 1
            if self.frame_count % self.frame_skip != 0:
                continue

            # Downscale frame for fast YOLO inference
            resized_frame = cv2.resize(frame, (480, 270))
            results = self.yolo(resized_frame, verbose=False)[0]

            scale_x = frame.shape[1] / resized_frame.shape[1]
            scale_y = frame.shape[0] / resized_frame.shape[0]

            detections = []
            for box in results.boxes.xyxy:
                x1, y1, x2, y2 = map(float, box[:4])
                x1 = int(x1 * scale_x)
                y1 = int(y1 * scale_y)
                x2 = int(x2 * scale_x)
                y2 = int(y2 * scale_y)
                w, h = x2 - x1, y2 - y1
                detections.append(([x1, y1, w, h], 0.9, None))

            tracks = self.tracker.update_tracks(detections, frame=frame)

            for track in tracks:
                if not track.is_confirmed():
                    continue

                l, t, r, b = track.to_ltrb()
                w, h = r - l, b - t
                track_box = (l, t, w, h)

                if self.selected_box and self.track_id is None:
                    iou_score = self.iou(self.selected_box, track_box)
                    if iou_score > 0.1:
                        self.track_id = track.track_id

                if self.track_id == track.track_id:
                    cv2.rectangle(frame, (int(l), int(t)), (int(r), int(b)), (0, 255, 0), 2)
                    cv2.putText(frame, f"Tracking ID {self.track_id}", (int(l), int(t) - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            if self.selected_box and self.track_id is None:
                x, y, w, h = self.selected_box
                cv2.rectangle(frame, (int(x), int(y)), (int(x + w), int(y + h)), (0, 0, 255), 2)
                cv2.putText(frame, "Waiting to lock target", (int(x), int(y) - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

            _, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
