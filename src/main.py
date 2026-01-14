import cv2
import sys
import os
from pathlib import Path
import threading
import uvicorn

from core.camera_manager import CameraManager
from core.detector import PhoneDetector
from core.proximity_analyzer import ProximityAnalyzer
from storage.screenshot_manager import ScreenshotManager
from storage.database import DatabaseManager
from utils.config import Config
from utils.logger import setup_logger
from core.gesture_detector import GestureDetector

class HabitExposerApp:
    """Main application orchestrator."""

    def __init__(self):
        """Initialize all components."""

        self.config = Config.load()
        self.logger = setup_logger(self.config)
        self.logger.info("Habit Exposer application initialized")

        # Auto-detect display availability (headless vs GUI mode)
        self.has_display = self._check_display()
        if self.has_display:
            self.logger.info("🖥️ Display detected - Running in GUI mode")
        else:
            self.logger.info("📟 No display detected - Running in headless mode (no cv2.imshow)")

        self.detector = PhoneDetector(
            model_size=self.config.detection.model_size,
            confidence=self.config.detection.confidence_threshold,
            device=self.config.detection.device,
        )
        self.logger.info("Detector initialized")

        self.proximity_analyzer = ProximityAnalyzer(
            temporal_frames=self.config.proximity.temporal_consistency_frames,
            cooldown_seconds=self.config.proximity.cooldown_seconds,
        )
        self.logger.info(f"Proximity analyzer initialized ")
        self.camera_manager = CameraManager(
            device_index=self.config.camera.device_index,
            resolution=(
                self.config.camera.resolution_width,
                self.config.camera.resolution_height,
            ),
        )
        self.logger.info("Camera manager initialized")

        self.screenshot_manager = ScreenshotManager(config=self.config)
        self.logger.info("Screenshot manager initialized")

        self.db = DatabaseManager(self.config.storage.database_path)
        self.logger.info("Database initialized")

        self.gesture_detected = GestureDetector()
        self.monitoring_paused = True

        # Start API server in background thread
        self.api_thread = None
        self._start_api_server()

    def _start_api_server(self):
        """Start the FastAPI server in a background thread."""
        try:
            # Import the FastAPI app
            api_path = Path(__file__).parent.parent / "api.py"
            sys.path.insert(0, str(api_path.parent))

            from api import app

            # Run uvicorn in a separate thread
            def run_api():
                uvicorn.run(
                    app,
                    host="0.0.0.0",
                    port=8000,
                    log_level="warning"  # Reduce noise
                )

            self.api_thread = threading.Thread(target=run_api, daemon=True)
            self.api_thread.start()

            self.logger.info("📊 API server started at http://localhost:8000")
            self.logger.info("📚 API docs at http://localhost:8000/docs")
        except Exception as e:
            self.logger.warning(f"Could not start API server: {e}")

    def _check_display(self):
        """Check if display is available for GUI."""
        # Check DISPLAY environment variable (Linux/Mac)
        display_env = os.environ.get('DISPLAY', None)
        if display_env is None:
            self.logger.debug("DISPLAY env variable not set - headless mode")
            return False

        self.logger.debug(f"DISPLAY env found: {display_env}")

        # Try to create a test window
        try:
            test_img = cv2.imread('/dev/null')  # Dummy
            cv2.namedWindow('test', cv2.WINDOW_NORMAL)
            cv2.destroyWindow('test')
            self.logger.debug("OpenCV window test passed - GUI available")
            return True
        except Exception as e:
            self.logger.debug(f"OpenCV window test failed: {e} - headless mode")
            return False

    def run(self):
        """Run the main detection loop."""
        if self.has_display:
            self.logger.info("Starting detection loop. Press 'q' to quit.")
        else:
            self.logger.info("Starting detection loop. Press Ctrl+C to quit.")
        frame_count = 0

        while True:
            # Read frame
            frame = self.camera_manager.read_frame()
            if frame is None:
                self.logger.warning("Failed to read frame")
                continue

            # Skip frames for performance (process every Nth frame)
            frame_count += 1
            if frame_count % self.config.detection.frame_skip != 0:
                continue

              # 1. Check for gestures (change state)
            gesture = self.gesture_detected.detect_control_gesture(frame)
            if gesture == "start":
                self.monitoring_paused = False
                self.logger.info("🖐️ Monitoring STARTED!")
            elif gesture == "stop":
                self.monitoring_paused = True
                self.logger.info("✊ Monitoring STOPPED!")

            if not self.monitoring_paused:
                 # Detect phones and people
                detections = self.detector.detect(frame)

                # Draw bounding boxes on frame (always show boxes when monitoring!)
                display_frame = self.detector.annotate_frame(frame, detections)

                # Add status text (green - active)
                cv2.putText(display_frame, "MONITORING: ACTIVE", (50, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)

                # Analyze if phone is being used
                event = self.proximity_analyzer.analyze(detections)

                # If phone usage detected, save it!
                if event:
                    screenshot_path = self.screenshot_manager.save_screenshot(
                        display_frame, event, detections
                    )
                    self.db.add_event(event, screenshot_path)
                    self.logger.info(f"📱 Phone usage detected! Screenshot: {screenshot_path}")
            else:
                # Monitoring stopped - just show frame with status
                display_frame = frame.copy()
                cv2.putText(display_frame, "MONITORING: STOPPED", (50, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)

            # Display the frame (only in GUI mode)
            if self.has_display:
                cv2.imshow('Habit Exposer', display_frame)
                if cv2.waitKey(1) == ord('q'):
                    break

    def cleanup(self):
        """Clean up resources."""
        self.logger.info("Cleaning up...")
        if hasattr(self, "camera_manager") and self.camera_manager is not None:
            self.camera_manager.release()
        if hasattr(self, "db") and self.db is not None:
            self.db.close()
        # TODO(human): Close gesture detector
        # if hasattr(self, "gesture_detector") and self.gesture_detector is not None:
        #     self.gesture_detector.close()
        if self.has_display:
            cv2.destroyAllWindows()
        self.logger.info("Shutdown complete")


def main():
    """Entry point."""
    app = HabitExposerApp()

    try:
        app.run()
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        app.cleanup()


if __name__ == "__main__":
    main()


