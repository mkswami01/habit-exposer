import cv2
import numpy as np

class CameraManager:
    def __init__(self, device_index=0, resolution=(1280, 720)):

        
        self.cap = cv2.VideoCapture(device_index)
        if not self.cap.isOpened():
            raise ValueError(f"Failed to open camera with index {device_index}")
        
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])
        self.cap.set(cv2.CAP_PROP_FPS, 30)

    def read_frame(self):
        
        ret, frame = self.cap.read()
        if not ret:
            return None
        return frame

    def release(self):
        """Release the camera capture."""
        self.cap.release()