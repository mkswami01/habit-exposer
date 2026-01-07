"""Create a test professional Strava-style post."""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path

def create_test_pro_post():
    """Create a test professional post."""

    output_dir = Path("data/posts")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Instagram Story size (9:16)
    width, height = 1080, 1920

    # Create gradient background
    img = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(img)

    # Gradient from dark blue to purple
    color1 = (30, 39, 46)
    color2 = (72, 52, 212)

    for y in range(height):
        ratio = y / height
        r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
        g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
        b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Blur
    img = img.filter(ImageFilter.GaussianBlur(radius=30))
    draw = ImageDraw.Draw(img)

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

    # Date header
    date_str = "JANUARY 6, 2026"
    bbox = draw.textbbox((0, 0), date_str, font=tiny_font)
    date_width = bbox[2] - bbox[0]
    draw.text(((width - date_width) // 2, 100), date_str,
             fill=(200, 200, 200), font=tiny_font)

    # Motivational message
    message = "Room for improvement 📊"
    bbox = draw.textbbox((0, 0), message, font=small_font)
    msg_width = bbox[2] - bbox[0]
    draw.text(((width - msg_width) // 2, 300), message,
             fill=(255, 165, 0), font=small_font)

    # Metric 1: Phone Checks
    y_pos = 400

    label1 = "PHONE CHECKS"
    bbox = draw.textbbox((0, 0), label1, font=small_font)
    label_width = bbox[2] - bbox[0]
    draw.text(((width - label_width) // 2, y_pos), label1,
             fill=(180, 180, 180), font=small_font)

    value1 = "12"
    bbox = draw.textbbox((0, 0), value1, font=huge_font)
    value_width = bbox[2] - bbox[0]
    draw.text(((width - value_width) // 2, y_pos + 60), value1,
             fill=(255, 255, 255), font=huge_font)

    # Metric 2: Time Wasted
    y_pos2 = y_pos + 280

    label2 = "TIME WASTED"
    bbox = draw.textbbox((0, 0), label2, font=small_font)
    label_width = bbox[2] - bbox[0]
    draw.text(((width - label_width) // 2, y_pos2), label2,
             fill=(180, 180, 180), font=small_font)

    value2 = "8.4 min"
    bbox = draw.textbbox((0, 0), value2, font=big_font)
    value_width = bbox[2] - bbox[0]
    draw.text(((width - value_width) // 2, y_pos2 + 60), value2,
             fill=(255, 255, 255), font=big_font)

    # Metric 3: Peak Hour
    y_pos3 = y_pos2 + 280

    label3 = "PEAK HOUR"
    bbox = draw.textbbox((0, 0), label3, font=small_font)
    label_width = bbox[2] - bbox[0]
    draw.text(((width - label_width) // 2, y_pos3), label3,
             fill=(180, 180, 180), font=small_font)

    value3 = "14:00"
    bbox = draw.textbbox((0, 0), value3, font=big_font)
    value_width = bbox[2] - bbox[0]
    draw.text(((width - value_width) // 2, y_pos3 + 60), value3,
             fill=(255, 255, 255), font=big_font)

    # Separator line
    line_y = y_pos3 + 210
    draw.line([(width // 2 - 100, line_y), (width // 2 + 100, line_y)],
             fill=(255, 255, 255, 128), width=2)

    # Additional stats
    stats_y = line_y + 60

    avg_text = "Avg. duration: 4.2 frames"
    bbox = draw.textbbox((0, 0), avg_text, font=tiny_font)
    avg_width = bbox[2] - bbox[0]
    draw.text(((width - avg_width) // 2, stats_y), avg_text,
             fill=(180, 180, 180), font=tiny_font)

    longest_text = "Longest session: 8 frames at 02:47 PM"
    bbox = draw.textbbox((0, 0), longest_text, font=tiny_font)
    longest_width = bbox[2] - bbox[0]
    draw.text(((width - longest_width) // 2, stats_y + 50), longest_text,
             fill=(180, 180, 180), font=tiny_font)

    # Branding
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

    tagline = "Digital Detox Tracker"
    bbox = draw.textbbox((0, 0), tagline, font=tiny_font)
    tagline_width = bbox[2] - bbox[0]
    draw.text(((width - tagline_width) // 2, logo_y + 150), tagline,
             fill=(150, 150, 150), font=tiny_font)

    # Test watermark
    test_mark = "TEST POST - SAMPLE DATA"
    bbox = draw.textbbox((0, 0), test_mark, font=tiny_font)
    test_width = bbox[2] - bbox[0]
    draw.text(((width - test_width) // 2, 200), test_mark,
             fill=(255, 100, 100), font=tiny_font)

    # Save
    output_path = output_dir / "TEST_pro_post.jpg"
    img.save(output_path, "JPEG", quality=95)

    print(f"✅ Test professional post created: {output_path}")
    print(f"📐 Size: 1080x1920 (Instagram Story)")
    print(f"🎨 Strava-style professional design")
    print(f"\n📱 Test it with:")
    print(f"   python3 post_to_instagram.py --image {output_path} --type story")

    return str(output_path)

if __name__ == "__main__":
    create_test_pro_post()
