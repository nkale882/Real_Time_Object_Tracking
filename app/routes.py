from flask import Blueprint, render_template, Response, request, jsonify
from .camera import VideoCamera
import cv2

main_bp = Blueprint('main', __name__)
camera = VideoCamera()

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/video_feed')
def video_feed():
    return Response(camera.generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@main_bp.route('/select_box', methods=['POST'])
def select_box():
    data = request.json
    # Frontend canvas dimensions sent in the request (assumed)
    canvas_width = data['canvasWidth']
    canvas_height = data['canvasHeight']

    # Get actual video resolution
    actual_width = camera.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    actual_height = camera.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

    scale_x = actual_width / canvas_width
    scale_y = actual_height / canvas_height

    # Scale the box to match real frame
    scaled_box = (
        int(data['x'] * scale_x),
        int(data['y'] * scale_y),
        int(data['w'] * scale_x),
        int(data['h'] * scale_y)
    )
    camera.set_manual_box(scaled_box)
    return jsonify({"status": "tracking_started", "scaled_box": scaled_box})
