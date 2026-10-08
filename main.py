
import cv2
import time

from config import (
    CAMERA_INDEX,
    FRAME_WIDTH,
    FRAME_HEIGHT,
    WINDOW_NAME,
    SHOW_LANDMARKS,
)

from hand_tracker import HandTracker
from gesture_controller import GestureController
from drawing_canvas import DrawingCanvas
from ui_manager import UIManager
from feedback_manager import FeedbackManager


mouse_click = None




def mouse_callback(event, x, y, flags, param):
    global mouse_click

    if event == cv2.EVENT_LBUTTONDOWN:
        mouse_click = (x, y)



# PROCESS ACTION


def process_action(
    action,
    ui,
    drawing_canvas,
    current_color_name,
    canvas_mode,
    feedback_manager,
):

    if not action:
        return current_color_name, canvas_mode

    action_type, value = action

   
    # SHAPE SELECTION
   

    if action_type == "SHAPE":

        drawing_canvas.set_shape_mode(
            value
        )

        ui.shapes_open = False

        print(
            f"Selected drawing mode: {value}"
        )

        
        feedback_manager.show(
            f"Mode: {value}",
            "INFO"
        )

        return current_color_name, canvas_mode

   
    # COLOR
   

    if action_type == "COLOR":

        current_color_name = value

        drawing_canvas.set_color(
            ui.colors[value]
        )

        print(
            f"Color selected: {value}"
        )

       
        feedback_manager.show(
            f"Color: {value}",
            "INFO"
        )

        return current_color_name, canvas_mode

  
    # BUTTON
   

    if action_type != "BUTTON":
        return current_color_name, canvas_mode

    if value == "COLORS":

        ui.colors_open = (
            not ui.colors_open
        )

        ui.shapes_open = False

        print(
            "Color palette:",
            ui.colors_open
        )

    elif value == "SHAPES":

        ui.shapes_open = (
            not ui.shapes_open
        )

        ui.colors_open = False

        print(
            "Shape palette:",
            ui.shapes_open
        )

    elif value == "ERASER":

        drawing_canvas.set_eraser(
            not drawing_canvas.eraser
        )

        print(
            "Eraser:",
            drawing_canvas.eraser
        )

       
        feedback_manager.show(
            "Eraser ON"
            if drawing_canvas.eraser
            else "Eraser OFF",
            "INFO"
        )

    elif value == "CLEAR":

        drawing_canvas.clear()

        print(
            "Canvas cleared."
        )

      
        feedback_manager.show(
            "Canvas cleared",
            "WARNING"
        )

    elif value == "BRUSH +":

        drawing_canvas.increase_brush()

        print(
            "Brush:",
            drawing_canvas.brush_size
        )

      
        feedback_manager.show(
            f"Brush: {drawing_canvas.brush_size}px",
            "INFO"
        )

    elif value == "BRUSH -":

        drawing_canvas.decrease_brush()

        print(
            "Brush:",
            drawing_canvas.brush_size
        )

      
        feedback_manager.show(
            f"Brush: {drawing_canvas.brush_size}px",
            "INFO"
        )

    elif value == "CANVAS":

        canvas_mode = not canvas_mode

        drawing_canvas.end_stroke()
        drawing_canvas.cancel_shape()

       
        if drawing_canvas.smart_active:
            drawing_canvas.finish_smart_draw()

        print(
            "Canvas mode:",
            canvas_mode
        )

       
        feedback_manager.show(
            "White Canvas"
            if canvas_mode
            else "Camera Mode",
            "INFO"
        )

    elif value == "UNDO":

        drawing_canvas.end_stroke()
        drawing_canvas.cancel_shape()

        print(
            "UNDO CLICK DETECTED"
        )

        if drawing_canvas.undo():

            print(
                "Undo successful."
            )

         
            feedback_manager.show(
                "Undo successful",
                "SUCCESS"
            )

        else:

            print(
                "Nothing to undo."
            )

            feedback_manager.show(
                "Nothing to undo",
                "WARNING"
            )

    elif value == "REDO":

        drawing_canvas.end_stroke()
        drawing_canvas.cancel_shape()

        print(
            "REDO CLICK DETECTED"
        )

        if drawing_canvas.redo():

            print(
                "Redo successful."
            )

         
            feedback_manager.show(
                "Redo successful",
                "SUCCESS"
            )

        else:

            print(
                "Nothing to redo."
            )

          
            feedback_manager.show(
                "Nothing to redo",
                "WARNING"
            )

    elif value == "SAVE":

        drawing_canvas.end_stroke()

        print(
            "SAVE CLICK DETECTED"
        )

        saved_path = (
            drawing_canvas.save()
        )

        if saved_path:

            print(
                f"Save successful: {saved_path}"
            )

          
            feedback_manager.show(
                "Drawing saved",
                "SUCCESS"
            )

        else:

            print(
                "Save failed."
            )

           
            feedback_manager.show(
                "Save failed",
                "ERROR"
            )

    return current_color_name, canvas_mode



# MAIN


def main():

    global mouse_click

    print("=" * 60)
    print("                   AIRCANVAS AI")
    print("=" * 60)

    print("AirCanvas AI - Hand Gesture Drawing Studio")
    print()

    print("Gesture Control")
    print()
    print("  V Sign          -> Move Cursor")
    print("  Thumb + Index   -> Click")
    print("  Index Only      -> Draw / Shape")
    print()

    print("Shape Modes:")
    print("  FREE")
    print("  LINE")
    print("  RECTANGLE")
    print("  CIRCLE")
    print("  SMART")
    print()

    print("SMART MODE:")
    print("  Draw rough Line / Circle / Rectangle")
    print("  Change gesture to finish recognition")
    print()

    print("STAGE:")
    print("  Action notifications enabled")
    print("  Smart recognition feedback enabled")
    print()

    print("Q -> Quit")
    print()


    # CAMERA

    cap = cv2.VideoCapture(
        CAMERA_INDEX
    )

    cap.set(
        cv2.CAP_PROP_FRAME_WIDTH,
        FRAME_WIDTH
    )

    cap.set(
        cv2.CAP_PROP_FRAME_HEIGHT,
        FRAME_HEIGHT
    )

    if not cap.isOpened():

        print(
            "ERROR: Camera could not open."
        )

        return

    
    # OBJECTS
   

    tracker = HandTracker()
    gestures = GestureController()

    drawing_canvas = None
    ui = None

    feedback_manager = FeedbackManager()

    current_color_name = "Violet"

    canvas_mode = False

  
    # CURSOR

    cursor_x = None
    cursor_y = None

    last_click_time = 0
    click_cooldown = 0.45

    previous_gesture = "NO HAND"

    
    # WINDOW


    cv2.namedWindow(
        WINDOW_NAME
    )

    cv2.setMouseCallback(
        WINDOW_NAME,
        mouse_callback
    )

    
    # MAIN LOOP

    while True:

        success, frame = cap.read()

        if not success:

            print(
                "ERROR: Camera frame unavailable."
            )

            break

        frame = cv2.flip(
            frame,
            1
        )

        height, width, _ = frame.shape

        # INITIALIZE

        if drawing_canvas is None:

            drawing_canvas = DrawingCanvas(
                width,
                height
            )

            ui = UIManager(
                width,
                height
            )

            drawing_canvas.set_color(
                ui.colors[current_color_name]
            )

            feedback_manager.show(
                "Welcome to AirCanvas AI",
                "SUCCESS",
                3.0
            )

    
        # HAND DETECTION

        result = tracker.detect(
            frame
        )

        landmarks = tracker.get_landmarks(
            result,
            width,
            height
        )

        gesture = "NO HAND"
        virtual_cursor = None

        # HAND FOUND

        if landmarks:

            gesture = gestures.recognize(
                landmarks
            )

            index_tip = landmarks[8]


            # RESPONSIVE CURSOR


            if cursor_x is None:

                cursor_x = index_tip[0]
                cursor_y = index_tip[1]

            else:

                dx = (
                    index_tip[0]
                    - cursor_x
                )

                dy = (
                    index_tip[1]
                    - cursor_y
                )

                distance = (
                    dx * dx
                    + dy * dy
                ) ** 0.5

                if distance < 3:

                    dx = 0
                    dy = 0

                if distance < 10:

                    smoothing = 0.45

                elif distance < 30:

                    smoothing = 0.65

                elif distance < 60:

                    smoothing = 0.80

                else:

                    smoothing = 0.92

                cursor_x = int(
                    cursor_x
                    + dx * smoothing
                )

                cursor_y = int(
                    cursor_y
                    + dy * smoothing
                )

            virtual_cursor = (
                cursor_x,
                cursor_y
            )

            # HOVER

            if gesture == "HOVER":

                drawing_canvas.end_stroke()

               

                if drawing_canvas.smart_active:

                    detected = (
                        drawing_canvas.finish_smart_draw()
                    )

                    if detected:

                        print(
                            f"SMART RESULT: {detected}"
                        )

                       
                        feedback_manager.show(
                            f"Smart: {detected}",
                            "SMART",
                            2.0
                        )

             

                elif (
                    drawing_canvas.shape_active
                    and
                    drawing_canvas.shape_mode
                    not in ["FREE", "SMART"]
                ):

                    current_shape = (
                        drawing_canvas.shape_mode
                    )

                    if drawing_canvas.finish_shape():

                        print(
                            f"{current_shape} created."
                        )


            elif gesture == "DRAW":

                if ui.is_inside_drawing_area(
                    index_tip[0],
                    index_tip[1]
                ):

                    
                    # FREE DRAW
                    

                    if (
                        drawing_canvas.shape_mode
                        == "FREE"
                    ):

                        if (
                            previous_gesture
                            != "DRAW"
                        ):

                            drawing_canvas.end_stroke()

                        else:

                            drawing_canvas.draw(
                                index_tip
                            )

                   
                    #SMART DRAW
                    

                    elif (
                        drawing_canvas.shape_mode
                        == "SMART"
                    ):

                        drawing_canvas.end_stroke()

                        if (
                            not
                            drawing_canvas.smart_active
                        ):

                            drawing_canvas.start_smart_draw(
                                index_tip
                            )

                        else:

                            drawing_canvas.update_smart_draw(
                                index_tip
                            )

                

                    else:

                        drawing_canvas.end_stroke()

                        if (
                            not
                            drawing_canvas.shape_active
                        ):

                            drawing_canvas.start_shape(
                                index_tip
                            )

                        else:

                            drawing_canvas.update_shape(
                                index_tip
                            )

                else:

                    drawing_canvas.end_stroke()

                    # SMART
                    if drawing_canvas.smart_active:

                        detected = (
                            drawing_canvas.finish_smart_draw()
                        )

                        if detected:

                            print(
                                f"SMART RESULT: {detected}"
                            )

                        
                            feedback_manager.show(
                                f"Smart: {detected}",
                                "SMART",
                                2.0
                            )

                    
                    elif drawing_canvas.shape_active:

                        drawing_canvas.finish_shape()

            
            # OTHER GESTURES
           

            else:

                drawing_canvas.end_stroke()

                # SMART
                if drawing_canvas.smart_active:

                    detected = (
                        drawing_canvas.finish_smart_draw()
                    )

                    if detected:

                        print(
                            f"SMART RESULT: {detected}"
                        )

                    
                        feedback_manager.show(
                            f"Smart: {detected}",
                            "SMART",
                            2.0
                        )

                # NORMAL SHAPE
                elif (
                    drawing_canvas.shape_active
                    and
                    drawing_canvas.shape_mode
                    not in ["FREE", "SMART"]
                ):

                    drawing_canvas.finish_shape()

           
            # PINCH CLICK
            

            pinch_click = (
                gestures.detect_pinch_click(
                    landmarks
                )
            )

            current_time = time.time()

            if (
                pinch_click
                and virtual_cursor is not None
                and (
                    current_time
                    - last_click_time
                ) > click_cooldown
            ):

                hovered_item = (
                    ui.get_hovered_item(
                        cursor_x,
                        cursor_y
                    )
                )

                if hovered_item:

                    current_color_name, canvas_mode = (
                        process_action(
                            hovered_item,
                            ui,
                            drawing_canvas,
                            current_color_name,
                            canvas_mode,
                            feedback_manager,
                        )
                    )

                    last_click_time = (
                        current_time
                    )

         
            # LANDMARKS
     

            if (
                SHOW_LANDMARKS
                and not canvas_mode
            ):

                tracker.draw_landmarks(
                    frame,
                    landmarks
                )

        # NO HAND


        else:

            drawing_canvas.end_stroke()

       
      

            if drawing_canvas.smart_active:

                detected = (
                    drawing_canvas.finish_smart_draw()
                )

                if detected:

                    print(
                        f"SMART RESULT: {detected}"
                    )

               
                    feedback_manager.show(
                        f"Smart: {detected}",
                        "SMART",
                        2.0
                    )

         

            elif (
                drawing_canvas.shape_active
                and
                drawing_canvas.shape_mode
                not in ["FREE", "SMART"]
            ):

                drawing_canvas.finish_shape()

            cursor_x = None
            cursor_y = None

            gestures.pinch_active = False

       

        frame = drawing_canvas.overlay(
            frame,
            white_canvas=canvas_mode
        )

     

        frame = (
            drawing_canvas.draw_shape_preview(
                frame
            )
        )



        frame = (
            drawing_canvas.draw_smart_preview(
                frame
            )
        )

        

        cv2.rectangle(
            frame,
            (170, 15),
            (530, 115),
            (30, 32, 40),
            -1
        )

        cv2.putText(
            frame,
            "AIRCANVAS AI",
            (190, 45),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.72,
            (255, 255, 255),
            2
        )

        cv2.putText(
            frame,
            f"Gesture: {gesture}",
            (190, 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.50,
            (120, 255, 180),
            1
        )

        cv2.putText(
            frame,
            f"Mode: {drawing_canvas.shape_mode}",
            (190, 92),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.46,
            (100, 210, 255),
            1
        )

      

        if (
            drawing_canvas.shape_mode
            == "SMART"
        ):

            instruction = (
                f"Smart: "
                f"{drawing_canvas.last_detected_shape}"
            )

        elif gesture == "HOVER":

            instruction = (
                "V Cursor | Pinch to Click"
            )

        elif gesture == "DRAW":

            if (
                drawing_canvas.shape_mode
                == "FREE"
            ):

                instruction = (
                    "Drawing..."
                )

            else:

                instruction = (
                    f"Creating {drawing_canvas.shape_mode}"
                )

        else:

            instruction = (
                "Show V sign to control"
            )

        cv2.putText(
            frame,
            instruction,
            (190, 110),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.38,
            (210, 210, 220),
            1
        )

     
        # UI
      

        ui.draw(
            frame,
            current_color_name,
            drawing_canvas.brush_size,
            drawing_canvas.eraser,
            canvas_mode,
            drawing_canvas.shape_mode,
        )

       

        if (
            virtual_cursor is not None
            and gesture == "HOVER"
        ):

            cv2.circle(
                frame,
                virtual_cursor,
                14,
                (255, 255, 255),
                2
            )

            cv2.circle(
                frame,
                virtual_cursor,
                5,
                (0, 220, 255),
                -1
            )

            hovered_item = (
                ui.get_hovered_item(
                    cursor_x,
                    cursor_y
                )
            )

            if hovered_item:

                item_type, item_name = (
                    hovered_item
                )

                cv2.putText(
                    frame,
                    f"SELECT: {item_name}",
                    (
                        180,
                        height - 30
                    ),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.58,
                    (0, 220, 255),
                    2
                )


        if mouse_click is not None:

            mx, my = mouse_click

            action = ui.handle_click(
                mx,
                my
            )

            mouse_click = None

            if action:

                
                if not (
                    action[0] == "BUTTON"
                    and action[1] in [
                        "COLORS",
                        "SHAPES",
                    ]
                ):

                    current_color_name, canvas_mode = (
                        process_action(
                            action,
                            ui,
                            drawing_canvas,
                            current_color_name,
                            canvas_mode,
                            feedback_manager,
                        )
                    )

     

        feedback_manager.draw(frame)

      

        cv2.imshow(
            WINDOW_NAME,
            frame
        )

    

        key = cv2.waitKey(1) & 0xFF

        if key == ord("c"):

            drawing_canvas.clear()

            print(
                "Canvas cleared."
            )

       
            feedback_manager.show(
                "Canvas cleared",
                "WARNING"
            )

        elif key == ord("q"):

            break

        previous_gesture = gesture

   

    tracker.close()

    cap.release()

    cv2.destroyAllWindows()

    print()
    print(
        "AirCanvas AI closed."
    )


if __name__ == "__main__":
    main()
