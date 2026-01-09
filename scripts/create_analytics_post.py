"""
Create comprehensive analytics posts with graphs and trends.
Think Strava's detailed activity summary with charts.
"""

import sys
from pathlib import Path
from datetime import datetime, date, timedelta
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from storage.database import DatabaseManager
from utils.config import Config


class AnalyticsPostGenerator:
    """Generate detailed analytics posts with graphs."""

    def __init__(self, output_dir: str = "data/posts"):
        """Initialize generator."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        try:
            self.config = Config.load()
            self.db = DatabaseManager(self.config.storage.database_path)
        except:
            self.db = None

    def create_weekly_analytics(self, use_sample_data: bool = False) -> str:
        """
        Create detailed weekly analytics post with graphs.

        Args:
            use_sample_data: If True, generates sample data for demo

        Returns:
            Path to generated image
        """
        if use_sample_data or not self.db:
            data = self._generate_sample_weekly_data()
        else:
            data = self._get_real_weekly_data()

        return self._render_weekly_post(data)

    def create_monthly_analytics(self, use_sample_data: bool = False) -> str:
        """
        Create detailed monthly analytics post with graphs.

        Args:
            use_sample_data: If True, generates sample data for demo

        Returns:
            Path to generated image
        """
        if use_sample_data or not self.db:
            data = self._generate_sample_monthly_data()
        else:
            data = self._get_real_monthly_data()

        return self._render_monthly_post(data)

    def _generate_sample_weekly_data(self) -> dict:
        """Generate sample data for weekly view."""
        today = date.today()
        days = []

        # Generate 7 days of sample data
        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            # Simulate varying usage (worse on weekdays, better on weekends)
            is_weekend = day.weekday() >= 5
            base_count = random.randint(5, 10) if is_weekend else random.randint(15, 25)

            days.append({
                'date': day,
                'count': base_count,
                'minutes': base_count * 0.7,
                'hourly': {f"{h:02d}": random.randint(0, 3) for h in range(24)}
            })

        return {
            'period': 'week',
            'start_date': days[0]['date'],
            'end_date': days[-1]['date'],
            'days': days,
            'total': sum(d['count'] for d in days),
            'avg_daily': sum(d['count'] for d in days) / 7,
            'total_minutes': sum(d['minutes'] for d in days),
            'best_day': min(days, key=lambda x: x['count']),
            'worst_day': max(days, key=lambda x: x['count']),
            'improvement': random.randint(-15, 20)  # % change from last week
        }

    def _generate_sample_monthly_data(self) -> dict:
        """Generate sample data for monthly view."""
        today = date.today()
        weeks = []

        # Generate 4 weeks of sample data
        for week_num in range(4):
            week_start = today - timedelta(days=(3-week_num)*7 + today.weekday())
            week_data = []

            for day_num in range(7):
                day = week_start + timedelta(days=day_num)
                if day <= today:
                    # Simulate gradual improvement over the month
                    base = 25 - (week_num * 3)
                    count = max(5, random.randint(base-5, base+5))
                    week_data.append({'date': day, 'count': count})

            weeks.append({
                'week_num': week_num + 1,
                'start': week_start,
                'days': week_data,
                'total': sum(d['count'] for d in week_data)
            })

        all_days = [day for week in weeks for day in week['days']]

        return {
            'period': 'month',
            'start_date': weeks[0]['start'],
            'end_date': today,
            'weeks': weeks,
            'total': sum(d['count'] for d in all_days),
            'avg_daily': sum(d['count'] for d in all_days) / len(all_days),
            'best_week': min(weeks, key=lambda x: x['total']),
            'worst_week': max(weeks, key=lambda x: x['total']),
            'improvement': random.randint(10, 40),  # % improvement over month
            'streak': random.randint(3, 7)  # Days under goal
        }

    def _render_weekly_post(self, data: dict) -> str:
        """Render weekly analytics post."""
        # Create image (Instagram Story: 1080x1920)
        width, height = 1080, 1920
        img = Image.new('RGB', (width, height), color=(18, 18, 18))
        draw = ImageDraw.Draw(img)

        # Load fonts
        fonts = self._load_fonts()

        y = 60

        # === HEADER ===
        y = self._draw_header(draw, width, y, "WEEKLY REPORT",
                             data['start_date'], data['end_date'], fonts)

        # === KEY METRICS ===
        y = self._draw_key_metrics(draw, width, y, data, fonts)

        # === TREND LINE CHART ===
        y += 30
        y = self._draw_line_chart(draw, width, y, data['days'], fonts)

        # === DAILY BAR CHART ===
        y += 40
        y = self._draw_bar_chart(draw, width, y, data['days'], fonts)

        # === HEATMAP ===
        y += 40
        y = self._draw_heatmap(draw, width, y, data['days'], fonts)

        # === INSIGHTS ===
        y += 40
        y = self._draw_insights(draw, width, y, data, fonts)

        # === FOOTER ===
        self._draw_footer(draw, width, height, fonts)

        # Save
        filename = f"analytics_weekly_{date.today().isoformat()}.jpg"
        output_path = self.output_dir / filename
        img.save(output_path, "JPEG", quality=95)

        print(f"✅ Weekly analytics post created: {output_path}")
        return str(output_path)

    def _render_monthly_post(self, data: dict) -> str:
        """Render monthly analytics post."""
        width, height = 1080, 1920
        img = Image.new('RGB', (width, height), color=(18, 18, 18))
        draw = ImageDraw.Draw(img)

        fonts = self._load_fonts()
        y = 60

        # === HEADER ===
        y = self._draw_header(draw, width, y, "MONTHLY REPORT",
                             data['start_date'], data['end_date'], fonts)

        # === KEY METRICS ===
        metrics_data = {
            'total': data['total'],
            'avg_daily': data['avg_daily'],
            'improvement': data['improvement']
        }
        y = self._draw_monthly_metrics(draw, width, y, metrics_data, fonts)

        # === WEEKLY PROGRESS ===
        y += 30
        y = self._draw_weekly_progress(draw, width, y, data['weeks'], fonts)

        # === CALENDAR HEATMAP ===
        y += 40
        y = self._draw_calendar_heatmap(draw, width, y, data['weeks'], fonts)

        # === PROGRESS INDICATOR ===
        y += 40
        y = self._draw_progress_circle(draw, width, y, data['improvement'], fonts)

        # === STREAK & ACHIEVEMENTS ===
        y += 40
        y = self._draw_achievements(draw, width, y, data, fonts)

        # === FOOTER ===
        self._draw_footer(draw, width, height, fonts)

        filename = f"analytics_monthly_{date.today().isoformat()}.jpg"
        output_path = self.output_dir / filename
        img.save(output_path, "JPEG", quality=95)

        print(f"✅ Monthly analytics post created: {output_path}")
        return str(output_path)

    def _load_fonts(self):
        """Load fonts with fallback."""
        try:
            return {
                'huge': ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 100),
                'big': ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 60),
                'medium': ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 42),
                'small': ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 32),
                'tiny': ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24),
            }
        except:
            default = ImageFont.load_default()
            return {'huge': default, 'big': default, 'medium': default,
                   'small': default, 'tiny': default}

    def _draw_header(self, draw, width, y, title, start_date, end_date, fonts):
        """Draw header section."""
        # Title
        bbox = draw.textbbox((0, 0), title, font=fonts['big'])
        title_width = bbox[2] - bbox[0]
        draw.text(((width - title_width) // 2, y), title,
                 fill=(255, 255, 255), font=fonts['big'])
        y += 80

        # Date range
        date_range = f"{start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')}"
        bbox = draw.textbbox((0, 0), date_range, font=fonts['tiny'])
        range_width = bbox[2] - bbox[0]
        draw.text(((width - range_width) // 2, y), date_range,
                 fill=(150, 150, 150), font=fonts['tiny'])

        return y + 60

    def _draw_key_metrics(self, draw, width, y, data, fonts):
        """Draw key metrics row."""
        metrics = [
            ("TOTAL", str(data['total']), (52, 152, 219)),
            ("AVG/DAY", f"{data['avg_daily']:.1f}", (46, 213, 115)),
            ("CHANGE", f"{data['improvement']:+d}%",
             (46, 213, 115) if data['improvement'] < 0 else (231, 76, 60))
        ]

        metric_width = 300
        spacing = (width - 3 * metric_width) // 4
        x = spacing

        for label, value, color in metrics:
            # Label
            bbox = draw.textbbox((0, 0), label, font=fonts['tiny'])
            label_w = bbox[2] - bbox[0]
            draw.text((x + (metric_width - label_w) // 2, y), label,
                     fill=(150, 150, 150), font=fonts['tiny'])

            # Value
            bbox = draw.textbbox((0, 0), value, font=fonts['big'])
            value_w = bbox[2] - bbox[0]
            draw.text((x + (metric_width - value_w) // 2, y + 40), value,
                     fill=color, font=fonts['big'])

            x += metric_width + spacing

        return y + 130

    def _draw_monthly_metrics(self, draw, width, y, data, fonts):
        """Draw monthly key metrics."""
        metrics = [
            ("TOTAL CHECKS", str(data['total']), (52, 152, 219)),
            ("DAILY AVG", f"{data['avg_daily']:.1f}", (46, 213, 115)),
            ("IMPROVED", f"{data['improvement']}%", (46, 213, 115))
        ]

        metric_width = 300
        spacing = (width - 3 * metric_width) // 4
        x = spacing

        for label, value, color in metrics:
            bbox = draw.textbbox((0, 0), label, font=fonts['tiny'])
            label_w = bbox[2] - bbox[0]
            draw.text((x + (metric_width - label_w) // 2, y), label,
                     fill=(150, 150, 150), font=fonts['tiny'])

            bbox = draw.textbbox((0, 0), value, font=fonts['big'])
            value_w = bbox[2] - bbox[0]
            draw.text((x + (metric_width - value_w) // 2, y + 40), value,
                     fill=color, font=fonts['big'])

            x += metric_width + spacing

        return y + 130

    def _draw_line_chart(self, draw, width, y, days, fonts):
        """Draw line chart showing trend."""
        chart_height = 200
        chart_width = width - 120
        chart_x = 60

        # Title
        draw.text((chart_x, y), "TREND", fill=(150, 150, 150), font=fonts['small'])
        y += 50

        # Find min/max for scaling
        counts = [d['count'] for d in days]
        min_val = min(counts)
        max_val = max(counts)
        value_range = max_val - min_val if max_val > min_val else 1

        # Draw grid lines
        for i in range(5):
            grid_y = y + (chart_height * i // 4)
            draw.line([(chart_x, grid_y), (chart_x + chart_width, grid_y)],
                     fill=(40, 40, 40), width=1)

        # Draw line
        points = []
        for i, day in enumerate(days):
            x = chart_x + (chart_width * i // (len(days) - 1))
            val = (day['count'] - min_val) / value_range
            point_y = y + chart_height - int(val * chart_height)
            points.append((x, point_y))

            # Draw point
            draw.ellipse([x-5, point_y-5, x+5, point_y+5],
                        fill=(52, 152, 219))

        # Draw connecting lines
        for i in range(len(points) - 1):
            draw.line([points[i], points[i+1]],
                     fill=(52, 152, 219), width=3)

        # Day labels
        for i, day in enumerate(days):
            x = chart_x + (chart_width * i // (len(days) - 1))
            label = day['date'].strftime("%a")[0]  # First letter
            bbox = draw.textbbox((0, 0), label, font=fonts['tiny'])
            label_w = bbox[2] - bbox[0]
            draw.text((x - label_w // 2, y + chart_height + 10), label,
                     fill=(100, 100, 100), font=fonts['tiny'])

        return y + chart_height + 50

    def _draw_bar_chart(self, draw, width, y, days, fonts):
        """Draw bar chart for daily breakdown."""
        chart_height = 180
        chart_width = width - 120
        chart_x = 60

        # Title
        draw.text((chart_x, y), "DAILY BREAKDOWN",
                 fill=(150, 150, 150), font=fonts['small'])
        y += 50

        max_val = max(d['count'] for d in days)
        bar_width = (chart_width - (len(days) - 1) * 10) // len(days)

        for i, day in enumerate(days):
            x = chart_x + i * (bar_width + 10)
            bar_height = int((day['count'] / max_val) * chart_height)

            # Bar
            color = (46, 213, 115) if day['count'] < 15 else (231, 76, 60)
            draw.rectangle([x, y + chart_height - bar_height,
                          x + bar_width, y + chart_height],
                         fill=color)

            # Value on top
            val_text = str(day['count'])
            bbox = draw.textbbox((0, 0), val_text, font=fonts['tiny'])
            val_w = bbox[2] - bbox[0]
            draw.text((x + (bar_width - val_w) // 2,
                      y + chart_height - bar_height - 25),
                     val_text, fill=(200, 200, 200), font=fonts['tiny'])

        return y + chart_height + 20

    def _draw_heatmap(self, draw, width, y, days, fonts):
        """Draw hourly heatmap."""
        chart_x = 60
        chart_width = width - 120

        # Title
        draw.text((chart_x, y), "PEAK HOURS",
                 fill=(150, 150, 150), font=fonts['small'])
        y += 50

        # Aggregate hourly data
        hourly_total = {}
        for day in days:
            for hour, count in day['hourly'].items():
                hourly_total[hour] = hourly_total.get(hour, 0) + count

        # Select peak hours (top 6)
        peak_hours = sorted(hourly_total.items(),
                           key=lambda x: x[1], reverse=True)[:6]
        peak_hours.sort(key=lambda x: x[0])  # Sort by hour

        if not peak_hours:
            return y + 50

        max_count = max(h[1] for h in peak_hours)
        cell_width = chart_width // len(peak_hours)
        cell_height = 60

        for i, (hour, count) in enumerate(peak_hours):
            x = chart_x + i * cell_width
            intensity = count / max_count if max_count > 0 else 0

            # Color based on intensity
            r = int(231 * intensity)
            g = int(76 * intensity)
            b = int(60 * intensity)

            # Cell
            draw.rectangle([x, y, x + cell_width - 5, y + cell_height],
                         fill=(r, g, b))

            # Hour label
            hour_text = f"{hour}h"
            bbox = draw.textbbox((0, 0), hour_text, font=fonts['tiny'])
            text_w = bbox[2] - bbox[0]
            draw.text((x + (cell_width - text_w) // 2, y + 15),
                     hour_text, fill=(255, 255, 255), font=fonts['tiny'])

            # Count
            count_text = str(count)
            bbox = draw.textbbox((0, 0), count_text, font=fonts['small'])
            count_w = bbox[2] - bbox[0]
            draw.text((x + (cell_width - count_w) // 2, y + 35),
                     count_text, fill=(255, 255, 255), font=fonts['small'])

        return y + cell_height + 20

    def _draw_insights(self, draw, width, y, data, fonts):
        """Draw insights section."""
        chart_x = 60

        # Title
        draw.text((chart_x, y), "INSIGHTS",
                 fill=(150, 150, 150), font=fonts['small'])
        y += 50

        # Best/Worst days
        best = data['best_day']
        worst = data['worst_day']

        insights = [
            f"🟢 Best day: {best['date'].strftime('%A')} ({best['count']} checks)",
            f"🔴 Worst day: {worst['date'].strftime('%A')} ({worst['count']} checks)",
            f"📊 Total time: {data['total_minutes']:.1f} minutes",
        ]

        if data['improvement'] < 0:
            insights.append(f"✨ Improved {abs(data['improvement'])}% from last week!")
        else:
            insights.append(f"⚠️  Up {data['improvement']}% from last week")

        for insight in insights:
            draw.text((chart_x, y), insight,
                     fill=(200, 200, 200), font=fonts['tiny'])
            y += 40

        return y + 20

    def _draw_weekly_progress(self, draw, width, y, weeks, fonts):
        """Draw weekly progress bars."""
        chart_x = 60
        chart_width = width - 120

        draw.text((chart_x, y), "WEEKLY PROGRESS",
                 fill=(150, 150, 150), font=fonts['small'])
        y += 50

        max_total = max(w['total'] for w in weeks)
        bar_height = 50
        bar_spacing = 20

        for week in weeks:
            # Week label
            label = f"Week {week['week_num']}"
            draw.text((chart_x, y + 15), label,
                     fill=(200, 200, 200), font=fonts['tiny'])

            # Bar
            bar_width_val = int((week['total'] / max_total) * (chart_width - 150))
            draw.rectangle([chart_x + 120, y,
                          chart_x + 120 + bar_width_val, y + bar_height],
                         fill=(52, 152, 219))

            # Value
            draw.text((chart_x + 120 + bar_width_val + 15, y + 15),
                     str(week['total']), fill=(255, 255, 255), font=fonts['tiny'])

            y += bar_height + bar_spacing

        return y + 20

    def _draw_calendar_heatmap(self, draw, width, y, weeks, fonts):
        """Draw calendar-style heatmap."""
        chart_x = 60

        draw.text((chart_x, y), "CALENDAR VIEW",
                 fill=(150, 150, 150), font=fonts['small'])
        y += 50

        # Get all counts for color scaling
        all_counts = [d['count'] for week in weeks for d in week['days']]
        max_count = max(all_counts) if all_counts else 1

        cell_size = 50
        cell_spacing = 8

        # Day labels
        days_labels = ['M', 'T', 'W', 'T', 'F', 'S', 'S']
        for i, label in enumerate(days_labels):
            draw.text((chart_x + i * (cell_size + cell_spacing), y),
                     label, fill=(100, 100, 100), font=fonts['tiny'])

        y += 30

        for week_idx, week in enumerate(weeks):
            for day_idx, day in enumerate(week['days']):
                x = chart_x + day_idx * (cell_size + cell_spacing)
                y_pos = y + week_idx * (cell_size + cell_spacing)

                # Color intensity
                intensity = day['count'] / max_count
                r = int(52 + (231 - 52) * intensity)
                g = int(152 + (76 - 152) * intensity)
                b = int(219 + (60 - 219) * intensity)

                draw.rectangle([x, y_pos, x + cell_size, y_pos + cell_size],
                             fill=(r, g, b))

        return y + len(weeks) * (cell_size + cell_spacing) + 20

    def _draw_progress_circle(self, draw, width, y, improvement, fonts):
        """Draw circular progress indicator."""
        center_x = width // 2
        radius = 100

        draw.text((center_x - 100, y), "IMPROVEMENT",
                 fill=(150, 150, 150), font=fonts['small'])
        y += 50

        # Background circle
        draw.ellipse([center_x - radius, y, center_x + radius, y + radius * 2],
                    outline=(50, 50, 50), width=15)

        # Progress arc (if improved)
        if improvement > 0:
            # Draw arc (simplified as ellipse for now)
            color = (46, 213, 115)
            draw.arc([center_x - radius, y, center_x + radius, y + radius * 2],
                    start=270, end=270 + int(360 * min(improvement / 100, 1)),
                    fill=color, width=15)

        # Percentage in center
        pct_text = f"{improvement}%"
        bbox = draw.textbbox((0, 0), pct_text, font=fonts['huge'])
        text_w = bbox[2] - bbox[0]
        draw.text((center_x - text_w // 2, y + radius - 40),
                 pct_text, fill=(255, 255, 255), font=fonts['huge'])

        return y + radius * 2 + 30

    def _draw_achievements(self, draw, width, y, data, fonts):
        """Draw achievements/streak section."""
        chart_x = 60

        draw.text((chart_x, y), "ACHIEVEMENTS",
                 fill=(150, 150, 150), font=fonts['small'])
        y += 50

        achievements = [
            f"🔥 {data['streak']} day streak under goal",
            f"✨ {data['improvement']}% improvement this month",
            "🎯 Keep going!"
        ]

        for achievement in achievements:
            draw.text((chart_x, y), achievement,
                     fill=(200, 200, 200), font=fonts['tiny'])
            y += 40

        return y

    def _draw_footer(self, draw, width, height, fonts):
        """Draw footer branding."""
        y = height - 150

        # Logo
        logo = "📱 PHONE SHAMER"
        bbox = draw.textbbox((0, 0), logo, font=fonts['medium'])
        logo_w = bbox[2] - bbox[0]
        draw.text(((width - logo_w) // 2, y), logo,
                 fill=(255, 255, 255), font=fonts['medium'])

        # Tagline
        tagline = "Digital Detox Analytics"
        bbox = draw.textbbox((0, 0), tagline, font=fonts['tiny'])
        tag_w = bbox[2] - bbox[0]
        draw.text(((width - tag_w) // 2, y + 60), tagline,
                 fill=(100, 100, 100), font=fonts['tiny'])


def main():
    """CLI interface."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Create detailed analytics posts with graphs"
    )
    parser.add_argument(
        '--period',
        choices=['week', 'month'],
        default='week',
        help='Time period for analytics'
    )
    parser.add_argument(
        '--sample-data',
        action='store_true',
        help='Use sample data for demo'
    )

    args = parser.parse_args()

    generator = AnalyticsPostGenerator()

    print(f"\n📊 Creating {args.period}ly analytics post...")

    if args.period == 'week':
        path = generator.create_weekly_analytics(use_sample_data=args.sample_data)
    else:
        path = generator.create_monthly_analytics(use_sample_data=args.sample_data)

    if path:
        print(f"\n🎉 Analytics post ready: {path}")
        print("📱 Instagram Story format (1080x1920)")
        print("📊 Includes:")
        if args.period == 'week':
            print("   - Trend line chart")
            print("   - Daily bar chart")
            print("   - Hourly heatmap")
            print("   - Key insights")
        else:
            print("   - Weekly progress bars")
            print("   - Calendar heatmap")
            print("   - Progress circle")
            print("   - Achievements")


if __name__ == "__main__":
    main()
