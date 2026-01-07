# 📱 Phone Shamer

A real-time phone usage detection system using YOLOv8 computer vision. Detects when people are using their phones and automatically captures screenshots as evidence.

## Features

- 🤖 **YOLOv8 Detection** - Fast and accurate person and phone detection
- 🎯 **Smart Usage Detection** - Bounding box overlap detection with temporal consistency
- 📸 **Automatic Screenshots** - Captures annotated screenshots when phone usage is detected
- 📊 **SQLite Database** - Tracks all events with timestamps and statistics
- 📈 **Statistics Viewer** - View daily/hourly analytics and trends
- 🎨 **Social Media Posts** - Generate fun, shareable "shame posts" for Instagram/Twitter
- 📱 **Instagram Integration** - Post directly to Stories/Feed (with approval safeguards)
- ⚙️ **Configurable** - Easy YAML configuration for all settings
- 🔄 **Real-time Processing** - Live camera feed with detection visualization

## Installation

### Prerequisites
- Python 3.8+
- Webcam
- pip

### Setup

1. **Clone or navigate to the repository:**
```bash
cd /Users/mk/code/phone-shamer
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

This will install:
- YOLOv8 (ultralytics)
- OpenCV
- NumPy
- And other required packages

On first run, YOLOv8 will automatically download the model weights (~6MB for nano model).

## Usage

### Run the detection system:

```bash
python src/main.py
```

The application will:
1. Initialize the camera
2. Load the YOLOv8 model
3. **Auto-detect** display mode (GUI or headless)
4. Start detecting people and phones in real-time
5. Display live feed with detection boxes (if monitor attached)
6. Save screenshots when phone usage is detected for 5 consecutive frames

**🖥️ Auto-Detect Modes:**
- **With monitor:** Shows live camera feed, press `q` to quit
- **Headless (SSH):** Runs without GUI, press `Ctrl+C` to quit
- Same code works in both environments automatically!

### View Statistics:

```bash
python3 view_stats.py
```

This displays:
- Total events and daily breakdown
- Hourly distribution for today
- Recent event history
- Week-over-week trends

### Create Social Media Posts:

Generate fun, shareable "shame posts" for Instagram/Twitter:

**Option 1: Stats Graphics (Charts & Numbers)**

Daily summary with charts:
```bash
python3 create_shame_post.py --type daily
```

Weekly report:
```bash
python3 create_shame_post.py --type weekly
```

**Option 2: Overlay on Actual Screenshots**

Overlay stats directly on detection screenshots (most authentic!):

```bash
# Latest screenshot
python3 create_overlay_post.py --mode latest

# All screenshots from today
python3 create_overlay_post.py --mode all-today

# Specific screenshot
python3 create_overlay_post.py --mode specific --screenshot path/to/image.jpg
```

**Features:**
- 🚨 "CAUGHT RED-HANDED" banner at top
- 📊 Live stats overlay at bottom (date, time, daily total)
- 🎯 Shows actual detection with bounding boxes
- 🔴 Addiction alert badge if 10+ times/day
- 📱 Instagram-ready (1080x1080)

**Option 3: Professional Strava-Style** ⭐ *Most Beautiful!*

Create ultra-professional posts like Strava fitness tracking:

```bash
# Daily professional post
python3 create_pro_post.py --type daily

# Daily with actual screenshot as background
python3 create_pro_post.py --type daily --use-screenshot

# Weekly summary
python3 create_pro_post.py --type weekly
```

**Features:**
- 🎨 Blurred gradient background
- 📊 Big bold metrics (Phone Checks, Time Wasted, Peak Hour)
- ✨ Clean minimal design
- 💪 Motivational messages
- 📱 Instagram Story format (1080x1920)
- 🏃 Strava-level professional aesthetics

**Option 4: Detailed Analytics with Graphs** 📊 *Most Comprehensive!*

Create data-rich posts with multiple charts and trends (like Strava analytics):

```bash
# Weekly analytics (7 days with graphs)
python3 create_analytics_post.py --period week

# Monthly analytics (4 weeks with heatmaps)
python3 create_analytics_post.py --period month

# Use sample data for testing
python3 create_analytics_post.py --period week --sample-data
```

**Weekly includes:**
- 📈 Trend line chart showing 7-day progress
- 📊 Daily bar chart breakdown
- 🔥 Hourly heatmap (peak hours)
- 💡 Key insights (best/worst days)

**Monthly includes:**
- 📊 Weekly progress bars (4 weeks)
- 📅 Calendar heatmap (color-coded days)
- ⭕ Progress circle (improvement %)
- 🏆 Achievements and streak counter

Posts are saved to `data/posts/` as Instagram-ready images!

### Post to Instagram (Optional):

**⚠️ SAFE: Multiple approval steps required - nothing posts without confirmation!**

Post your shame stats directly to Instagram Stories or Feed:

```bash
# Preview only (safe, default)
python3 post_to_instagram.py --image data/posts/your_post.png --type story

# Actually post (requires typing 'YES' then 'POST NOW')
python3 post_to_instagram.py --image data/posts/your_post.png --type story --no-dry-run
```

**Safety features:**
- 🔒 Dry-run mode by default (preview only)
- ✋ Double confirmation required (`YES` + `POST NOW`)
- 🔐 Requires `AUTO_POST_ENABLED=true` in `.env`
- 👁️ Shows preview before posting

See [INSTAGRAM_GUIDE.md](INSTAGRAM_GUIDE.md) for full setup and usage.

### Screenshots Location

Screenshots are automatically organized by date:
```
data/screenshots/
├── 2026-01-06/
│   ├── 143052_event_abc12345.jpg
│   ├── 143052_event_abc12345.json
│   └── ...
└── 2026-01-07/
    └── ...
```

Each screenshot includes:
- Annotated image with detection boxes
- Metadata JSON with event details (bounding boxes, timestamp, etc.)

## Configuration

Edit `config/config.yaml` to customize behavior:

### Key Settings:

**Camera:**
```yaml
camera:
  device_index: 0          # Change if you have multiple cameras
  resolution_width: 1280
  resolution_height: 720
```

**Detection:**
```yaml
detection:
  model_size: "n"          # n=nano (fast), s=small, m=medium, l=large, x=extra-large
  confidence_threshold: 0.5
  device: "cpu"            # Use "cuda" for GPU or "mps" for Apple Silicon
  frame_skip: 2            # Process every Nth frame (higher = faster but less accurate)
```

**Phone Usage Detection:**
```yaml
proximity:
  temporal_consistency_frames: 5  # Frames needed to confirm usage
  cooldown_seconds: 10            # Minimum time between captures
```

**Screenshots:**
```yaml
screenshot:
  save_enabled: true
  quality: 95              # JPEG quality (0-100)
  include_annotations: true
```

## How It Works

1. **Capture** - Reads frames from webcam
2. **Detect** - YOLOv8 detects people (class 0) and cell phones (class 67)
3. **Analyze** - Checks if person's bounding box overlaps with phone's bounding box
4. **Confirm** - Requires detection for 5 consecutive frames to avoid false positives
5. **Capture** - Saves annotated screenshot with metadata
6. **Log** - Records event to SQLite database with timestamp and details
7. **Cooldown** - Waits 10 seconds before detecting another event

## Project Structure

```
phone-shamer/
├── src/
│   ├── core/
│   │   ├── camera_manager.py      # Webcam interface
│   │   ├── detector.py            # YOLOv8 detection
│   │   └── proximity_analyzer.py  # Phone usage detection logic
│   ├── storage/
│   │   ├── screenshot_manager.py  # Screenshot capture and storage
│   │   └── database.py            # SQLite database manager
│   ├── utils/
│   │   ├── config.py              # Configuration loader
│   │   └── logger.py              # Logging utilities
│   └── main.py                    # Main application
├── config/
│   └── config.yaml                # Configuration file
├── data/
│   ├── screenshots/               # Captured screenshots (organized by date)
│   ├── database/                  # SQLite database (events.db)
│   └── models/                    # YOLOv8 model weights (auto-downloaded)
├── view_stats.py                  # Statistics viewer
├── list_cameras.py                # Camera discovery utility
├── requirements.txt
└── README.md
```

## Performance Tips

### CPU is too slow?
- Increase `frame_skip` to 3 or 4 in config
- Reduce resolution to 640x480
- Use YOLOv8n (nano) model

### Getting false positives?
- Increase `temporal_consistency_frames` to 7-10
- Increase `confidence_threshold` to 0.6

### Missing detections?
- Lower `confidence_threshold` to 0.4
- Ensure good lighting
- Reduce `frame_skip` to 1

### Want to use GPU?
- Install CUDA-enabled PyTorch
- Set `device: "cuda"` in config
- For Apple Silicon Macs: Set `device: "mps"`

## Troubleshooting

**Camera not found:**
```
ValueError: Failed to open camera with index 0
```
- Try changing `device_index` to 1, 2, etc. in config
- Check camera permissions
- Ensure no other app is using the camera

**YOLO model download fails:**
- Check internet connection
- Models are downloaded to: `~/.cache/ultralytics/`
- Download manually if needed and place in that directory

**Import errors:**
```
ModuleNotFoundError: No module named 'ultralytics'
```
- Run: `pip install -r requirements.txt`
- Ensure you're using Python 3.8+

## Future Enhancements

- [x] SQLite database for event tracking ✅
- [x] Statistics viewer with analytics ✅
- [x] Social media post generator ✅
- [x] Instagram auto-posting with safety ✅
- [ ] Streamlit dashboard with live graphs
- [ ] Multiple person tracking with IDs
- [ ] Distance-based proximity detection (vs overlap)
- [ ] Email/SMS notifications
- [ ] Privacy mode (face blurring)
- [ ] Twitter/X integration
- [ ] Scheduled posting with cron
- [ ] More post templates and themes

## License

MIT License - Feel free to use and modify!

## Credits

Built with:
- [YOLOv8](https://github.com/ultralytics/ultralytics) by Ultralytics
- [OpenCV](https://opencv.org/)
- Python ❤️
