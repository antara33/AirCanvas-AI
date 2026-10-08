import math


class GestureController:

    def __init__(self):

        # Pinch thresholds are normalized relative
        # to hand size instead of raw pixels.
        self.pinch_threshold = 0.32
        self.release_threshold = 0.48

        self.pinch_active = False

    @staticmethod
    def finger_is_up(landmarks, tip, pip):
        return landmarks[tip][1] < landmarks[pip][1]

    @staticmethod
    def distance(point1, point2):

        return math.hypot(
            point1[0] - point2[0],
            point1[1] - point2[1]
        )

    def get_finger_states(self, landmarks):

        if landmarks is None:
            return {
                "index": False,
                "middle": False,
                "ring": False,
                "pinky": False,
            }

        return {
            "index": self.finger_is_up(
                landmarks, 8, 6
            ),

            "middle": self.finger_is_up(
                landmarks, 12, 10
            ),

            "ring": self.finger_is_up(
                landmarks, 16, 14
            ),

            "pinky": self.finger_is_up(
                landmarks, 20, 18
            ),
        }

    def recognize(self, landmarks):

        if landmarks is None:
            return "NO HAND"

        fingers = self.get_finger_states(
            landmarks
        )

        index = fingers["index"]
        middle = fingers["middle"]
        ring = fingers["ring"]
        pinky = fingers["pinky"]

        # V shape = cursor / hover
        if (
            index
            and middle
            and not ring
            and not pinky
        ):
            return "HOVER"

        # Index only = drawing
        if (
            index
            and not middle
            and not ring
            and not pinky
        ):
            return "DRAW"

        if (
            index
            and middle
            and ring
            and pinky
        ):
            return "OPEN PALM"

        if (
            not index
            and not middle
            and not ring
            and not pinky
        ):
            return "STOP"

        return "UNKNOWN"

    def get_pinch_ratio(self, landmarks):

        if landmarks is None:
            return 999

    
        pinch_distance = self.distance(
            landmarks[4],
            landmarks[8]
        )

       
        hand_size = self.distance(
            landmarks[0],
            landmarks[9]
        )

        if hand_size < 1:
            return 999

        return pinch_distance / hand_size

    def detect_pinch_click(self, landmarks):

        """
        Returns True only once when a new
        thumb-index pinch happens.
        """

        if landmarks is None:

            self.pinch_active = False
            return False

        ratio = self.get_pinch_ratio(
            landmarks
        )

    
        if (
            ratio < self.pinch_threshold
            and not self.pinch_active
        ):

            self.pinch_active = True
            return True

    
        if ratio > self.release_threshold:

            self.pinch_active = False

        return False