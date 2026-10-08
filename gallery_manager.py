import os
import cv2
import numpy as np
from datetime import datetime
from config import SAVE_DIR


class GalleryManager:
    """Keyboard/mouse gallery for existing AirCanvas PNG exports."""

    def __init__(self):
        self.opened = False
        self.files = []
        self.selected = 0
        self.page = 0
        self.page_size = 6
        self.click_regions = []
        self.preview_cache = {}
        self.message = ''

    def refresh(self):
        os.makedirs(SAVE_DIR, exist_ok=True)
        self.files = sorted(
            [os.path.join(SAVE_DIR, name) for name in os.listdir(SAVE_DIR)
             if name.lower().endswith('.png') and os.path.isfile(os.path.join(SAVE_DIR, name))],
            key=lambda path: os.path.getmtime(path), reverse=True,
        )
        self.selected = min(self.selected, max(0, len(self.files) - 1))
        self.page = self.selected // self.page_size
        self.preview_cache.clear()

    def toggle(self):
        self.opened = not self.opened
        if self.opened:
            self.refresh()
        return self.opened

    def selected_path(self):
        return self.files[self.selected] if self.files else None

    def navigate(self, step):
        if self.files:
            self.selected = (self.selected + step) % len(self.files)
            self.page = self.selected // self.page_size

    def handle_click(self, x, y):
        for rect, action, value in self.click_regions:
            x1, y1, x2, y2 = rect
            if x1 <= x <= x2 and y1 <= y <= y2:
                if action == 'select':
                    self.selected = value
                    self.page = value // self.page_size
                elif action == 'prev':
                    self.page = max(0, self.page - 1)
                    self.selected = min(self.selected, len(self.files) - 1)
                elif action == 'next':
                    self.page = min(max(0, (len(self.files) - 1) // self.page_size), self.page + 1)
                elif action == 'close':
                    self.opened = False
                return True
        return False

    @staticmethod
    def _fit(image, width, height):
        ih, iw = image.shape[:2]
        scale = min(width / max(1, iw), height / max(1, ih))
        size = (max(1, int(iw * scale)), max(1, int(ih * scale)))
        return cv2.resize(image, size, interpolation=cv2.INTER_AREA if scale < 1 else cv2.INTER_LINEAR)

    def _preview(self, path, width, height):
        key = (path, width, height)
        if key not in self.preview_cache:
            image = cv2.imread(path, cv2.IMREAD_COLOR)
            self.preview_cache[key] = self._fit(image, width, height) if image is not None else None
        return self.preview_cache[key]

    def render(self, frame):
        if not self.opened:
            return frame
        h, w = frame.shape[:2]
        # Dedicated full-window gallery, preserving camera and drawing state underneath.
        
        output = np.full_like(frame, (29, 32, 40))
        self.click_regions = []
        cv2.putText(output, 'AIRCANVAS GALLERY', (16, 34), cv2.FONT_HERSHEY_SIMPLEX,
                    0.67, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(output, 'G/Esc: Close | Arrows: Select | L: Load | E: Export | R: Refresh',
                    (16, 56), cv2.FONT_HERSHEY_SIMPLEX, 0.36, (190, 210, 220), 1, cv2.LINE_AA)
        close_rect = (w - 44, 12, w - 10, 44)
        cv2.rectangle(output, close_rect[:2], close_rect[2:], (75, 80, 100), -1)
        cv2.putText(output, 'X', (w - 35, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        self.click_regions.append((close_rect, 'close', None))
        if not self.files:
            cv2.putText(output, 'No saved PNG drawings yet. Save a drawing first.',
                        (20, h // 2), cv2.FONT_HERSHEY_SIMPLEX, 0.47, (220, 220, 220), 1)
            return output

        # A compact grid of thumbnails on the left; large selected preview on the right.
        grid_width = max(165, int(w * 0.48))
        cols = 2
        gap = 9
        tile_w = max(60, (grid_width - 3 * gap) // cols)
        tile_h = max(60, (h - 118 - 2 * gap) // 3)
        first = self.page * self.page_size
        for index in range(first, min(first + self.page_size, len(self.files))):
            local = index - first
            row, col = divmod(local, cols)
            x1 = gap + col * (tile_w + gap)
            y1 = 75 + row * (tile_h + gap)
            x2, y2 = x1 + tile_w, y1 + tile_h
            selected = index == self.selected
            cv2.rectangle(output, (x1, y1), (x2, y2), (90, 190, 225) if selected else (65, 70, 80), 2)
            thumbnail = self._preview(self.files[index], tile_w - 12, tile_h - 30)
            if thumbnail is not None:
                th, tw = thumbnail.shape[:2]
                px = x1 + (tile_w - tw) // 2
                py = y1 + 4 + (tile_h - 30 - th) // 2
                output[py:py+th, px:px+tw] = thumbnail
            name = os.path.basename(self.files[index])
            cv2.putText(output, name[:max(8, (tile_w - 10) // 7)], (x1 + 5, y2 - 9),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.30, (245, 245, 245), 1, cv2.LINE_AA)
            self.click_regions.append(((x1, y1, x2, y2), 'select', index))

        preview_x = grid_width + 12
        preview_w = max(40, w - preview_x - 12)
        preview_y = 83
        preview_h = max(40, h - 190)
        cv2.rectangle(output, (preview_x, preview_y),
                      (preview_x + preview_w, preview_y + preview_h), (75, 80, 95), 1)
        path = self.selected_path()
        preview = self._preview(path, preview_w - 10, preview_h - 10)
        if preview is not None:
            ph, pw = preview.shape[:2]
            px = preview_x + (preview_w - pw) // 2
            py = preview_y + (preview_h - ph) // 2
            output[py:py+ph, px:px+pw] = preview
        filename = os.path.basename(path)
        date_text = datetime.fromtimestamp(os.path.getmtime(path)).strftime('%Y-%m-%d %H:%M:%S')
        cv2.putText(output, filename[:max(10, preview_w // 8)], (preview_x, h - 89),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.38, (240, 240, 240), 1)
        cv2.putText(output, date_text, (preview_x, h - 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.38, (180, 200, 210), 1)
        cv2.putText(output, f'{self.selected + 1}/{len(self.files)} | Page {self.page + 1}',
                    (16, h - 25), cv2.FONT_HERSHEY_SIMPLEX, 0.46, (230, 230, 230), 1)
        cv2.putText(output, 'Left/Right: Browse', (preview_x, h - 42),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.36, (220, 220, 220), 1)
        return output

    def load_selected(self, drawing_canvas):
        path = self.selected_path()
        if not path:
            return False
        image = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        if image is None:
            return False
        if image.ndim == 2:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        elif image.shape[2] == 4:
            image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)
        if image.shape[:2] != (drawing_canvas.height, drawing_canvas.width):
            image = cv2.resize(image, (drawing_canvas.width, drawing_canvas.height), interpolation=cv2.INTER_AREA)
        drawing_canvas.end_stroke()
        drawing_canvas.cancel_shape()
        drawing_canvas.smart_active = False
        drawing_canvas.smart_recognizer.reset()
        drawing_canvas.canvas = image.copy()
        # Existing exports have an opaque white background. Treat white as background
        # when loading so white canvas doesn't cover the live camera unnecessarily.
        grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        drawing_canvas.mask = np.where(grayscale < 250, 255, 0).astype(np.uint8)
        drawing_canvas.previous_point = None
        drawing_canvas.stroke_changed = False
        drawing_canvas.save_history()
        return True

    def export_selected(self):
        path = self.selected_path()
        if not path:
            return None
        import shutil
        export_dir = os.path.join(SAVE_DIR, 'exports')
        os.makedirs(export_dir, exist_ok=True)
        stem = os.path.splitext(os.path.basename(path))[0]
        stamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        target = os.path.join(export_dir, f'{stem}_export_{stamp}.png')
        shutil.copy2(path, target)
        return target