"""Configuration loader for Phone Shamer application."""

import yaml
from pathlib import Path
from dataclasses import dataclass
from typing import Optional


@dataclass
class CameraConfig:
    """Camera configuration."""
    device_index: int
    resolution_width: int
    resolution_height: int
    fps_target: int


@dataclass
class DetectionConfig:
    """Detection configuration."""
    model_size: str
    confidence_threshold: float
    device: str
    frame_skip: int


@dataclass
class ProximityConfig:
    """Proximity detection configuration."""
    distance_threshold_pixels: float
    temporal_consistency_frames: int
    cooldown_seconds: int


@dataclass
class ScreenshotConfig:
    """Screenshot configuration."""
    save_enabled: bool
    quality: int
    include_annotations: bool
    retention_days: int


@dataclass
class DashboardConfig:
    """Dashboard configuration."""
    port: int
    refresh_interval_ms: int
    gallery_items_per_page: int


@dataclass
class StorageConfig:
    """Storage configuration."""
    database_path: str
    screenshots_base_path: str


@dataclass
class LoggingConfig:
    """Logging configuration."""
    level: str
    file: str


@dataclass
class Config:
    """Main configuration class."""
    camera: CameraConfig
    detection: DetectionConfig
    proximity: ProximityConfig
    screenshot: ScreenshotConfig
    dashboard: DashboardConfig
    storage: StorageConfig
    logging: LoggingConfig

    @classmethod
    def load(cls, config_path: Optional[str] = None) -> 'Config':
        """
        Load configuration from YAML file.

        Args:
            config_path: Path to config file. If None, uses default location.

        Returns:
            Config object with loaded settings.
        """
        if config_path is None:
            # Default to config/config.yaml relative to project root
            project_root = Path(__file__).parent.parent.parent
            config_path = project_root / "config" / "config.yaml"
        else:
            config_path = Path(config_path)

        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        with open(config_path, 'r') as f:
            data = yaml.safe_load(f)

        return cls(
            camera=CameraConfig(**data['camera']),
            detection=DetectionConfig(**data['detection']),
            proximity=ProximityConfig(**data['proximity']),
            screenshot=ScreenshotConfig(**data['screenshot']),
            dashboard=DashboardConfig(**data['dashboard']),
            storage=StorageConfig(**data['storage']),
            logging=LoggingConfig(**data['logging'])
        )

    def save(self, config_path: Optional[str] = None):
        """
        Save configuration to YAML file.

        Args:
            config_path: Path to save config file. If None, uses default location.
        """
        if config_path is None:
            project_root = Path(__file__).parent.parent.parent
            config_path = project_root / "config" / "config.yaml"
        else:
            config_path = Path(config_path)

        data = {
            'camera': self.camera.__dict__,
            'detection': self.detection.__dict__,
            'proximity': self.proximity.__dict__,
            'screenshot': self.screenshot.__dict__,
            'dashboard': self.dashboard.__dict__,
            'storage': self.storage.__dict__,
            'logging': self.logging.__dict__
        }

        with open(config_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
