import cv2
import numpy as np
import math


class ShapeRecognizer:

    def __init__(self):

        self.points = []

        # Minimum number of collected points
        self.min_points = 8


    def reset(self):

        self.points = []



    def add_point(self, point):

        if point is None:
            return

        x, y = point

        # Avoid storing almost identical points
        if self.points:

            last_x, last_y = self.points[-1]

            distance = math.hypot(
                x - last_x,
                y - last_y
            )

            if distance < 3:
                return

        self.points.append(
            (int(x), int(y))
        )




    @staticmethod
    def distance(p1, p2):

        return math.hypot(
            p1[0] - p2[0],
            p1[1] - p2[1]
        )

    # PATH LENGTH
  

    def path_length(self):

        if len(self.points) < 2:
            return 0

        total = 0

        for i in range(
            1,
            len(self.points)
        ):

            total += self.distance(
                self.points[i - 1],
                self.points[i]
            )

        return total

  
    # BOUNDING BOX


    def bounding_box(self):

        if not self.points:
            return None

        xs = [
            p[0]
            for p in self.points
        ]

        ys = [
            p[1]
            for p in self.points
        ]

        return (
            min(xs),
            min(ys),
            max(xs),
            max(ys)
        )

   
    # LINE DETECTION
  

    def is_line(self):

        if len(self.points) < self.min_points:
            return False

        start = self.points[0]
        end = self.points[-1]

        direct_distance = self.distance(
            start,
            end
        )

        path = self.path_length()

        if path < 20:
            return False

       
        straightness = (
            direct_distance / path
        )

        return straightness > 0.92

   
    # CLOSED SHAPE CHECK
    

    def is_closed(self):

        if len(self.points) < self.min_points:
            return False

        box = self.bounding_box()

        if box is None:
            return False

        x1, y1, x2, y2 = box

        width = x2 - x1
        height = y2 - y1

        size = max(
            width,
            height
        )

        if size < 20:
            return False

        start = self.points[0]
        end = self.points[-1]

        closing_distance = self.distance(
            start,
            end
        )

        # Start/end don't need to touch perfectly.
        return (
            closing_distance
            <
            size * 0.38
        )


    def get_contour(self):

        if len(self.points) < 3:
            return None

        contour = np.array(
            self.points,
            dtype=np.int32
        ).reshape(
            (-1, 1, 2)
        )

        return contour

  
    # CIRCLE DETECTION
   

    def is_circle(self):

        if not self.is_closed():
            return False

        contour = self.get_contour()

        if contour is None:
            return False

        area = abs(
            cv2.contourArea(
                contour
            )
        )

        perimeter = cv2.arcLength(
            contour,
            True
        )

        if (
            area < 200
            or perimeter < 1
        ):
            return False

      
        circularity = (
            4
            * math.pi
            * area
            /
            (
                perimeter
                * perimeter
            )
        )

        x, y, w, h = cv2.boundingRect(
            contour
        )

        if h == 0:
            return False

        aspect_ratio = (
            w / float(h)
        )

        return (
            circularity > 0.68
            and
            0.68
            <
            aspect_ratio
            <
            1.45
        )

    
    # RECTANGLE DETECTION
  

    def is_rectangle(self):

        if not self.is_closed():
            return False

        contour = self.get_contour()

        if contour is None:
            return False

        perimeter = cv2.arcLength(
            contour,
            True
        )

        if perimeter < 1:
            return False

        approximation = (
            cv2.approxPolyDP(
                contour,
                0.045 * perimeter,
                True
            )
        )

        area = abs(
            cv2.contourArea(
                contour
            )
        )

        x, y, w, h = cv2.boundingRect(
            contour
        )

        bounding_area = (
            w * h
        )

        if bounding_area == 0:
            return False

        fill_ratio = (
            area / bounding_area
        )

        
        return (
            4
            <= len(approximation)
            <= 6
            and
            fill_ratio > 0.60
        )

  

    def recognize(self):

        if len(self.points) < self.min_points:

            return {
                "shape": "UNKNOWN",
                "points": self.points.copy()
            }

        # Check straight line first
        if self.is_line():

            return {
                "shape": "LINE",
                "points": self.points.copy(),
                "start": self.points[0],
                "end": self.points[-1],
            }

        # Closed shapes
        if self.is_closed():

            # Circle first
            if self.is_circle():

                box = self.bounding_box()

                x1, y1, x2, y2 = box

                center = (
                    (x1 + x2) // 2,
                    (y1 + y2) // 2
                )

                radius = int(
                    (
                        (x2 - x1)
                        +
                        (y2 - y1)
                    )
                    / 4
                )

                return {
                    "shape": "CIRCLE",
                    "points": self.points.copy(),
                    "center": center,
                    "radius": radius,
                }

            # Rectangle
            if self.is_rectangle():

                box = self.bounding_box()

                x1, y1, x2, y2 = box

                return {
                    "shape": "RECTANGLE",
                    "points": self.points.copy(),
                    "start": (
                        x1,
                        y1
                    ),
                    "end": (
                        x2,
                        y2
                    ),
                }

        return {
            "shape": "UNKNOWN",
            "points": self.points.copy()
        }