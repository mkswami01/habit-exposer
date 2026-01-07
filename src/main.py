import cv2
import sys
import os
from pathlib import Path

from core.camera_manager import CameraManager
from core.detector import PhoneDetector
from core.proximity_analyzer import ProximityAnalyzer
from storage.screenshot_manager import ScreenshotManager
from storage.database import DatabaseManager
from utils.config import Config
from utils.logger import setup_logger

class PhoneShamerApp:
    """Main application orchestrator."""

    def __init__(self):
        """Initialize all components."""

        self.config = Config.load()
        self.logger = setup_logger(self.config)
        self.logger.info("Phone Shamer application initialized")

        # Auto-detect display availability (headless vs GUI mode)
        self.has_display = self._check_display()
        if self.has_display:
            self.logger.info("Display detected - GUI mode enabled")
        else:
            self.logger.info("No display detected - Running in headless mode")

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

    def _check_display(self):
        """Check if display is available for GUI."""
        # Check DISPLAY environment variable (Linux/Mac)
        if 'DISPLAY' not in os.environ:
            return False

        # Try to create a test window
        try:
            test_img = cv2.imread('/dev/null')  # Dummy
            cv2.namedWindow('test', cv2.WINDOW_NORMAL)
            cv2.destroyWindow('test')
            return True
        except:
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

            # Run detection
            detections = self.detector.detect(frame)

            # Analyze proximity
            event = self.proximity_analyzer.analyze(detections)

            # If event detected, save screenshot and log to database
            if event:
                annotated = self.detector.annotate_frame(frame, detections)
                screenshot_path = self.screenshot_manager.save_screenshot(
                    annotated, event, detections
                )

                # Save event to database
                self.db.add_event(event, screenshot_path)

                # Get statistics
                stats = self.db.get_statistics_summary()

                self.logger.info(
                    f"Phone usage detected! Screenshot saved: {screenshot_path}"
                )
                self.logger.info(
                    f"Stats - Today: {stats['today_events']}, Total: {stats['total_events']}"
                )

            # Display frame (only if display available)
            if self.has_display:
                annotated = self.detector.annotate_frame(frame, detections)
                cv2.imshow("Phone Shamer", annotated)

                # Check for 'q' key to quit
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
            else:
                # Headless mode - small delay to avoid CPU spinning
                cv2.waitKey(1)

    def cleanup(self):
        """Clean up resources."""
        self.logger.info("Cleaning up...")
        if hasattr(self, "camera_manager") and self.camera_manager is not None:
            self.camera_manager.release()
        if hasattr(self, "db") and self.db is not None:
            self.db.close()
        if self.has_display:
            cv2.destroyAllWindows()
        self.logger.info("Shutdown complete")


def main():
    """Entry point."""
    app = PhoneShamerApp()

    try:
        app.run()
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        app.cleanup()


if __name__ == "__main__":
    main()


