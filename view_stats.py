"""View statistics from the phone detection database."""

import sys
from pathlib import Path
from datetime import date, timedelta

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from storage.database import DatabaseManager
from utils.config import Config


def print_statistics():
    """Print comprehensive statistics."""
    # Load config and database
    config = Config.load()
    db = DatabaseManager(config.storage.database_path)

    print("=" * 60)
    print("📱 PHONE SHAMER - STATISTICS")
    print("=" * 60)
    print()

    # Get summary stats
    summary = db.get_statistics_summary()

    print("📊 SUMMARY")
    print("-" * 60)
    print(f"Total Events:         {summary['total_events']}")
    print(f"Today's Events:       {summary['today_events']}")
    print(f"Yesterday's Events:   {summary['yesterday_events']}")
    print(f"This Week's Events:   {summary['week_events']}")
    print(f"Days Tracking:        {summary['tracking_days']}")
    if summary['first_event']:
        print(f"First Detection:      {summary['first_event']}")
    if summary['last_event']:
        print(f"Last Detection:       {summary['last_event']}")
    print()

    # Daily stats for last 7 days
    print("📅 DAILY BREAKDOWN (Last 7 Days)")
    print("-" * 60)
    daily_stats = db.get_daily_statistics(days=7)
    for date_str in sorted(daily_stats.keys(), reverse=True):
        count = daily_stats[date_str]
        bar = "█" * count if count > 0 else ""
        print(f"{date_str}:  {count:3d} events  {bar}")
    print()

    # Hourly stats for today
    print("⏰ HOURLY BREAKDOWN (Today)")
    print("-" * 60)
    hourly_stats = db.get_hourly_statistics()

    # Print in 4 columns
    hours = list(hourly_stats.keys())
    for i in range(0, 24, 4):
        row = []
        for j in range(4):
            if i + j < 24:
                hour = hours[i + j]
                count = hourly_stats[hour]
                row.append(f"{hour}:00 ({count:2d})")
        print("  ".join(row))
    print()

    # Recent events
    print("🕐 RECENT EVENTS (Last 10)")
    print("-" * 60)
    recent = db.get_recent_events(limit=10)
    if recent:
        for event in recent:
            timestamp = event.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            print(f"{timestamp} - Event {event.event_uuid[:8]}... - {event.frame_count} frames")
    else:
        print("No events recorded yet.")
    print()

    print("=" * 60)

    # Close database
    db.close()


def main():
    """Entry point."""
    try:
        print_statistics()
    except FileNotFoundError:
        print("❌ Database not found. Run the detection system first to collect data.")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
