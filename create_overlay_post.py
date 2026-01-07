"""Create social media posts with stats overlaid on actual screenshots."""

import sys
from pathlib import Path
from datetime import datetime, date
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from storage.database import DatabaseManager, Event
from utils.config import Config


class OverlayPostGenerator:
    """Generate posts with stats overlaid on actual detection screenshots."""

    # Fun overlay messages
    MESSAGES = {
        'caught': [
            "🚨 CAUGHT RED-HANDED! 🚨",
            "BUSTED! 📱",
            "PHONE ADDICT DETECTED! 🔴",
            "YOU'VE BEEN EXPOSED! 📸",
            "SHAME! SHAME! 🔔"
        ],
        'stats': [
            "Time #{count} today!",
            "#{count} of the day!",
            "Offense #{count} today",
            "Strike #{count}!"
        ]
    }

    def __init__(self, output_dir: str = "data/posts"):
        """Initialize post generator."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Load config and database
        self.config = Config.load()
        self.db = DatabaseManager(self.config.storage.database_path)

    def create_overlay_post(self, screenshot_path: str = None, event_uuid: str = None) -> str:
        """
        Create post with stats overlaid on screenshot.

        Args:
            screenshot_path: Path to screenshot. If None, uses most recent.
            event_uuid: Specific event UUID. If None, uses most recent.

        Returns:
            Path to generated image
        """
        # Get event from database
        if event_uuid:
            event = self.db.session.query(Event).filter_by(event_uuid=event_uuid).first()
            if not event:
                print(f"Event {event_uuid} not found")
                return None
            screenshot_path = event.screenshot_path
        elif not screenshot_path:
            # Get most recent event
            events = self.db.get_recent_events(limit=1)
            if not events:
                print("No events found")
                return None
            event = events[0]
            screenshot_path = event.screenshot_path
        else:
            # Load event by screenshot path
            event = self.db.session.query(Event).filter_by(screenshot_path=screenshot_path).first()

        # Load screenshot
        img_path = Path(screenshot_path)
        if not img_path.exists():
            print(f"Screenshot not found: {img_path}")
            return None

        img = Image.open(img_path)

        # Get today's event count for this event
        event_date = event.timestamp.date()
        events_today = self.db.get_events_by_date(event_date)
        event_number = len([e for e in events_today if e.timestamp <= event.timestamp])
        total_today = len(events_today)

        # Convert to RGB if needed
        if img.mode != 'RGB':
            img = img.convert('RGB')

        # Create drawing context
        draw = ImageDraw.Draw(img)
        width, height = img.size

        # Load fonts
        try:
            huge_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", int(height * 0.08))
            big_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", int(height * 0.06))
            medium_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", int(height * 0.04))
            small_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", int(height * 0.03))
        except:
            huge_font = ImageFont.load_default()
            big_font = ImageFont.load_default()
            medium_font = ImageFont.load_default()
            small_font = ImageFont.load_default()

        # === TOP OVERLAY ===
        # Create semi-transparent red banner at top
        top_overlay = Image.new('RGBA', (width, int(height * 0.15)), (231, 76, 60, 220))
        img.paste(top_overlay, (0, 0), top_overlay)

        # Main "CAUGHT" message
        caught_msg = random.choice(self.MESSAGES['caught'])
        bbox = draw.textbbox((0, 0), caught_msg, font=huge_font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        draw.text(((width - text_width) // 2, int(height * 0.02)), caught_msg,
                 fill=(255, 255, 255), font=huge_font, stroke_width=3, stroke_fill=(0, 0, 0))

        # Event number
        stats_msg = random.choice(self.MESSAGES['stats']).format(count=event_number)
        bbox = draw.textbbox((0, 0), stats_msg, font=medium_font)
        text_width = bbox[2] - bbox[0]
        draw.text(((width - text_width) // 2, int(height * 0.10)), stats_msg,
                 fill=(255, 255, 255), font=medium_font, stroke_width=2, stroke_fill=(0, 0, 0))

        # === BOTTOM OVERLAY ===
        # Create semi-transparent black banner at bottom
        bottom_height = int(height * 0.20)
        bottom_overlay = Image.new('RGBA', (width, bottom_height), (0, 0, 0, 200))
        img.paste(bottom_overlay, (0, height - bottom_height), bottom_overlay)

        y_pos = height - bottom_height + 10

        # Timestamp
        timestamp = event.timestamp.strftime("%B %d, %Y at %I:%M %p")
        time_text = f"📅 {timestamp}"
        draw.text((20, y_pos), time_text, fill=(255, 255, 255), font=medium_font)
        y_pos += int(height * 0.05)

        # Daily stats
        daily_text = f"📊 Today's Total: {total_today} times"
        draw.text((20, y_pos), daily_text, fill=(255, 255, 255), font=medium_font)
        y_pos += int(height * 0.05)

        # Duration
        duration_text = f"⏱️  Detected for {event.frame_count} frames"
        draw.text((20, y_pos), duration_text, fill=(255, 255, 255), font=small_font)
        y_pos += int(height * 0.04)

        # Watermark
        watermark = "📱 Phone Shamer - Digital Detox Tracker"
        bbox = draw.textbbox((0, 0), watermark, font=small_font)
        text_width = bbox[2] - bbox[0]
        draw.text(((width - text_width) // 2, height - 25), watermark,
                 fill=(178, 190, 195), font=small_font)

        # === SIDE BADGE (if total today > 10) ===
        if total_today >= 10:
            # Draw "ADDICTION ALERT" badge in top right
            badge_text = f"🚨 {total_today}"
            badge_overlay = Image.new('RGBA', (int(width * 0.15), int(width * 0.15)), (231, 76, 60, 240))

            # Draw circle
            badge_draw = ImageDraw.Draw(badge_overlay)
            badge_draw.ellipse([5, 5, badge_overlay.width-5, badge_overlay.height-5],
                              fill=(231, 76, 60, 255), outline=(255, 255, 255), width=4)

            bbox = badge_draw.textbbox((0, 0), badge_text, font=big_font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            badge_draw.text(((badge_overlay.width - text_width) // 2,
                           (badge_overlay.height - text_height) // 2 - 10),
                          badge_text, fill=(255, 255, 255), font=big_font)

            img.paste(badge_overlay, (width - badge_overlay.width - 20, int(height * 0.18)), badge_overlay)

        # === Resize for Instagram (1080x1080 or keep aspect ratio) ===
        # Calculate dimensions to fit in 1080x1080 while maintaining aspect ratio
        max_size = 1080
        img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)

        # Create square canvas with padding if needed
        if img.width != img.height:
            canvas = Image.new('RGB', (max_size, max_size), (0, 0, 0))
            x_offset = (max_size - img.width) // 2
            y_offset = (max_size - img.height) // 2
            canvas.paste(img, (x_offset, y_offset))
            img = canvas

        # Save
        filename = f"shame_overlay_{event.event_uuid[:8]}_{event.timestamp.strftime('%Y%m%d_%H%M%S')}.png"
        output_path = self.output_dir / filename
        img.save(output_path, quality=95)

        print(f"✅ Overlay post created: {output_path}")
        print(f"   Event: #{event_number} of {total_today} today")
        print(f"   Time: {timestamp}")

        return str(output_path)

    def create_latest_post(self) -> str:
        """Create post from latest screenshot."""
        return self.create_overlay_post()

    def create_all_today_posts(self) -> list:
        """Create overlay posts for all events today."""
        today = date.today()
        events = self.db.get_events_by_date(today)

        if not events:
            print(f"No events found for {today}")
            return []

        paths = []
        print(f"\n📸 Creating posts for {len(events)} events from today...")

        for i, event in enumerate(events, 1):
            print(f"\n[{i}/{len(events)}] Processing event {event.event_uuid[:8]}...")
            path = self.create_overlay_post(event_uuid=event.event_uuid)
            if path:
                paths.append(path)

        print(f"\n✅ Created {len(paths)} posts!")
        return paths


def main():
    """CLI interface."""
    import argparse

    parser = argparse.ArgumentParser(description="Create shame posts with overlaid stats")
    parser.add_argument(
        '--mode',
        choices=['latest', 'all-today', 'specific'],
        default='latest',
        help='Which screenshot(s) to process'
    )
    parser.add_argument(
        '--screenshot',
        type=str,
        help='Path to specific screenshot (for specific mode)'
    )
    parser.add_argument(
        '--event-id',
        type=str,
        help='Event UUID (for specific mode)'
    )

    args = parser.parse_args()

    generator = OverlayPostGenerator()

    if args.mode == 'latest':
        print("📸 Creating post from latest screenshot...")
        path = generator.create_latest_post()

    elif args.mode == 'all-today':
        print("📸 Creating posts for all today's events...")
        paths = generator.create_all_today_posts()
        if paths:
            print(f"\n🎉 {len(paths)} posts ready in data/posts/")

    elif args.mode == 'specific':
        if args.screenshot:
            path = generator.create_overlay_post(screenshot_path=args.screenshot)
        elif args.event_id:
            path = generator.create_overlay_post(event_uuid=args.event_id)
        else:
            print("❌ Please provide --screenshot or --event-id")
            return

    print("\n📱 Posts are ready to share on social media!")
    print("💡 Pro tip: The detection boxes make it look more authentic!")


if __name__ == "__main__":
    main()
