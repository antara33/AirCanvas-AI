
import cv2


class UIManager:

    def __init__(self, frame_width, frame_height):

        self.width = frame_width
        self.height = frame_height

        self.left_sidebar_width = 155
        self.right_sidebar_width = 155
        self.sidebar_width = self.right_sidebar_width

        self.margin = 12
        self.button_height = 55
        self.button_gap = 8

        self.colors_open = False
        self.shapes_open = False

        self.button_rects = {}
        self.color_rects = {}
        self.shape_rects = {}

        
        self.colors = {
            "Coral": (80, 90, 255),
            "Blue": (255, 120, 40),
            "Mint": (120, 255, 120),
            "Violet": (220, 80, 200),
            "Amber": (30, 190, 255),
            "Cyan": (255, 255, 0),
            "White": (255, 255, 255),
            "Black": (0, 0, 0),
        }

        self.left_buttons = [
            "CANVAS",
            "BRUSH -",
            "BRUSH +",
            "SHAPES",
        ]

        self.right_buttons = [
            "COLORS",
            "ERASER",
            "UNDO",
            "REDO",
            "CLEAR",
            "SAVE",
        ]

  
        self.selected_shape = "FREE"
        self.selected_color = "Violet"


    def draw_button(
        self,
        frame,
        x1,
        y1,
        x2,
        y2,
        label,
        fill_color,
        text_color=(255, 255, 255),
        active=False,
    ):

        cv2.rectangle(
            frame,
            (x1, y1),
            (x2, y2),
            fill_color,
            -1,
        )

        cv2.rectangle(
            frame,
            (x1, y1),
            (x2, y2),
            (110, 115, 130),
            1,
        )

        if active:

            cv2.rectangle(
                frame,
                (x1, y1),
                (x2, y2),
                (0, 235, 255),
                3,
            )

            cv2.rectangle(
                frame,
                (x1 + 4, y1 + 4),
                (x2 - 4, y2 - 4),
                (255, 255, 255),
                1,
            )

        text_size = cv2.getTextSize(
            label,
            cv2.FONT_HERSHEY_SIMPLEX,
            0.52,
            1,
        )[0]

        text_x = (
            x1
            + ((x2 - x1) - text_size[0]) // 2
        )

        text_y = (
            y1
            + ((y2 - y1) + text_size[1]) // 2
        )

        cv2.putText(
            frame,
            label,
            (text_x, text_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.52,
            text_color,
            1,
            cv2.LINE_AA,
        )

  

    def draw(
        self,
        frame,
        current_color_name,
        brush_size,
        eraser,
        canvas_mode,
        shape_mode="FREE",
    ):

        self.button_rects.clear()
        self.color_rects.clear()
        self.shape_rects.clear()

       
        self.selected_shape = shape_mode
        self.selected_color = current_color_name

        left_end = self.left_sidebar_width
        right_start = self.width - self.right_sidebar_width

        
        # LEFT BACKGROUND
      

        left_overlay = frame.copy()

        cv2.rectangle(
            left_overlay,
            (0, 0),
            (left_end, self.height),
            (25, 28, 35),
            -1,
        )

        cv2.addWeighted(
            left_overlay,
            0.90,
            frame,
            0.10,
            0,
            frame,
        )

       

        right_overlay = frame.copy()

        cv2.rectangle(
            right_overlay,
            (right_start, 0),
            (self.width, self.height),
            (25, 28, 35),
            -1,
        )

        cv2.addWeighted(
            right_overlay,
            0.90,
            frame,
            0.10,
            0,
            frame,
        )

        
        # LEFT TITLE
       

        cv2.putText(
            frame,
            "TOOLS",
            (28, 38),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (255, 255, 255),
            2,
        )

       
        # LEFT BUTTONS
        

        y = 70

        left_button_colors = {
            "CANVAS": (170, 85, 125),
            "BRUSH -": (125, 90, 55),
            "BRUSH +": (125, 90, 55),
            "SHAPES": (70, 145, 155),
        }

        for label in self.left_buttons:

            x1 = self.margin
            x2 = self.left_sidebar_width - self.margin

            y1 = y
            y2 = y + self.button_height

            self.button_rects[label] = (
                x1, y1, x2, y2
            )

            display_label = label

            if label == "CANVAS" and canvas_mode:
                display_label = "CAMERA"

            if label == "SHAPES" and shape_mode != "FREE":
                display_label = shape_mode

         
            active = (
                (label == "CANVAS" and canvas_mode)
                or
                (label == "SHAPES" and shape_mode != "FREE")
            )

            self.draw_button(
                frame,
                x1, y1, x2, y2,
                display_label,
                left_button_colors[label],
                active=active,
            )

            y += self.button_height + self.button_gap


        preview_y = y + 25

        cv2.putText(
            frame,
            "BRUSH SIZE",
            (32, preview_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.42,
            (190, 195, 210),
            1,
        )

        preview_radius = max(
            3,
            min(15, brush_size // 2)
        )

        preview_color = self.colors.get(
            current_color_name,
            (255, 255, 255),
        )

        cv2.circle(
            frame,
            (
                self.left_sidebar_width // 2,
                preview_y + 40
            ),
            preview_radius,
            preview_color,
            -1,
        )

        cv2.putText(
            frame,
            f"{brush_size}px",
            (58, preview_y + 75),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.40,
            (255, 255, 255),
            1,
        )

        cv2.putText(
            frame,
            f"MODE: {shape_mode}",
            (25, preview_y + 115),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.36,
            (180, 220, 255),
            1,
        )

      
        # RIGHT TITLE
       

        cv2.putText(
            frame,
            "AIR",
            (right_start + 20, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.70,
            (255, 255, 255),
            2,
        )

        cv2.putText(
            frame,
            "CANVAS AI",
            (right_start + 20, 52),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            (170, 180, 200),
            1,
        )

     
        # RIGHT BUTTONS
        

        y = 70

        right_button_colors = {
            "COLORS": (145, 75, 190),
            "ERASER": (80, 90, 105),
            "UNDO": (175, 110, 55),
            "REDO": (155, 95, 65),
            "CLEAR": (75, 75, 210),
            "SAVE": (75, 160, 90),
        }

        for label in self.right_buttons:

            x1 = right_start + self.margin
            x2 = self.width - self.margin

            y1 = y
            y2 = y + self.button_height

            self.button_rects[label] = (
                x1, y1, x2, y2
            )

            display_label = label

            if label == "ERASER" and eraser:
                display_label = "ERASER ON"

        
            active = (
                (label == "ERASER" and eraser)
                or
                (label == "COLORS" and self.colors_open)
            )

            self.draw_button(
                frame,
                x1, y1, x2, y2,
                display_label,
                right_button_colors[label],
                active=active,
            )

            y += self.button_height + self.button_gap

        # CURRENT COLOR
      

        status_y = self.height - 25

        current_color = self.colors.get(
            current_color_name,
            (255, 255, 255),
        )

        cv2.circle(
            frame,
            (right_start + 20, status_y - 5),
            7,
            current_color,
            -1,
        )

        cv2.circle(
            frame,
            (right_start + 20, status_y - 5),
            10,
            (255, 255, 255),
            2,
        )

        cv2.putText(
            frame,
            current_color_name,
            (right_start + 35, status_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.38,
            (255, 255, 255),
            1,
        )

        # POPUP MENUS
        

        if self.colors_open:
            self.draw_color_palette(frame, right_start)

        if self.shapes_open:
            self.draw_shape_palette(frame)

    # COLOR PALETTE
   

    def draw_color_palette(self, frame, right_start):

        palette_width = 220
        palette_height = 150

        x2 = right_start - 10
        x1 = x2 - palette_width

        y1 = 70
        y2 = y1 + palette_height

        cv2.rectangle(
            frame,
            (x1, y1),
            (x2, y2),
            (35, 38, 46),
            -1,
        )

        cv2.rectangle(
            frame,
            (x1, y1),
            (x2, y2),
            (120, 125, 140),
            1,
        )

        cv2.putText(
            frame,
            "CHOOSE COLOR",
            (x1 + 15, y1 + 24),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            (255, 255, 255),
            1,
        )

        names = list(self.colors.keys())

        box_size = 34
        horizontal_gap = 16
        vertical_gap = 22

        start_x = x1 + 18
        start_y = y1 + 40

        for index, name in enumerate(names):

            row = index // 4
            column = index % 4

            bx1 = start_x + column * (
                box_size + horizontal_gap
            )

            by1 = start_y + row * (
                box_size + vertical_gap
            )

            bx2 = bx1 + box_size
            by2 = by1 + box_size

            self.color_rects[name] = (
                bx1, by1, bx2, by2
            )

            cv2.rectangle(
                frame,
                (bx1, by1),
                (bx2, by2),
                self.colors[name],
                -1,
            )

            if name == self.selected_color:
                cv2.rectangle(
                    frame,
                    (bx1 - 3, by1 - 3),
                    (bx2 + 3, by2 + 3),
                    (255, 255, 255),
                    3,
                )
            else:
                cv2.rectangle(
                    frame,
                    (bx1, by1),
                    (bx2, by2),
                    (230, 230, 230),
                    1,
                )

            cv2.putText(
                frame,
                name[:5],
                (bx1, by2 + 13),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.28,
                (225, 225, 225),
                1,
            )


    def draw_shape_palette(self, frame):

        x1 = self.left_sidebar_width + 10
        x2 = x1 + 165

        options = [
            "FREE",
            "LINE",
            "RECTANGLE",
            "CIRCLE",
            "SMART",
        ]

        button_height = 38
        button_gap = 6
        title_height = 42
        bottom_padding = 10

        palette_height = (
            title_height
            + len(options) * (button_height + button_gap)
            + bottom_padding
        )

        y1 = 190
        y2 = y1 + palette_height

        if y2 > self.height - 10:
            y2 = self.height - 10
            y1 = y2 - palette_height

        if y1 < 10:
            y1 = 10
            y2 = y1 + palette_height

        cv2.rectangle(
            frame,
            (x1, y1),
            (x2, y2),
            (35, 38, 46),
            -1,
        )

        cv2.rectangle(
            frame,
            (x1, y1),
            (x2, y2),
            (120, 125, 140),
            1,
        )

        cv2.putText(
            frame,
            "DRAW MODE",
            (x1 + 25, y1 + 27),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.48,
            (255, 255, 255),
            1,
        )

        shape_colors = {
            "FREE": (95, 95, 115),
            "LINE": (160, 100, 70),
            "RECTANGLE": (85, 125, 175),
            "CIRCLE": (120, 90, 175),
            "SMART": (65, 165, 135),
        }

        button_y = y1 + title_height

        for option in options:

            sx1 = x1 + 10
            sx2 = x2 - 10

            sy1 = button_y
            sy2 = button_y + button_height

            self.shape_rects[option] = (
                sx1, sy1, sx2, sy2
            )

           
            self.draw_button(
                frame,
                sx1, sy1, sx2, sy2,
                option,
                shape_colors[option],
                active=(option == self.selected_shape),
            )

            button_y += button_height + button_gap

   

    @staticmethod
    def point_inside(x, y, rect):

        x1, y1, x2, y2 = rect

        return (
            x1 <= x <= x2
            and y1 <= y <= y2
        )

  
    # MOUSE CLICK
   

    def handle_click(self, x, y):

        # Shape popup priority
        if self.shapes_open:

            for name, rect in self.shape_rects.items():

                if self.point_inside(x, y, rect):

                    self.shapes_open = False

                    return ("SHAPE", name)

        # Color popup priority
        if self.colors_open:

            for name, rect in self.color_rects.items():

                if self.point_inside(x, y, rect):

                    self.colors_open = False

                    return ("COLOR", name)

        for label, rect in self.button_rects.items():

            if self.point_inside(x, y, rect):

                if label == "COLORS":

                    self.colors_open = (
                        not self.colors_open
                    )

                    self.shapes_open = False

                elif label == "SHAPES":

                    self.shapes_open = (
                        not self.shapes_open
                    )

                    self.colors_open = False

                return ("BUTTON", label)

        if self.colors_open:
            self.colors_open = False

        if self.shapes_open:
            self.shapes_open = False

        return None

   
    # GESTURE HOVER
   

    def get_hovered_item(self, x, y):

        if self.shapes_open:

            for name, rect in self.shape_rects.items():

                if self.point_inside(x, y, rect):
                    return ("SHAPE", name)

        if self.colors_open:

            for name, rect in self.color_rects.items():

                if self.point_inside(x, y, rect):
                    return ("COLOR", name)

        for label, rect in self.button_rects.items():

            if self.point_inside(x, y, rect):
                return ("BUTTON", label)

        return None


    def is_inside_drawing_area(self, x, y):

        return (
            self.left_sidebar_width
            < x
            < (self.width - self.right_sidebar_width)
        )
