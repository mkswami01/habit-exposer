"""Screenshot capture and storage manager."""

import cv2
import json
from pathlib import Path
from datetime import datetime
from typing import Dict
import numpy as np


class ScreenshotManager:
    """Manages screenshot capture and storage."""

    def __init__(self, config):
        """
        Initialize screenshot manager.

        Args:
            config: Config object with screenshot settings
        """
        self.config = config
        self.base_path = Path(config.storage.screenshots_base_path)
        self.quality = config.screenshot.quality
        self.save_enabled = config.screenshot.save_enabled

    def save_screenshot(self, frame: np.ndarray, event, detections: Dict) -> str:
        """
        Save screenshot and metadata.

        Args:
            frame: Annotated frame to save
            event: PhoneUsageEvent object
            detections: Detection dictionary

        Returns:
            Path to saved screenshot
        """
        if not self.save_enabled:
            return ""

        # Create folder for today
        folder = self._create_date_folder()

        # Generate filename
        filename = self._generate_filename(event)

        # Full paths
        image_path = folder / f"{filename}.jpg"
        json_path = folder / f"{filename}.json"

        # Save image
        cv2.imwrite(str(image_path), frame, [cv2.IMWRITE_JPEG_QUALITY, self.quality])

        # Save metadata
        self._save_metadata(json_path, event, detections)

        return str(image_path)

    def _create_date_folder(self) -> Path:
        """
        Create folder for today's date.

        Returns:
            Path to today's folder
        """
        today = datetime.now().strftime("%Y-%m-%d")
        folder = self.base_path / today
        folder.mkdir(parents=True, exist_ok=True)
        return folder

    def _generate_filename(self, event) -> str:
        """
        Generate filename from event.

        Args:
            event: PhoneUsageEvent object

        Returns:
            Filename string (without extension)
        """
        # Get HHmmss from event start_time
        time_str = event.start_time.strftime("%H%M%S")
        # Get short event ID (last 8 chars)
        event_id_short = event.event_id[-8:]
        return f"{time_str}_event_{event_id_short}"

    def _save_metadata(self, filepath: Path, event, detections: Dict):
        """
        Save metadata JSON file.

        Args:
            filepath: Path to save JSON
            event: PhoneUsageEvent object
            detections: Detection dictionary
        """
        metadata = {
            'event_id': event.event_id,
            'timestamp': event.start_time.isoformat(),
            'person_bbox': event.person_bbox,
            'phone_bbox': event.phone_bbox,
            'frame_count': event.frame_count,
            'num_persons': len(detections['persons']),
            'num_phones': len(detections['phones'])
        }

        with open(filepath, 'w') as f:
            json.dump(metadata, f, indent=2)

    def get_screenshots_for_date(self, date: str = None) -> list:
        """
        Get list of screenshots for a specific date.

        Args:
            date: Date string in YYYY-MM-DD format. If None, uses today.

        Returns:
            List of screenshot paths
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        folder = self.base_path / date
        if not folder.exists():
            return []

        # Get all jpg files
        screenshots = sorted(folder.glob("*.jpg"))
        return [str(s) for s in screenshots]

    def get_screenshot_metadata(self, screenshot_path: str) -> dict:
        """
        Get metadata for a screenshot.

        Args:
            screenshot_path: Path to screenshot image

        Returns:
            Dictionary with metadata or None if not found
        """
        json_path = Path(screenshot_path).with_suffix('.json')
        if not json_path.exists():
            return None

        with open(json_path, 'r') as f:
            return json.load(f)
