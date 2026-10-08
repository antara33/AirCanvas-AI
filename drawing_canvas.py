import cv2
import numpy as np
import os
from datetime import datetime

from config import SAVE_DIR
from shape_recognizer import ShapeRecognizer


class DrawingCanvas:

    def __init__(self, width, height):

        self.width = width
        self.height = height

        self.canvas = np.zeros(
            (height, width, 3),
            dtype=np.uint8
        )

        self.mask = np.zeros(
            (height, width),
            dtype=np.uint8
        )

        self.previous_point = None

        self.color = (220, 80, 200)
        self.brush_size = 6
        self.eraser = False

       

        self.history = []
        self.redo_stack = []

        self.stroke_changed = False
        self.max_history = 20

        self.save_history()

      

        self.shape_mode = "FREE"

        self.shape_start = None
        self.shape_current = None
        self.shape_active = False

       

        self.smart_recognizer = ShapeRecognizer()

        self.smart_active = False

        self.last_detected_shape = "NONE"


    def set_color(self, color):

        self.color = color
        self.eraser = False


    def set_eraser(self, enabled):

        self.eraser = enabled
        self.end_stroke()

       
        if enabled:
            self.set_shape_mode("FREE")

   

    def increase_brush(self):

        self.brush_size = min(
            self.brush_size + 2,
            30
        )

    def decrease_brush(self):

        self.brush_size = max(
            self.brush_size - 2,
            2
        )

   

    def draw(self, point):

        if self.previous_point is None:

            self.previous_point = point
            return

        if self.eraser:

            thickness = max(
                self.brush_size * 3,
                10
            )

            cv2.line(
                self.canvas,
                self.previous_point,
                point,
                (0, 0, 0),
                thickness,
                cv2.LINE_AA
            )

            cv2.line(
                self.mask,
                self.previous_point,
                point,
                0,
                thickness,
                cv2.LINE_AA
            )

        else:

            cv2.line(
                self.canvas,
                self.previous_point,
                point,
                self.color,
                self.brush_size,
                cv2.LINE_AA
            )

            cv2.line(
                self.mask,
                self.previous_point,
                point,
                255,
                self.brush_size,
                cv2.LINE_AA
            )

        self.previous_point = point
        self.stroke_changed = True


    def end_stroke(self):

        self.previous_point = None

        if self.stroke_changed:

            self.save_history()
            self.stroke_changed = False



    def save_history(self):

        state = (
            self.canvas.copy(),
            self.mask.copy()
        )

        if len(self.history) >= self.max_history:
            self.history.pop(0)

        self.history.append(state)

        self.redo_stack.clear()

   

    def undo(self):

        self.end_stroke()
        self.cancel_shape()

      
        self.smart_active = False
        self.smart_recognizer.reset()

        if len(self.history) <= 1:

            print("Nothing to undo.")
            return False

        current_state = self.history.pop()

        self.redo_stack.append(
            (
                current_state[0].copy(),
                current_state[1].copy()
            )
        )

        previous_state = self.history[-1]

        self.canvas = previous_state[0].copy()
        self.mask = previous_state[1].copy()

        self.previous_point = None

        return True


    def redo(self):

        self.end_stroke()
        self.cancel_shape()

        self.smart_active = False
        self.smart_recognizer.reset()

        if not self.redo_stack:

            print("Nothing to redo.")
            return False

        state = self.redo_stack.pop()

        self.canvas = state[0].copy()
        self.mask = state[1].copy()

        self.history.append(
            (
                self.canvas.copy(),
                self.mask.copy()
            )
        )

        if len(self.history) > self.max_history:
            self.history.pop(0)

        self.previous_point = None

        return True


    def clear(self):

        self.end_stroke()
        self.cancel_shape()

      
        self.smart_active = False
        self.smart_recognizer.reset()

        if not np.any(self.mask):

            print("Canvas already empty.")
            return

        self.canvas[:] = 0
        self.mask[:] = 0

        self.previous_point = None

        self.save_history()

   

    def set_shape_mode(self, mode):

        valid_modes = [
            "FREE",
            "LINE",
            "RECTANGLE",
            "CIRCLE",
            "SMART",
        ]

        if mode not in valid_modes:
            return

        self.end_stroke()
        self.cancel_shape()

        
        self.smart_active = False
        self.smart_recognizer.reset()

        self.shape_mode = mode
        self.smart_active = False
        self.smart_recognizer.reset()

        
        if mode != "FREE":
            self.eraser = False

        print(
            f"Shape mode: {self.shape_mode}"
        )

    # START SHAPE
  

    def start_shape(self, point):

        if self.shape_mode == "FREE":
            return

        if self.shape_mode == "SMART":
            return

        if self.shape_active:
            return

        self.shape_start = point
        self.shape_current = point
        self.shape_active = True

    

    def update_shape(self, point):

        if not self.shape_active:
            return

        self.shape_current = point

    # CANCEL SHAPE
    

    def cancel_shape(self):

        self.shape_start = None
        self.shape_current = None
        self.shape_active = False

    

    def finish_shape(self):

        if not self.shape_active:
            return False

        if (
            self.shape_start is None
            or self.shape_current is None
        ):
            self.cancel_shape()
            return False

        start = self.shape_start
        end = self.shape_current

        # Ignore extremely tiny accidental shapes
        distance = (
            (
                end[0] - start[0]
            ) ** 2
            +
            (
                end[1] - start[1]
            ) ** 2
        ) ** 0.5

        if distance < 8:

            self.cancel_shape()
            return False


        if self.shape_mode == "LINE":

            cv2.line(
                self.canvas,
                start,
                end,
                self.color,
                self.brush_size,
                cv2.LINE_AA
            )

            cv2.line(
                self.mask,
                start,
                end,
                255,
                self.brush_size,
                cv2.LINE_AA
            )


        elif self.shape_mode == "RECTANGLE":

            cv2.rectangle(
                self.canvas,
                start,
                end,
                self.color,
                self.brush_size,
                cv2.LINE_AA
            )

            cv2.rectangle(
                self.mask,
                start,
                end,
                255,
                self.brush_size,
                cv2.LINE_AA
            )


        elif self.shape_mode == "CIRCLE":

            radius = int(
                (
                    (
                        end[0] - start[0]
                    ) ** 2
                    +
                    (
                        end[1] - start[1]
                    ) ** 2
                ) ** 0.5
            )

            cv2.circle(
                self.canvas,
                start,
                radius,
                self.color,
                self.brush_size,
                cv2.LINE_AA
            )

            cv2.circle(
                self.mask,
                start,
                radius,
                255,
                self.brush_size,
                cv2.LINE_AA
            )

        else:

            self.cancel_shape()
            return False

        self.cancel_shape()

        # Shape becomes one Undo/Redo item
        self.save_history()

        return True

    # DRAW SHAPE PREVIEW
   

    def draw_shape_preview(self, frame):

        if not self.shape_active:
            return frame

        if (
            self.shape_start is None
            or self.shape_current is None
        ):
            return frame

        start = self.shape_start
        end = self.shape_current

        preview = frame.copy()

        preview_thickness = max(
            2,
            self.brush_size
        )

        if self.shape_mode == "LINE":

            cv2.line(
                preview,
                start,
                end,
                self.color,
                preview_thickness,
                cv2.LINE_AA
            )

        elif self.shape_mode == "RECTANGLE":

            cv2.rectangle(
                preview,
                start,
                end,
                self.color,
                preview_thickness,
                cv2.LINE_AA
            )

        elif self.shape_mode == "CIRCLE":

            radius = int(
                (
                    (
                        end[0] - start[0]
                    ) ** 2
                    +
                    (
                        end[1] - start[1]
                    ) ** 2
                ) ** 0.5
            )

            cv2.circle(
                preview,
                start,
                radius,
                self.color,
                preview_thickness,
                cv2.LINE_AA
            )

        cv2.circle(
            preview,
            start,
            5,
            (255, 255, 255),
            -1
        )

        return preview


    def start_smart_draw(self, point):

        if self.shape_mode != "SMART":
            return

        if self.smart_active:
            return

        self.end_stroke()
        self.cancel_shape()

        self.smart_recognizer.reset()

        self.smart_recognizer.add_point(
            point
        )

        self.smart_active = True
        self.last_detected_shape = "DRAWING"

    

    def update_smart_draw(self, point):

        if not self.smart_active:
            return

        self.smart_recognizer.add_point(
            point
        )

   

    def draw_smart_preview(self, frame):

        if not self.smart_active:
            return frame

        points = self.smart_recognizer.points

        if len(points) < 2:
            return frame

        preview = frame.copy()

        for i in range(
            1,
            len(points)
        ):

            cv2.line(
                preview,
                points[i - 1],
                points[i],
                self.color,
                max(
                    2,
                    self.brush_size
                ),
                cv2.LINE_AA
            )

        return preview

 

    def save_rough_smart_stroke(
        self,
        points
    ):

        if len(points) < 2:
            return False

        for i in range(
            1,
            len(points)
        ):

            cv2.line(
                self.canvas,
                points[i - 1],
                points[i],
                self.color,
                self.brush_size,
                cv2.LINE_AA
            )

            cv2.line(
                self.mask,
                points[i - 1],
                points[i],
                255,
                self.brush_size,
                cv2.LINE_AA
            )

        return True

   

    def finish_smart_draw(self):

        if not self.smart_active:
            return None

        result = self.smart_recognizer.recognize()

        detected = result.get(
            "shape",
            "UNKNOWN"
        )

        self.last_detected_shape = detected

        

        if detected == "LINE":

            start = result["start"]
            end = result["end"]

            cv2.line(
                self.canvas,
                start,
                end,
                self.color,
                self.brush_size,
                cv2.LINE_AA
            )

            cv2.line(
                self.mask,
                start,
                end,
                255,
                self.brush_size,
                cv2.LINE_AA
            )

        

        elif detected == "CIRCLE":

            center = result["center"]
            radius = result["radius"]

            cv2.circle(
                self.canvas,
                center,
                radius,
                self.color,
                self.brush_size,
                cv2.LINE_AA
            )

            cv2.circle(
                self.mask,
                center,
                radius,
                255,
                self.brush_size,
                cv2.LINE_AA
            )

       

        elif detected == "RECTANGLE":

            start = result["start"]
            end = result["end"]

            cv2.rectangle(
                self.canvas,
                start,
                end,
                self.color,
                self.brush_size,
                cv2.LINE_AA
            )

            cv2.rectangle(
                self.mask,
                start,
                end,
                255,
                self.brush_size,
                cv2.LINE_AA
            )


        else:

            # If recognition fails,
            # preserve the user's rough drawing.
            self.save_rough_smart_stroke(
                result.get(
                    "points",
                    []
                )
            )

        self.smart_active = False

        self.smart_recognizer.reset()

        
        self.save_history()

        print(
            f"Smart detected: {detected}"
        )

        return detected


    def overlay(
        self,
        frame,
        white_canvas=False
    ):

        if white_canvas:

            output = np.full_like(
                frame,
                245
            )

        else:

            output = frame.copy()

        inverse_mask = cv2.bitwise_not(
            self.mask
        )

        background = cv2.bitwise_and(
            output,
            output,
            mask=inverse_mask
        )

        drawing = cv2.bitwise_and(
            self.canvas,
            self.canvas,
            mask=self.mask
        )

        return cv2.add(
            background,
            drawing
        )



    def get_export_image(self):

        output = np.full(
            (
                self.height,
                self.width,
                3
            ),
            255,
            dtype=np.uint8
        )

        inverse_mask = cv2.bitwise_not(
            self.mask
        )

        background = cv2.bitwise_and(
            output,
            output,
            mask=inverse_mask
        )

        drawing = cv2.bitwise_and(
            self.canvas,
            self.canvas,
            mask=self.mask
        )

        return cv2.add(
            background,
            drawing
        )

   

    def save(self):

        self.end_stroke()

       
        if self.shape_active:
            self.finish_shape()

     
        if self.smart_active:
            self.finish_smart_draw()

        os.makedirs(
            SAVE_DIR,
            exist_ok=True
        )

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        filename = (
            f"aircanvas_{timestamp}.png"
        )

        filepath = os.path.join(
            SAVE_DIR,
            filename
        )

        export_image = (
            self.get_export_image()
        )

        success = cv2.imwrite(
            filepath,
            export_image
        )

        if success:

            print(
                f"Drawing saved: {filepath}"
            )

            return filepath

        print(
            "ERROR: Drawing could not be saved."
        )

        return None