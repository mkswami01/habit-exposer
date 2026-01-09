"""Gesture detection using MediaPipe's new Gesture Recognizer API."""
import cv2
import time
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision


class GestureDetector:
    """Lightweight gesture detector using MediaPipe's built-in gesture recognition."""

    def __init__(self, model_path='models/gesture_recognizer.task'):
        """
        Initialize the gesture recognizer.

        Args:
            model_path: Path to the gesture_recognizer.task model file
        """
        # Setup options for the recognizer
        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.GestureRecognizerOptions(
            base_options=base_options,
            num_hands=1,  # Only track one hand
            min_hand_detection_confidence=0.7,
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=0.5
        )

        # Create the gesture recognizer
        self.recognizer = vision.GestureRecognizer.create_from_options(options)

        self.last_gesture_time = 0
        self.cooldown_seconds = 1.0  # Wait 1 second between gesture detections

        print("✅ Gesture Recognizer initialized")
        print("   Recognizes: Open_Palm, Thumbs_Up, Thumbs_Down, Victory, Pointing_Up, Closed_Fist, ILoveYou")

    def detect_control_gesture(self, frame):
        """
        Detect control gestures (Open_Palm or Closed_Fist).

        Args:
            frame: Input frame (BGR format from OpenCV)

        Returns:
            str: "start" if Open_Palm detected
                 "stop" if Closed_Fist detected
                 None if no control gesture detected
        """
        # Check cooldown
        current_time = time.time()
        if current_time - self.last_gesture_time < self.cooldown_seconds:
            return None

        # Convert BGR to RGB (MediaPipe uses RGB)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Create MediaPipe Image
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

        # Recognize gestures
        result = self.recognizer.recognize(mp_image)

        # Check if any hands detected
        if not result.gestures:
            return None

        # Check handedness (only respond to RIGHT hand)
        handedness = result.handedness[0][0]
        hand_label = handedness.category_name  # "Left" or "Right"

        if hand_label != "Right":
            print(f"Ignoring {hand_label} hand")
            return None

        # Get the top gesture for the first hand
        top_gesture = result.gestures[0][0]
        gesture_name = top_gesture.category_name
        confidence = top_gesture.score

        print(f"Detected RIGHT hand: {gesture_name} (confidence: {confidence:.2f})")

        # Check for control gestures
        if confidence > 0.5:
            if gesture_name == "Open_Palm":
                self.last_gesture_time = current_time
                return "start"
            elif gesture_name == "Closed_Fist":
                self.last_gesture_time = current_time
                return "stop"

        return None

    def close(self):
        """Clean up resources."""
        self.recognizer.close()
