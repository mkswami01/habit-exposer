from ultralytics import YOLO
import numpy as np
import cv2
from typing import Dict, List, Tuple

class PhoneDetector:
    # Class constants
    PERSON_CLASS_ID = 0
    PHONE_CLASS_ID = 67

    def __init__(self, model_size='n', confidence=0.5, device='cpu'):
        """
        Args:
            model_size: 'n', 's', 'm', 'l', 'x' (nano to extra-large)
            confidence: Detection confidence threshold (0.0-1.0)
            device: 'cpu', 'cuda', or 'mps' (Apple Silicon)
        """

        self.model = YOLO(f'yolov8{model_size}.pt')
        self.confidence = confidence
        self.device = device

    def detect(self, frame: np.ndarray) -> Dict[str, List[Dict]]:
        """
        Detect persons and phones in frame.
        
        Returns:
            {
                'persons': [{'bbox': [x1,y1,x2,y2], 'confidence': 0.95, 'center': (cx,cy)}, ...],
                'phones': [{'bbox': [x1,y1,x2,y2], 'confidence': 0.87, 'center': (cx,cy)}, ...]
            }
        """
        persons = []
        phones = []
        results = self.model(frame, conf=self.confidence, device=self.device, verbose=False)
        for result in results:
            for box in result.boxes:
                class_id = int(box.cls[0])
                bbox = box.xyxy[0].cpu().numpy()
                confidence = float(box.conf[0])
                center = self._calculate_center(bbox)
                if class_id == self.PERSON_CLASS_ID:
                    persons.append({
                        'bbox': bbox,
                        'confidence': confidence,
                        'center': center}
                    )
                elif class_id == self.PHONE_CLASS_ID:
                    phones.append({
                        'bbox': bbox,
                        'confidence': confidence,
                        'center': center
                    })
        return {
            'persons': persons,
            'phones': phones
        }

    @staticmethod
    def _calculate_center(bbox) -> Tuple[float, float]:
        """Calculate center of bounding box."""
        x1, y1, x2, y2 = bbox
        return ((x1 + x2) / 2, (y1 + y2) / 2)

    def annotate_frame(self, frame: np.ndarray, detections: Dict) -> np.ndarray:
        """Draw bounding boxes on frame."""
        annotated = frame.copy()
        for person in detections['persons']:
            cv2.rectangle(annotated, (int(person['bbox'][0]), int(person['bbox'][1])), (int(person['bbox'][2]), int(person['bbox'][3])), (0, 255, 0), 2)
            cv2.putText(annotated, f"Person {person['confidence']:.2f}", (int(person['bbox'][0]), int(person['bbox'][1])), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        for phone in detections['phones']:
            cv2.rectangle(annotated, (int(phone['bbox'][0]), int(phone['bbox'][1])), (int(phone['bbox'][2]), int(phone['bbox'][3])), (0, 0, 255), 2)
            cv2.putText(annotated, f"Phone {phone['confidence']:.2f}", (int(phone['bbox'][0]), int(phone['bbox'][1])), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        return annotated