"""Database manager for event tracking and statistics."""

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, date, timedelta
import json
from pathlib import Path

Base = declarative_base()


class Event(Base):
    """Database model for phone usage events."""
    __tablename__ = 'events'

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_uuid = Column(String, unique=True, nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    screenshot_path = Column(String)
    person_bbox = Column(Text)  # Store as JSON string
    phone_bbox = Column(Text)   # Store as JSON string
    frame_count = Column(Integer)

    def to_dict(self):
        """Convert event to dictionary."""
        return {
            'id': self.id,
            'event_uuid': self.event_uuid,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'screenshot_path': self.screenshot_path,
            'person_bbox': json.loads(self.person_bbox) if self.person_bbox else None,
            'phone_bbox': json.loads(self.phone_bbox) if self.phone_bbox else None,
            'frame_count': self.frame_count
        }


class DatabaseManager:
    """Manages database operations for event tracking."""

    def __init__(self, db_path: str):
        """
        Initialize database connection.

        Args:
            db_path: Path to SQLite database file
        """
        # Ensure directory exists
        db_file = Path(db_path)
        db_file.parent.mkdir(parents=True, exist_ok=True)

        # Create engine
        self.engine = create_engine(f'sqlite:///{db_path}', echo=False)

        # Create tables
        Base.metadata.create_all(self.engine)

        # Create session factory
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def add_event(self, event, screenshot_path: str):
        """
        Add new event to database.

        Args:
            event: PhoneUsageEvent object
            screenshot_path: Path to screenshot
        """
        try:
            db_event = Event(
                event_uuid=event.event_id,
                timestamp=event.start_time,
                screenshot_path=screenshot_path,
                person_bbox=json.dumps(event.person_bbox),
                phone_bbox=json.dumps(event.phone_bbox),
                frame_count=event.frame_count
            )

            self.session.add(db_event)
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            print(f"Error adding event to database: {e}")
            return False

    def get_today_events(self) -> list:
        """
        Get all events from today.

        Returns:
            List of Event objects
        """
        today = date.today()
        events = self.session.query(Event).filter(
            func.date(Event.timestamp) == today
        ).order_by(Event.timestamp.desc()).all()
        return events

    def get_total_events(self) -> int:
        """
        Get total number of events.

        Returns:
            Total event count
        """
        return self.session.query(Event).count()

    def get_recent_events(self, limit: int = 10) -> list:
        """
        Get most recent events.

        Args:
            limit: Maximum number of events to return

        Returns:
            List of Event objects
        """
        events = self.session.query(Event).order_by(
            Event.timestamp.desc()
        ).limit(limit).all()
        return events

    def get_events_by_date(self, target_date: date) -> list:
        """
        Get all events for a specific date.

        Args:
            target_date: Date to query

        Returns:
            List of Event objects
        """
        events = self.session.query(Event).filter(
            func.date(Event.timestamp) == target_date
        ).order_by(Event.timestamp.desc()).all()
        return events

    def get_events_date_range(self, start_date: date, end_date: date) -> list:
        """
        Get events within a date range.

        Args:
            start_date: Start date (inclusive)
            end_date: End date (inclusive)

        Returns:
            List of Event objects
        """
        events = self.session.query(Event).filter(
            Event.timestamp >= datetime.combine(start_date, datetime.min.time()),
            Event.timestamp <= datetime.combine(end_date, datetime.max.time())
        ).order_by(Event.timestamp.desc()).all()
        return events

    def get_daily_statistics(self, days: int = 7) -> dict:
        """
        Get daily event counts for the last N days.

        Args:
            days: Number of days to include

        Returns:
            Dictionary with date -> count mapping
        """
        end_date = date.today()
        start_date = end_date - timedelta(days=days-1)

        # Query events grouped by date
        results = self.session.query(
            func.date(Event.timestamp).label('date'),
            func.count(Event.id).label('count')
        ).filter(
            Event.timestamp >= datetime.combine(start_date, datetime.min.time())
        ).group_by(
            func.date(Event.timestamp)
        ).all()

        # Create dictionary with all dates (including zeros)
        stats = {}
        current_date = start_date
        while current_date <= end_date:
            stats[current_date.isoformat()] = 0
            current_date += timedelta(days=1)

        # Fill in actual counts
        for result in results:
            date_str = result.date if isinstance(result.date, str) else result.date.isoformat()
            stats[date_str] = result.count

        return stats

    def get_hourly_statistics(self, target_date: date = None) -> dict:
        """
        Get hourly event distribution for a specific date.

        Args:
            target_date: Date to analyze. If None, uses today.

        Returns:
            Dictionary with hour (0-23) -> count mapping
        """
        if target_date is None:
            target_date = date.today()

        # Query events grouped by hour
        results = self.session.query(
            func.strftime('%H', Event.timestamp).label('hour'),
            func.count(Event.id).label('count')
        ).filter(
            func.date(Event.timestamp) == target_date
        ).group_by(
            func.strftime('%H', Event.timestamp)
        ).all()

        # Create dictionary with all hours (0-23)
        stats = {f"{h:02d}": 0 for h in range(24)}

        # Fill in actual counts
        for result in results:
            stats[result.hour] = result.count

        return stats

    def get_statistics_summary(self) -> dict:
        """
        Get comprehensive statistics summary.

        Returns:
            Dictionary with various statistics
        """
        today = date.today()
        yesterday = today - timedelta(days=1)
        week_ago = today - timedelta(days=7)

        today_count = len(self.get_events_by_date(today))
        yesterday_count = len(self.get_events_by_date(yesterday))
        week_count = len(self.get_events_date_range(week_ago, today))
        total_count = self.get_total_events()

        # Get first and last event
        first_event = self.session.query(Event).order_by(Event.timestamp.asc()).first()
        last_event = self.session.query(Event).order_by(Event.timestamp.desc()).first()

        return {
            'total_events': total_count,
            'today_events': today_count,
            'yesterday_events': yesterday_count,
            'week_events': week_count,
            'first_event': first_event.timestamp.isoformat() if first_event else None,
            'last_event': last_event.timestamp.isoformat() if last_event else None,
            'tracking_days': (today - first_event.timestamp.date()).days + 1 if first_event else 0
        }

    def clear_old_events(self, days_to_keep: int = 30):
        """
        Delete events older than specified days.

        Args:
            days_to_keep: Number of days to keep

        Returns:
            Number of deleted events
        """
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        deleted = self.session.query(Event).filter(
            Event.timestamp < cutoff_date
        ).delete()
        self.session.commit()
        return deleted

    def clear_all_events(self):
        """Delete all events from database."""
        deleted = self.session.query(Event).delete()
        self.session.commit()
        return deleted

    def close(self):
        """Close database connection."""
        self.session.close()
