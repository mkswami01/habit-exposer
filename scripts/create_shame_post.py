"""Generate fun social media posts from phone detection stats."""

import sys
from pathlib import Path
from datetime import datetime, date
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from storage.database import DatabaseManager
from utils.config import Config


class ShamePostGenerator:
    """Generate shareable social media posts."""

    # Fun captions for different event counts
    CAPTIONS = {
        'low': [
            "Not bad! Only {count} phone checks today 📱",
            "Pretty good! Caught {count} times 👀",
            "{count} phone breaks today - room for improvement! 💪"
        ],
        'medium': [
            "Whoa! {count} times on the phone today! 😅",
            "Phone addiction level: {count}/10 📱🔥",
            "{count} times! Put that phone down! 🙈"
        ],
        'high': [
            "YIKES! {count} phone checks today! 🚨",
            "PHONE ADDICT ALERT! {count} times! 📱💀",
            "{count} times?! You might have a problem... 😬"
        ],
        'extreme': [
            "🚨 EMERGENCY! {count} PHONE CHECKS TODAY! 🚨",
            "This is intervention-level: {count} times! 📱⚠️",
            "New record! {count} phone sessions! Is it glued to your hand? 🤯"
        ]
    }

    def __init__(self, output_dir: str = "data/posts"):
        """Initialize post generator."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Load config and database
        self.config = Config.load()
        self.db = DatabaseManager(self.config.storage.database_path)

    def get_caption(self, count: int) -> str:
        """Get fun caption based on event count."""
        if count <= 3:
            category = 'low'
        elif count <= 10:
            category = 'medium'
        elif count <= 20:
            category = 'high'
        else:
            category = 'extreme'

        caption = random.choice(self.CAPTIONS[category])
        return caption.format(count=count)

    def create_daily_summary_post(self, target_date: date = None) -> str:
        """
        Create a daily summary post with stats.

        Args:
            target_date: Date to create post for. If None, uses today.

        Returns:
            Path to generated image
        """
        if target_date is None:
            target_date = date.today()

        # Get events for the day
        events = self.db.get_events_by_date(target_date)
        event_count = len(events)

        if event_count == 0:
            print(f"No events found for {target_date}")
            return None

        # Get hourly stats for visualization
        hourly_stats = self.db.get_hourly_statistics(target_date)

        # Create image (Instagram square: 1080x1080)
        img = Image.new('RGB', (1080, 1080), color=(45, 52, 54))  # Dark background
        draw = ImageDraw.Draw(img)

        # Try to load fonts (fallback to default if not available)
        try:
            title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 80)
            big_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 120)
            medium_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 50)
            small_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 35)
        except:
            # Fallback to default font
            title_font = ImageFont.load_default()
            big_font = ImageFont.load_default()
            medium_font = ImageFont.load_default()
            small_font = ImageFont.load_default()

        # Title
        title = "📱 PHONE SHAMER 📱"
        title_bbox = draw.textbbox((0, 0), title, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        draw.text(((1080 - title_width) // 2, 80), title, fill=(255, 255, 255), font=title_font)

        # Date
        date_str = target_date.strftime("%B %d, %Y")
        date_bbox = draw.textbbox((0, 0), date_str, font=medium_font)
        date_width = date_bbox[2] - date_bbox[0]
        draw.text(((1080 - date_width) // 2, 190), date_str, fill=(178, 190, 195), font=medium_font)

        # Big number in center
        count_str = str(event_count)
        count_bbox = draw.textbbox((0, 0), count_str, font=big_font)
        count_width = count_bbox[2] - count_bbox[0]

        # Draw circle behind number
        circle_center = (540, 450)
        circle_radius = 200
        draw.ellipse(
            [circle_center[0] - circle_radius, circle_center[1] - circle_radius,
             circle_center[0] + circle_radius, circle_center[1] + circle_radius],
            fill=(231, 76, 60)  # Red circle
        )

        draw.text(((1080 - count_width) // 2, 400), count_str, fill=(255, 255, 255), font=big_font)

        # "times caught" text
        caught_text = "TIMES CAUGHT!"
        caught_bbox = draw.textbbox((0, 0), caught_text, font=medium_font)
        caught_width = caught_bbox[2] - caught_bbox[0]
        draw.text(((1080 - caught_width) // 2, 540), caught_text, fill=(255, 255, 255), font=medium_font)

        # Simple bar chart of hourly activity
        chart_y_start = 700
        chart_height = 150
        bar_width = 35
        bar_spacing = 45
        chart_x_start = 50

        max_events = max(hourly_stats.values()) if hourly_stats else 1

        # Draw only hours with activity
        active_hours = [(hour, count) for hour, count in hourly_stats.items() if count > 0]

        if active_hours:
            draw.text((50, 650), "Peak Hours:", fill=(178, 190, 195), font=small_font)

            for i, (hour, count) in enumerate(active_hours[:10]):  # Show max 10 bars
                if count > 0:
                    bar_height = int((count / max_events) * chart_height)
                    x = chart_x_start + i * bar_spacing

                    # Draw bar
                    draw.rectangle(
                        [x, chart_y_start + chart_height - bar_height,
                         x + bar_width, chart_y_start + chart_height],
                        fill=(52, 152, 219)  # Blue bars
                    )

                    # Draw hour label
                    draw.text((x, chart_y_start + chart_height + 10), hour,
                             fill=(178, 190, 195), font=small_font)

        # Fun caption at bottom
        caption = self.get_caption(event_count)
        caption_bbox = draw.textbbox((0, 0), caption, font=medium_font)
        caption_width = caption_bbox[2] - caption_bbox[0]

        # Wrap caption if too long
        if caption_width > 1000:
            words = caption.split()
            lines = []
            current_line = []

            for word in words:
                current_line.append(word)
                line_text = ' '.join(current_line)
                bbox = draw.textbbox((0, 0), line_text, font=medium_font)
                if bbox[2] - bbox[0] > 1000:
                    current_line.pop()
                    lines.append(' '.join(current_line))
                    current_line = [word]

            if current_line:
                lines.append(' '.join(current_line))

            y = 950
            for line in lines:
                bbox = draw.textbbox((0, 0), line, font=medium_font)
                width = bbox[2] - bbox[0]
                draw.text(((1080 - width) // 2, y), line, fill=(255, 255, 255), font=medium_font)
                y += 55
        else:
            draw.text(((1080 - caption_width) // 2, 980), caption, fill=(255, 255, 255), font=medium_font)

        # Save image
        filename = f"shame_post_{target_date.isoformat()}.png"
        output_path = self.output_dir / filename
        img.save(output_path, quality=95)

        print(f"✅ Social media post created: {output_path}")
        return str(output_path)

    def create_screenshot_post(self, event_id: str = None) -> str:
        """
        Create post with actual screenshot from detection.

        Args:
            event_id: Specific event UUID. If None, uses most recent.

        Returns:
            Path to generated image
        """
        # Get event
        if event_id:
            event = self.db.session.query(Event).filter_by(event_uuid=event_id).first()
        else:
            events = self.db.get_recent_events(limit=1)
            event = events[0] if events else None

        if not event or not event.screenshot_path:
            print("No screenshot available")
            return None

        # Load screenshot
        screenshot_path = Path(event.screenshot_path)
        if not screenshot_path.exists():
            print(f"Screenshot not found: {screenshot_path}")
            return None

        screenshot = Image.open(screenshot_path)

        # Create Instagram square canvas
        canvas = Image.new('RGB', (1080, 1080), color=(0, 0, 0))

        # Resize screenshot to fit (keep aspect ratio)
        screenshot.thumbnail((1080, 800), Image.Resampling.LANCZOS)

        # Paste screenshot on canvas (centered)
        x_offset = (1080 - screenshot.width) // 2
        y_offset = 50
        canvas.paste(screenshot, (x_offset, y_offset))

        # Add text overlay at bottom
        draw = ImageDraw.Draw(canvas)

        try:
            big_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 60)
            small_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 40)
        except:
            big_font = ImageFont.load_default()
            small_font = ImageFont.load_default()

        # Black semi-transparent overlay at bottom
        overlay = Image.new('RGBA', (1080, 200), (0, 0, 0, 200))
        canvas.paste(overlay, (0, 880), overlay)

        # Text
        caught_text = "🚨 CAUGHT! 🚨"
        bbox = draw.textbbox((0, 0), caught_text, font=big_font)
        width = bbox[2] - bbox[0]
        draw.text(((1080 - width) // 2, 900), caught_text, fill=(231, 76, 60), font=big_font)

        timestamp = event.timestamp.strftime("%I:%M %p")
        time_text = f"Busted at {timestamp}"
        bbox = draw.textbbox((0, 0), time_text, font=small_font)
        width = bbox[2] - bbox[0]
        draw.text(((1080 - width) // 2, 990), time_text, fill=(255, 255, 255), font=small_font)

        # Save
        filename = f"caught_{event.event_uuid[:8]}.png"
        output_path = self.output_dir / filename
        canvas.save(output_path, quality=95)

        print(f"✅ Caught post created: {output_path}")
        return str(output_path)

    def create_weekly_report(self) -> str:
        """Create a weekly summary report post."""
        today = date.today()

        # Get daily stats for last 7 days
        daily_stats = self.db.get_daily_statistics(days=7)
        total_week = sum(daily_stats.values())

        if total_week == 0:
            print("No events this week")
            return None

        # Create image
        img = Image.new('RGB', (1080, 1080), color=(30, 39, 46))
        draw = ImageDraw.Draw(img)

        try:
            title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 70)
            big_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 100)
            medium_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 45)
            small_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 35)
        except:
            title_font = ImageFont.load_default()
            big_font = ImageFont.load_default()
            medium_font = ImageFont.load_default()
            small_font = ImageFont.load_default()

        # Title
        title = "📊 WEEKLY SHAME REPORT 📊"
        bbox = draw.textbbox((0, 0), title, font=title_font)
        width = bbox[2] - bbox[0]
        draw.text(((1080 - width) // 2, 60), title, fill=(255, 255, 255), font=title_font)

        # Week total
        total_text = str(total_week)
        bbox = draw.textbbox((0, 0), total_text, font=big_font)
        width = bbox[2] - bbox[0]
        draw.text(((1080 - width) // 2, 200), total_text, fill=(231, 76, 60), font=big_font)

        times_text = "times this week!"
        bbox = draw.textbbox((0, 0), times_text, font=medium_font)
        width = bbox[2] - bbox[0]
        draw.text(((1080 - width) // 2, 320), times_text, fill=(255, 255, 255), font=medium_font)

        # Bar chart
        chart_y = 450
        chart_height = 300
        bar_width = 120
        bar_spacing = 150
        start_x = 60

        max_count = max(daily_stats.values())

        dates_sorted = sorted(daily_stats.keys())

        for i, date_str in enumerate(dates_sorted):
            count = daily_stats[date_str]

            # Draw bar
            if count > 0:
                bar_height = int((count / max_count) * chart_height)
                x = start_x + i * bar_spacing

                draw.rectangle(
                    [x, chart_y + chart_height - bar_height,
                     x + bar_width, chart_y + chart_height],
                    fill=(52, 152, 219)
                )

                # Count on top of bar
                count_text = str(count)
                bbox = draw.textbbox((0, 0), count_text, font=small_font)
                text_width = bbox[2] - bbox[0]
                draw.text((x + (bar_width - text_width) // 2,
                          chart_y + chart_height - bar_height - 40),
                         count_text, fill=(255, 255, 255), font=small_font)

                # Day label
                day = datetime.fromisoformat(date_str).strftime("%a")
                bbox = draw.textbbox((0, 0), day, font=small_font)
                text_width = bbox[2] - bbox[0]
                draw.text((x + (bar_width - text_width) // 2, chart_y + chart_height + 20),
                         day, fill=(178, 190, 195), font=small_font)

        # Bottom message
        avg = total_week / 7
        message = f"Average: {avg:.1f} per day"
        bbox = draw.textbbox((0, 0), message, font=medium_font)
        width = bbox[2] - bbox[0]
        draw.text(((1080 - width) // 2, 900), message, fill=(178, 190, 195), font=medium_font)

        judgment = "Not bad!" if avg < 5 else "Yikes! Time to detox! 📵"
        bbox = draw.textbbox((0, 0), judgment, font=medium_font)
        width = bbox[2] - bbox[0]
        draw.text(((1080 - width) // 2, 980), judgment, fill=(255, 255, 255), font=medium_font)

        # Save
        filename = f"weekly_report_{today.isoformat()}.png"
        output_path = self.output_dir / filename
        img.save(output_path, quality=95)

        print(f"✅ Weekly report created: {output_path}")
        return str(output_path)


def main():
    """CLI interface for post generation."""
    import argparse

    parser = argparse.ArgumentParser(description="Generate fun social media shame posts")
    parser.add_argument(
        '--type',
        choices=['daily', 'weekly', 'screenshot'],
        default='daily',
        help='Type of post to generate'
    )
    parser.add_argument(
        '--date',
        type=str,
        help='Date for daily post (YYYY-MM-DD). Default: today'
    )

    args = parser.parse_args()

    generator = ShamePostGenerator()

    if args.type == 'daily':
        target_date = date.fromisoformat(args.date) if args.date else date.today()
        path = generator.create_daily_summary_post(target_date)
    elif args.type == 'weekly':
        path = generator.create_weekly_report()
    elif args.type == 'screenshot':
        path = generator.create_screenshot_post()

    if path:
        print(f"\n🎉 Post ready to share: {path}")
        print("📱 Perfect for Instagram, Twitter, or Facebook!")


if __name__ == "__main__":
    main()
