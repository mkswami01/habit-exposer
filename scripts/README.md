# Utility Scripts

Helper scripts for the Habit Exposer project.

## 📊 Statistics & Viewing

**`view_stats.py`** - View database statistics in terminal
```bash
python3 scripts/view_stats.py
```
Shows summary stats, daily/hourly breakdowns, and recent events.

## 📸 Social Media Post Generation

**`create_shame_post.py`** - Generate basic shame posts
```bash
python3 scripts/create_shame_post.py
```
Creates fun 1080x1080 posts with stats.

**`create_overlay_post.py`** - Generate overlay posts
```bash
python3 scripts/create_overlay_post.py [event_id]
```
Overlays stats on actual screenshots with "CAUGHT!" banner.

**`create_pro_post.py`** - Generate professional Strava-style posts
```bash
python3 scripts/create_pro_post.py
```
Creates polished 1080x1920 Instagram Story format posts.

**`create_analytics_post.py`** - Generate detailed analytics posts
```bash
python3 scripts/create_analytics_post.py [weekly|monthly]
```
Creates comprehensive analytics with charts (weekly or monthly view).

## 📱 Instagram Integration

**`post_to_instagram.py`** - Post images to Instagram
```bash
python3 scripts/post_to_instagram.py [image_path]
```
Posts generated images to Instagram with safety checks.

**⚠️ Safety Features:**
- Dry-run mode by default
- Double confirmation required
- `AUTO_POST_ENABLED` flag in `.env`

## 🎥 Camera Utilities

**`list_cameras.py`** - Detect available cameras
```bash
python3 scripts/list_cameras.py
```
Lists all available camera devices with their indices.

## 📝 Notes

All scripts should be run from the project root directory to ensure proper path resolution.
