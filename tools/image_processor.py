import cv2
import numpy as np

from abc import ABC, abstractmethod
from typing import Tuple, Optional, Dict


class DrawingStrategy(ABC):

    def __init__(self, sizing_options: Optional[Dict] = None, *args, **kwargs):
        self.sizing_options = sizing_options or {}

    @abstractmethod
    def draw(self, frame: np.ndarray, color: Tuple[int, int, int]) -> np.ndarray:
        pass


class RectangleStrategy(DrawingStrategy):

    def __init__(self, sizing_options: Optional[Dict] = None, *args, **kwargs):
        super().__init__(sizing_options, *args, **kwargs)
        self.height_proportion = self.sizing_options.get("height_proportion", 0.3) #  30% by default
        self.width_proportion = self.sizing_options.get("width_proportion", 0.3)

    def draw(self, frame: np.ndarray, color: Tuple[int, int, int]) -> np.ndarray:
        h, w, _ = frame.shape
        top_left, bottom_right = self._get_rectangle_coordinates(h, w)
        cv2.rectangle(frame, top_left, bottom_right, color, cv2.FILLED)
        return frame

    def _get_rectangle_coordinates(
        self, height: int, width: int
    ) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        center_x, center_y = width // 2, height // 2
        shape_height = int(height * self.height_proportion)
        shape_width = int(width * self.width_proportion)

        top_left = (center_x - shape_width // 2, center_y - shape_height // 2)
        bottom_right = (center_x + shape_width // 2, center_y + shape_height // 2)
        return top_left, bottom_right


class ImageProcessor:

    def __init__(self, strategy: Optional[DrawingStrategy] = None):
        self._strategy = strategy or RectangleStrategy()

    def process_image(self, image_data: bytes, color: Tuple[int, int, int]) -> bytes:
        if not (
            isinstance(color, tuple)
            and len(color) == 3
            and all(0 <= c <= 255 for c in color)
        ):
            raise ValueError("Color must be a 3-tuple with values 0-255")

        nparr = np.frombuffer(image_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if frame is None:
            raise ValueError("Failed to decode image")

        frame = self._strategy.draw(frame, color[::-1])  # reversing to get BGR color tuple (OpenCV historically works with BGR)
        _, buffer = cv2.imencode(".jpg", frame)
        return buffer.tobytes()
