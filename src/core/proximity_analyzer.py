
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict
from collections import deque
import uuid

@dataclass
class PhoneUsageEvent:
    """Represents a phone usage detection event."""
    event_id: str
    start_time: datetime
    person_bbox: List[float]
    phone_bbox: List[float]
    frame_count: int = 0

class ProximityAnalyzer:
    def __init__(self, temporal_frames=5, cooldown_seconds=10):
        self.temporal_frames = temporal_frames
        self.cooldown_seconds = cooldown_seconds

        # Track recent detections (True/False)
        self.detection_history = deque(maxlen=temporal_frames)

        # Current event tracking
        self.active_event: Optional[PhoneUsageEvent] = None
        self.last_event_time: Optional[datetime] = None

    def analyze(self, detections: Dict) -> Optional[PhoneUsageEvent]:
        """Analyze if person is using phone (boxes overlap)."""
        persons = detections['persons']
        phones = detections['phones']

        # No person or phone? Not using phone.
        if not persons or not phones:
            self.detection_history.append(False)
            self._check_event_end()
            return None

        # Check if ANY person overlaps with ANY phone
        overlap_found = False
        best_pair = None

        for person in persons:
            for phone in phones:
                if self._boxes_overlap(person['bbox'], phone['bbox']):
                    overlap_found = True
                    best_pair = (person, phone)
                    break
            if overlap_found:
                break

        if overlap_found:
            self.detection_history.append(True)

            # Check temporal consistency (5 frames in a row)
            if self._is_temporally_consistent():
                return self._handle_confirmed_detection(best_pair)
        else:
            self.detection_history.append(False)
            self._check_event_end()

        return None

    def _boxes_overlap(self, bbox1, bbox2) -> bool:
        """
        Check if two bounding boxes overlap.
        
        Args:
            bbox1: [x1, y1, x2, y2] - first bounding box
            bbox2: [x1, y1, x2, y2] - second bounding box
        
        Returns:å
            True if boxes overlap, False otherwise
        """
        x1_1, y1_1, x2_1, y2_1 = bbox1
        x1_2, y1_2, x2_2, y2_2 = bbox2

        # Check if boxes overlap in X dimension
        # Box1's left edge is left of Box2's right edge AND
        # Box1's right edge is right of Box2's left edge
        x_overlap = x1_1 < x2_2 and x2_1 > x1_2

        # Check if boxes overlap in Y dimension
        # Box1's top edge is above Box2's bottom edge AND
        # Box1's bottom edge is below Box2's top edge
        y_overlap = y1_1 < y2_2 and y2_1 > y1_2

        # They overlap only if BOTH X and Y dimensions overlap
        return x_overlap and y_overlap

    def _is_temporally_consistent(self) -> bool:
        """
        Check if all last N frames had positive detections.

        Returns:
            True if deque is full and all values are True
        """
        # Check if we have enough frames
        if len(self.detection_history) < self.temporal_frames:
            return False

        # Check if ALL recent frames detected overlap
        return all(self.detection_history)

    def _handle_confirmed_detection(self, pair) -> Optional[PhoneUsageEvent]:
        """Create or update event."""
        person, phone = pair
        current_time = datetime.now()

        # Check cooldown
        if self.last_event_time:
            time_since_last = (current_time - self.last_event_time).total_seconds()
            if time_since_last < self.cooldown_seconds:
                return None  # Still in cooldown

        # Create new event if none active
        if self.active_event is None:
            self.active_event = PhoneUsageEvent(
                event_id=str(uuid.uuid4()),
                start_time=current_time,
                person_bbox=person['bbox'].tolist(),
                phone_bbox=phone['bbox'].tolist(),
                frame_count=1
            )
            return self.active_event  # Return event to trigger screenshot
        else:
            # Update existing event
            self.active_event.frame_count += 1
            return None  # Don't trigger multiple screenshots

    def _check_event_end(self):
        """End active event if detection stopped."""
        if self.active_event and not any(self.detection_history):
            self.last_event_time = datetime.now()
            self.active_event = None