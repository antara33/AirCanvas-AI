import cv2
import mediapipe as mp

from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from config import (
    MODEL_PATH,
    NUM_HANDS,
    MIN_HAND_DETECTION_CONFIDENCE,
    MIN_HAND_PRESENCE_CONFIDENCE,
    MIN_TRACKING_CONFIDENCE,
)


class HandTracker:

    def __init__(self):

        base_options = python.BaseOptions(
            model_asset_path=MODEL_PATH
        )

        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.IMAGE,
            num_hands=NUM_HANDS,
            min_hand_detection_confidence=MIN_HAND_DETECTION_CONFIDENCE,
            min_hand_presence_confidence=MIN_HAND_PRESENCE_CONFIDENCE,
            min_tracking_confidence=MIN_TRACKING_CONFIDENCE,
        )

        self.detector = vision.HandLandmarker.create_from_options(
            options
        )

    def detect(self, frame):

        rgb_frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb_frame
        )

        result = self.detector.detect(mp_image)

        return result

    def get_landmarks(self, result, frame_width, frame_height):

        if not result.hand_landmarks:
            return None

        hand = result.hand_landmarks[0]

        landmarks = []

        for landmark in hand:

            x = int(landmark.x * frame_width)
            y = int(landmark.y * frame_height)

            landmarks.append((x, y))

        return landmarks

    def draw_landmarks(self, frame, landmarks):

        if landmarks is None:
            return

        # Draw landmark points
        for x, y in landmarks:

            cv2.circle(
                frame,
                (x, y),
                4,
                (0, 255, 0),
                -1
            )

        # MediaPipe hand connections
        connections = [
            (0, 1), (1, 2), (2, 3), (3, 4),

            (0, 5), (5, 6), (6, 7), (7, 8),

            (5, 9), (9, 10), (10, 11), (11, 12),

            (9, 13), (13, 14), (14, 15), (15, 16),

            (13, 17), (17, 18), (18, 19), (19, 20),

            (0, 17)
        ]

        for start, end in connections:

            cv2.line(
                frame,
                landmarks[start],
                landmarks[end],
                (255, 255, 255),
                2
            )

    def close(self):

        self.detector.close()