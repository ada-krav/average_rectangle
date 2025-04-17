import cv2
import numpy as np

from abc import ABC, abstractmethod
from av import VideoFrame
from typing import Tuple, Optional, Dict


class DrawingStrategy(ABC):
    def __init__(self, sizing_options: Optional[Dict] = None, *args, **kwargs):
        self.sizing_options = sizing_options or {}

    @abstractmethod
    def draw(self, frame: np.ndarray, color_BGR: Tuple[int, int, int]) -> np.ndarray:
        pass


class RectangleStrategy(DrawingStrategy):
    def __init__(self, sizing_options: Optional[Dict] = None, *args, **kwargs):
        super().__init__(sizing_options, *args, **kwargs)
        self.height_proportion = self.sizing_options.get("height_proportion", 0.3) #  30% by default
        self.width_proportion = self.sizing_options.get("width_proportion", 0.3)

    def draw(self, frame: np.ndarray, color_BGR: Tuple[int, int, int]) -> np.ndarray:
        h, w, _ = frame.shape
        top_left, bottom_right = self._get_rectangle_coordinates(h, w)
        cv2.rectangle(frame, top_left, bottom_right, color_BGR, cv2.FILLED)
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


class IoStrategy(ABC):
    @abstractmethod
    def to_ndarray(self, image_data) -> np.ndarray:
        pass

    @abstractmethod
    def from_ndarray(self, image_data: np.ndarray):
        pass


class JpegIo(IoStrategy):
    def to_ndarray(self, image_data) -> np.ndarray:
        nparr = np.frombuffer(image_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if frame is None:
            raise ValueError("Failed to decode image")
        return frame

    def from_ndarray(self, frame: np.ndarray):
        _, buffer = cv2.imencode(".jpg", frame)
        return buffer.tobytes()


class PyAVframeIo(IoStrategy):
    def to_ndarray(self, image_data) -> np.ndarray:
        return image_data.to_ndarray(format="bgr24")

    def from_ndarray(self, frame: np.ndarray):
        return VideoFrame.from_ndarray(frame, format="bgr24")


class ImageProcessor:
    def __init__(
        self,
        input_strategy: Optional[IoStrategy] = None,
        output_strategy: Optional[IoStrategy] = None,
        drawing_strategy: Optional[DrawingStrategy] = None,
    ):
        self._input_strategy = input_strategy or JpegIo()
        self._output_strategy = output_strategy or input_strategy or JpegIo()
        self._drawing_strategy = drawing_strategy or RectangleStrategy()

    def process_image(self, image_data: bytes, color: Tuple[int, int, int]) -> bytes:
        frame = self._input_strategy.to_ndarray(image_data)

        if (
            isinstance(color, tuple)
            and len(color) == 3
            and all(0 <= c <= 255 for c in color)
        ):
            frame = self._drawing_strategy.draw(frame, color_BGR=color[::-1])

        output_frame = self._output_strategy.from_ndarray(frame)
        return output_frame
