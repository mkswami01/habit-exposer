"""
Create Strava-style professional social media posts.
Clean, minimal, athletic aesthetic.
"""

import sys
from pathlib import Path
from datetime import datetime, date, timedelta
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import random

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from storage.database import DatabaseManager, Event
from utils.config import Config


class ProPostGenerator:
    """Generate Strava-style professional posts."""

    def __init__(self, output_dir: str = "data/posts"):
        """Initialize generator."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Load config and database
        self.config = Config.load()
        self.db = DatabaseManager(self.config.storage.database_path)

    def create_professional_post(self, target_date: date = None, use_screenshot: bool = False) -> str:
        """
        Create Strava-style professional post.

        Args:
            target_date: Date to create post for. If None, uses today.
            use_screenshot: If True, uses actual screenshot as background

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

        # Get hourly stats
        hourly_stats = self.db.get_hourly_statistics(target_date)

        # Calculate metrics
        total_frames = sum(e.frame_count for e in events)
        avg_frames = total_frames / event_count if event_count > 0 else 0

        # Estimate time (assuming ~30 FPS and frame_skip=2)
        estimated_seconds = (total_frames * 2) / 30  # frames * skip / fps
        estimated_minutes = estimated_seconds / 60

        # Find peak hour
        peak_hour = max(hourly_stats.items(), key=lambda x: x[1])[0] if hourly_stats else "N/A"

        # === CREATE IMAGE ===
        width, height = 1080, 1920  # Instagram Story size (9:16)

        # Background
        if use_screenshot and events:
            # Use actual screenshot as background
            screenshot_path = Path(events[0].screenshot_path)
            if screenshot_path.exists():
                bg = Image.open(screenshot_path)
                bg = bg.convert('RGB')

                # Resize to fill
                bg_ratio = bg.width / bg.height
                target_ratio = width / height

                if bg_ratio > target_ratio:
                    new_height = height
                    new_width = int(height * bg_ratio)
                else:
                    new_width = width
                    new_height = int(width / bg_ratio)

                bg = bg.resize((new_width, new_height), Image.Resampling.LANCZOS)

                # Center crop
                left = (new_width - width) // 2
                top = (new_height - height) // 2
                bg = bg.crop((left, top, left + width, top + height))
            else:
                # Fallback gradient
                bg = self._create_gradient_background(width, height)
        else:
            # Create gradient background
            bg = self._create_gradient_background(width, height)

        # Heavy blur for professional look
        bg = bg.filter(ImageFilter.GaussianBlur(radius=40))

        # Darken background
        enhancer = ImageEnhance.Brightness(bg)
        bg = enhancer.enhance(0.4)  # Darker

        # Create drawing context
        draw = ImageDraw.Draw(bg)

        # Load fonts
        try:
            huge_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 140)
            big_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 80)
            medium_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 50)
            small_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 38)
            tiny_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 30)
        except:
            huge_font = ImageFont.load_default()
            big_font = ImageFont.load_default()
            medium_font = ImageFont.load_default()
            small_font = ImageFont.load_default()
            tiny_font = ImageFont.load_default()

        # === DATE HEADER (top) ===
        date_str = target_date.strftime("%B %d, %Y").upper()
        bbox = draw.textbbox((0, 0), date_str, font=tiny_font)
        date_width = bbox[2] - bbox[0]
        draw.text(((width - date_width) // 2, 100), date_str,
                 fill=(200, 200, 200), font=tiny_font)

        # === MAIN METRICS (center) ===
        metrics_y_start = 400

        # Metric 1: Phone Checks
        self._draw_metric(
            draw, width, metrics_y_start,
            "PHONE CHECKS", str(event_count),
            small_font, huge_font
        )

        # Metric 2: Estimated Time
        self._draw_metric(
            draw, width, metrics_y_start + 280,
            "TIME WASTED", f"{estimated_minutes:.1f} min",
            small_font, big_font
        )

        # Metric 3: Peak Hour
        self._draw_metric(
            draw, width, metrics_y_start + 520,
            "PEAK HOUR", f"{peak_hour}:00",
            small_font, big_font
        )

        # === SEPARATOR LINE ===
        line_y = metrics_y_start + 750
        draw.line([(width // 2 - 100, line_y), (width // 2 + 100, line_y)],
                 fill=(255, 255, 255, 128), width=2)

        # === ADDITIONAL STATS (bottom section) ===
        stats_y = line_y + 60

        # Average frames per detection
        avg_text = f"Avg. duration: {avg_frames:.1f} frames"
        bbox = draw.textbbox((0, 0), avg_text, font=tiny_font)
        avg_width = bbox[2] - bbox[0]
        draw.text(((width - avg_width) // 2, stats_y), avg_text,
                 fill=(180, 180, 180), font=tiny_font)

        # Longest session
        longest_event = max(events, key=lambda e: e.frame_count) if events else None
        if longest_event:
            longest_time = longest_event.timestamp.strftime("%I:%M %p")
            longest_text = f"Longest session: {longest_event.frame_count} frames at {longest_time}"
            bbox = draw.textbbox((0, 0), longest_text, font=tiny_font)
            longest_width = bbox[2] - bbox[0]
            draw.text(((width - longest_width) // 2, stats_y + 50), longest_text,
                     fill=(180, 180, 180), font=tiny_font)

        # === BRANDING (bottom) ===
        logo_y = height - 250

        # Phone emoji logo
        logo_text = "📱"
        bbox = draw.textbbox((0, 0), logo_text, font=big_font)
        logo_width = bbox[2] - bbox[0]
        draw.text(((width - logo_width) // 2, logo_y), logo_text, font=big_font)

        # App name
        app_name = "PHONE SHAMER"
        bbox = draw.textbbox((0, 0), app_name, font=medium_font)
        name_width = bbox[2] - bbox[0]
        draw.text(((width - name_width) // 2, logo_y + 80), app_name,
                 fill=(255, 255, 255), font=medium_font)

        # Tagline
        tagline = "Digital Detox Tracker"
        bbox = draw.textbbox((0, 0), tagline, font=tiny_font)
        tagline_width = bbox[2] - bbox[0]
        draw.text(((width - tagline_width) // 2, logo_y + 150), tagline,
                 fill=(150, 150, 150), font=tiny_font)

        # === MOTIVATIONAL MESSAGE ===
        if event_count <= 5:
            message = "Great restraint! 💪"
            color = (46, 213, 115)  # Green
        elif event_count <= 15:
            message = "Room for improvement 📊"
            color = (255, 165, 0)  # Orange
        else:
            message = "Time to disconnect! 🚨"
            color = (231, 76, 60)  # Red

        bbox = draw.textbbox((0, 0), message, font=small_font)
        msg_width = bbox[2] - bbox[0]
        draw.text(((width - msg_width) // 2, 300), message,
                 fill=color, font=small_font)

        # === Save ===
        filename = f"pro_post_{target_date.isoformat()}.jpg"
        output_path = self.output_dir / filename
        bg.save(output_path, "JPEG", quality=95)

        print(f"✅ Professional post created: {output_path}")
        print(f"   Phone checks: {event_count}")
        print(f"   Estimated time: {estimated_minutes:.1f} minutes")
        print(f"   Peak hour: {peak_hour}:00")

        return str(output_path)

    def _create_gradient_background(self, width: int, height: int) -> Image:
        """Create gradient background."""
        # Create gradient from dark blue to dark purple
        img = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(img)

        # Gradient colors
        color1 = (30, 39, 46)    # Dark grey-blue
        color2 = (72, 52, 212)   # Purple

        for y in range(height):
            # Interpolate colors
            ratio = y / height
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)

            draw.line([(0, y), (width, y)], fill=(r, g, b))

        return img

    def _draw_metric(self, draw, width, y_pos, label, value, label_font, value_font):
        """Draw a metric with label above."""
        # Label
        bbox = draw.textbbox((0, 0), label, font=label_font)
        label_width = bbox[2] - bbox[0]
        draw.text(((width - label_width) // 2, y_pos), label,
                 fill=(180, 180, 180), font=label_font)

        # Value
        bbox = draw.textbbox((0, 0), value, font=value_font)
        value_width = bbox[2] - bbox[0]
        draw.text(((width - value_width) // 2, y_pos + 60), value,
                 fill=(255, 255, 255), font=value_font)

    def create_weekly_pro_post(self) -> str:
        """Create professional weekly summary post."""
        today = date.today()

        # Get weekly stats
        daily_stats = self.db.get_daily_statistics(days=7)
        total_week = sum(daily_stats.values())

        if total_week == 0:
            print("No events this week")
            return None

        # Calculate metrics
        avg_daily = total_week / 7

        # Find best and worst days
        dates_sorted = sorted(daily_stats.items(), key=lambda x: x[1])
        best_day = dates_sorted[0] if dates_sorted[0][1] > 0 else None
        worst_day = dates_sorted[-1] if dates_sorted[-1][1] > 0 else None

        # === CREATE IMAGE ===
        width, height = 1080, 1920
        bg = self._create_gradient_background(width, height)

        # Blur
        bg = bg.filter(ImageFilter.GaussianBlur(radius=30))

        draw = ImageDraw.Draw(bg)

        # Load fonts
        try:
            huge_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 160)
            big_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 80)
            medium_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 50)
            small_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 38)
            tiny_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 30)
        except:
            huge_font = ImageFont.load_default()
            big_font = ImageFont.load_default()
            medium_font = ImageFont.load_default()
            small_font = ImageFont.load_default()
            tiny_font = ImageFont.load_default()

        # === HEADER ===
        header = "WEEKLY SUMMARY"
        bbox = draw.textbbox((0, 0), header, font=medium_font)
        header_width = bbox[2] - bbox[0]
        draw.text(((width - header_width) // 2, 100), header,
                 fill=(200, 200, 200), font=medium_font)

        # Date range
        end_date = today
        start_date = today - timedelta(days=6)
        date_range = f"{start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')}"
        bbox = draw.textbbox((0, 0), date_range, font=tiny_font)
        range_width = bbox[2] - bbox[0]
        draw.text(((width - range_width) // 2, 180), date_range,
                 fill=(150, 150, 150), font=tiny_font)

        # === METRICS ===
        metrics_y = 350

        # Total checks
        self._draw_metric(draw, width, metrics_y,
                         "TOTAL CHECKS", str(total_week),
                         small_font, huge_font)

        # Daily average
        self._draw_metric(draw, width, metrics_y + 280,
                         "DAILY AVERAGE", f"{avg_daily:.1f}",
                         small_font, big_font)

        # === BEST/WORST DAYS ===
        comparison_y = metrics_y + 550

        if best_day:
            best_date = datetime.fromisoformat(best_day[0]).strftime("%a")
            best_text = f"Best: {best_date} ({best_day[1]} checks)"
            bbox = draw.textbbox((0, 0), best_text, font=small_font)
            best_width = bbox[2] - bbox[0]
            draw.text(((width - best_width) // 2, comparison_y), best_text,
                     fill=(46, 213, 115), font=small_font)

        if worst_day:
            worst_date = datetime.fromisoformat(worst_day[0]).strftime("%a")
            worst_text = f"Worst: {worst_date} ({worst_day[1]} checks)"
            bbox = draw.textbbox((0, 0), worst_text, font=small_font)
            worst_width = bbox[2] - bbox[0]
            draw.text(((width - worst_width) // 2, comparison_y + 70), worst_text,
                     fill=(231, 76, 60), font=small_font)

        # === PROGRESS BAR ===
        bar_y = comparison_y + 200
        bar_width_total = 600
        bar_height = 40
        bar_x = (width - bar_width_total) // 2

        # Background bar
        draw.rectangle([bar_x, bar_y, bar_x + bar_width_total, bar_y + bar_height],
                      fill=(50, 50, 50))

        # Progress (based on improvement from worst to best)
        if worst_day and best_day and worst_day[1] > 0:
            improvement = (worst_day[1] - avg_daily) / worst_day[1]
            progress = max(0, min(1, improvement))
            progress_width = int(bar_width_total * progress)

            draw.rectangle([bar_x, bar_y, bar_x + progress_width, bar_y + bar_height],
                          fill=(46, 213, 115))

        # === BRANDING ===
        logo_y = height - 250
        logo_text = "📱"
        bbox = draw.textbbox((0, 0), logo_text, font=big_font)
        logo_width = bbox[2] - bbox[0]
        draw.text(((width - logo_width) // 2, logo_y), logo_text, font=big_font)

        app_name = "PHONE SHAMER"
        bbox = draw.textbbox((0, 0), app_name, font=medium_font)
        name_width = bbox[2] - bbox[0]
        draw.text(((width - name_width) // 2, logo_y + 80), app_name,
                 fill=(255, 255, 255), font=medium_font)

        # === Save ===
        filename = f"pro_weekly_{today.isoformat()}.jpg"
        output_path = self.output_dir / filename
        bg.save(output_path, "JPEG", quality=95)

        print(f"✅ Professional weekly post created: {output_path}")
        print(f"   Total checks: {total_week}")
        print(f"   Daily average: {avg_daily:.1f}")

        return str(output_path)


def main():
    """CLI interface."""
    import argparse

    parser = argparse.ArgumentParser(description="Create Strava-style professional posts")
    parser.add_argument(
        '--type',
        choices=['daily', 'weekly'],
        default='daily',
        help='Type of post'
    )
    parser.add_argument(
        '--date',
        type=str,
        help='Date for daily post (YYYY-MM-DD)'
    )
    parser.add_argument(
        '--use-screenshot',
        action='store_true',
        help='Use actual screenshot as background (daily only)'
    )

    args = parser.parse_args()

    generator = ProPostGenerator()

    if args.type == 'daily':
        target_date = date.fromisoformat(args.date) if args.date else date.today()
        path = generator.create_professional_post(target_date, use_screenshot=args.use_screenshot)
    else:
        path = generator.create_weekly_pro_post()

    if path:
        print(f"\n🎉 Professional post ready: {path}")
        print("📱 Instagram Story format (1080x1920)")
        print("✨ Strava-style professional design")


if __name__ == "__main__":
    main()
