import cv2
import time


class FeedbackManager:

    def __init__(self):

        self.message = ""
        self.message_type = "INFO"

        self.start_time = 0
        self.duration = 1.8


    def show(
        self,
        message,
        message_type="INFO",
        duration=1.8,
    ):

        self.message = message
        self.message_type = message_type
        self.duration = duration
        self.start_time = time.time()


    def is_active(self):

        if not self.message:
            return False

        elapsed = (
            time.time()
            - self.start_time
        )

        if elapsed > self.duration:

            self.message = ""

            return False

        return True


    def get_color(self):

        colors = {
            "INFO": (80, 150, 230),
            "SUCCESS": (80, 180, 100),
            "WARNING": (50, 180, 230),
            "ERROR": (70, 70, 220),
            "SMART": (150, 100, 220),
        }

        return colors.get(
            self.message_type,
            (80, 150, 230),
        )

   

    def draw(self, frame):

        if not self.is_active():
            return

        height, width = frame.shape[:2]

        text = self.message

        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.52
        thickness = 1

        text_size = cv2.getTextSize(
            text,
            font,
            font_scale,
            thickness,
        )[0]

        padding_x = 20
        padding_y = 12

        box_width = (
            text_size[0]
            + padding_x * 2
        )

        box_height = (
            text_size[1]
            + padding_y * 2
        )

        # Center toast
        x1 = (
            width
            - box_width
        ) // 2

        y1 = 15

        x2 = (
            x1
            + box_width
        )

        y2 = (
            y1
            + box_height
        )

    

        overlay = frame.copy()

        cv2.rectangle(
            overlay,
            (x1, y1),
            (x2, y2),
            (30, 32, 40),
            -1,
        )

        cv2.addWeighted(
            overlay,
            0.88,
            frame,
            0.12,
            0,
            frame,
        )


        color = self.get_color()

        cv2.rectangle(
            frame,
            (x1, y1),
            (x1 + 5, y2),
            color,
            -1,
        )


        cv2.rectangle(
            frame,
            (x1, y1),
            (x2, y2),
            (100, 105, 120),
            1,
        )

       

        text_x = (
            x1
            + padding_x
        )

        text_y = (
            y1
            + padding_y
            + text_size[1]
        )

        cv2.putText(
            frame,
            text,
            (text_x, text_y),
            font,
            font_scale,
            (255, 255, 255),
            thickness,
            cv2.LINE_AA,
        )