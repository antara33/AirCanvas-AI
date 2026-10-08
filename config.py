import os



BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "hand_landmarker.task"
)

SAVE_DIR = os.path.join(
    BASE_DIR,
    "saved_drawings"
)



CAMERA_INDEX = 0

FRAME_WIDTH = 1280
FRAME_HEIGHT = 720



NUM_HANDS = 1

MIN_HAND_DETECTION_CONFIDENCE = 0.5
MIN_HAND_PRESENCE_CONFIDENCE = 0.5
MIN_TRACKING_CONFIDENCE = 0.5



WINDOW_NAME = "AirCanvas AI"

SHOW_LANDMARKS = True