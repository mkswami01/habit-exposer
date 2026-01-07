# 🚀 Server Deployment Guide

Complete guide for deploying Phone Shamer to a server (headless or with display).

## 📋 Pre-Transfer Checklist

### 1. Clean Up Local Development Files

```bash
# Remove local cache and session files
rm -rf data/.instagram_session.json
rm -rf __pycache__/
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
rm -f phone_shamer.log
```

### 2. Create Deployment Package

```bash
# From project root
tar -czf phone-shamer.tar.gz \
  src/ \
  config/ \
  requirements.txt \
  README.md \
  list_cameras.py \
  view_stats.py \
  create_*.py \
  post_to_instagram.py \
  .env.example \
  .gitignore

# Or use git (recommended)
git init
git add .
git commit -m "Initial commit"
# Then push to GitHub and clone on server
```

---

## 🖥️ Server Setup

### Step 1: Check Python Version

```bash
python3 --version  # Should be 3.8+
```

If Python 3.8+ not available:
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.9 python3.9-venv python3.9-dev

# CentOS/RHEL
sudo yum install python39 python39-devel
```

### Step 2: Install System Dependencies

**For Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install -y \
  python3-pip \
  python3-venv \
  python3-opencv \
  libopencv-dev \
  libglib2.0-0 \
  libsm6 \
  libxext6 \
  libxrender-dev \
  libgomp1 \
  libgstreamer1.0-0 \
  ffmpeg
```

**For CentOS/RHEL:**
```bash
sudo yum install -y \
  python3-pip \
  python3-devel \
  opencv \
  opencv-devel \
  gcc \
  gcc-c++ \
  make
```

**For old servers (minimal):**
```bash
# Minimum required
sudo apt install -y python3-pip python3-venv libopencv-dev
```

### Step 3: Transfer Files

**Option A: Using SCP**
```bash
# From local machine
scp phone-shamer.tar.gz user@server:/home/user/
ssh user@server
cd /home/user
tar -xzf phone-shamer.tar.gz
cd phone-shamer
```

**Option B: Using Git (Recommended)**
```bash
ssh user@server
git clone https://github.com/yourusername/phone-shamer.git
cd phone-shamer
```

**Option C: Using rsync**
```bash
# From local machine
rsync -avz --exclude='data/' --exclude='*.log' \
  /Users/mk/code/phone-shamer/ \
  user@server:/home/user/phone-shamer/
```

---

## 🐍 Python Environment Setup

### Create Virtual Environment

```bash
# On server
cd /home/user/phone-shamer

# Create venv
python3 -m venv venv

# Activate
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

### Install Dependencies

```bash
# Install from requirements.txt
pip install -r requirements.txt

# If you get errors, install one by one:
pip install ultralytics
pip install opencv-python
pip install pillow
pip install pyyaml
pip install sqlalchemy
pip install python-dotenv

# For Instagram (optional)
pip install "instagrapi<2.0"  # Python 3.9 compatible
```

**For old servers with limited resources:**
```bash
# Install minimal requirements
pip install ultralytics opencv-python-headless pillow pyyaml sqlalchemy
```

---

## ⚙️ Configuration for Headless Server

### 1. Disable Display (No GUI)

Edit `src/main.py` to make display optional:

```python
# Change this section:
# Display frame (optional - for debugging)
if os.getenv('DISPLAY'):  # Only show if display available
    annotated = self.detector.annotate_frame(frame, detections)
    cv2.imshow("Phone Shamer", annotated)

    # Check for 'q' key to quit
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break
```

Or run in headless mode by editing config:

```yaml
# config/config.yaml
display:
  enabled: false  # Disable GUI
```

### 2. Configure for Server Camera

```bash
# Find camera on server
python3 list_cameras.py

# Update config/config.yaml with correct device_index
```

### 3. Set Up Logging

```bash
# Logs will go to phone_shamer.log
tail -f phone_shamer.log  # Monitor in real-time
```

---

## 🎬 Running on Server

### Option 1: Foreground (Testing)

```bash
source venv/bin/activate
python3 src/main.py
```

Press `Ctrl+C` to stop.

### Option 2: Background with nohup

```bash
source venv/bin/activate
nohup python3 src/main.py > output.log 2>&1 &

# Get process ID
echo $! > phone_shamer.pid

# Check if running
ps -p $(cat phone_shamer.pid)

# View logs
tail -f output.log

# Stop
kill $(cat phone_shamer.pid)
```

### Option 3: Using screen (Recommended)

```bash
# Install screen
sudo apt install screen

# Start screen session
screen -S phone-shamer

# Activate venv and run
source venv/bin/activate
python3 src/main.py

# Detach: Press Ctrl+A then D

# Reattach later
screen -r phone-shamer

# List sessions
screen -ls
```

### Option 4: Using systemd (Production)

Create service file:
```bash
sudo nano /etc/systemd/system/phone-shamer.service
```

Content:
```ini
[Unit]
Description=Phone Shamer Detection Service
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/home/user/phone-shamer
Environment="PATH=/home/user/phone-shamer/venv/bin"
ExecStart=/home/user/phone-shamer/venv/bin/python3 src/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable phone-shamer
sudo systemctl start phone-shamer

# Check status
sudo systemctl status phone-shamer

# View logs
sudo journalctl -u phone-shamer -f

# Stop
sudo systemctl stop phone-shamer
```

---

## 📊 Headless Analytics Generation

### Generate Posts Without Display

```bash
# Activate venv
source venv/bin/activate

# Generate analytics
python3 create_analytics_post.py --period week
python3 create_analytics_post.py --period month

# View stats in terminal
python3 view_stats.py

# Create posts and transfer back to local
scp data/posts/*.jpg local_machine:/path/to/destination/
```

---

## 🔧 Troubleshooting Server Issues

### Camera Not Found

```bash
# List video devices
ls -l /dev/video*

# Check permissions
sudo usermod -a -G video $USER
# Logout and login again

# Test camera
python3 list_cameras.py
```

### Display Error (No $DISPLAY)

```bash
# Use opencv-python-headless instead
pip uninstall opencv-python
pip install opencv-python-headless
```

### Memory Issues (Old Server)

Edit `config/config.yaml`:
```yaml
camera:
  resolution_width: 640   # Lower resolution
  resolution_height: 480

detection:
  model_size: "n"         # Use nano (smallest)
  frame_skip: 5           # Process fewer frames
```

### CPU Too Slow

```yaml
detection:
  frame_skip: 10          # Process every 10th frame
  device: "cpu"

camera:
  resolution_width: 320   # Very low
  resolution_height: 240
```

### Disk Space Issues

```bash
# Clean old screenshots
find data/screenshots -type f -mtime +7 -delete  # Delete >7 days old

# Or limit in code
python3 -c "
from storage.database import DatabaseManager
from utils.config import Config
config = Config.load()
db = DatabaseManager(config.storage.database_path)
db.clear_old_events(days_to_keep=7)
"
```

---

## 🔐 Security Considerations

### 1. Secure .env File

```bash
# Set proper permissions
chmod 600 .env

# Never commit to git
echo ".env" >> .gitignore
```

### 2. Firewall (if exposing ports)

```bash
# Ubuntu
sudo ufw allow 22/tcp  # SSH only
sudo ufw enable
```

### 3. Update Regularly

```bash
# Update Python packages
source venv/bin/activate
pip install --upgrade pip
pip install --upgrade -r requirements.txt
```

---

## 📈 Performance Optimization for Old Servers

### 1. Use Lightweight Config

```yaml
camera:
  device_index: 0
  resolution_width: 640
  resolution_height: 480
  fps_target: 15  # Lower FPS

detection:
  model_size: "n"  # Nano (fastest)
  confidence_threshold: 0.6
  device: "cpu"
  frame_skip: 5  # Process every 5th frame

proximity:
  temporal_consistency_frames: 3  # Require fewer frames
```

### 2. Disable Unnecessary Features

```python
# In src/main.py, comment out:
# - cv2.imshow() calls
# - Screenshot annotation (save raw frames)
# - Real-time statistics queries
```

### 3. Use Cron for Periodic Processing

Instead of 24/7, run at specific times:

```bash
crontab -e

# Run 9am-6pm on weekdays
0 9 * * 1-5 cd /home/user/phone-shamer && ./venv/bin/python3 src/main.py &
0 18 * * 1-5 pkill -f "python3 src/main.py"
```

---

## 🧪 Testing on Server

```bash
# 1. Test camera
python3 list_cameras.py

# 2. Test detection (short run)
timeout 30 python3 src/main.py

# 3. Check logs
tail -f phone_shamer.log

# 4. Verify database
python3 view_stats.py

# 5. Test post generation
python3 create_pro_post.py --type daily
```

---

## 📦 No Binaries Needed!

Python is **interpreted**, so you just transfer source code:

### What to Transfer:
✅ `.py` files (source code)
✅ `config/config.yaml` (configuration)
✅ `requirements.txt` (dependencies)
✅ `.env.example` (template)

### What NOT to Transfer:
❌ `__pycache__/` (bytecode cache)
❌ `*.pyc` (compiled bytecode)
❌ `venv/` (virtual environment)
❌ `data/` (local data)
❌ `.instagram_session.json` (login session)
❌ `*.log` (log files)

### Dependencies Install Automatically:
The YOLOv8 model (~6MB) downloads on first run automatically.

---

## 🚀 Quick Deploy Script

Save as `deploy.sh`:

```bash
#!/bin/bash
set -e

echo "📦 Deploying Phone Shamer to Server..."

# Create venv
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Setup directories
mkdir -p data/screenshots data/models data/database data/posts

# Copy config template
if [ ! -f .env ]; then
    cp .env.example .env
    echo "⚠️  Edit .env with your credentials"
fi

# Test installation
python3 -c "import cv2; import ultralytics; print('✅ All imports successful')"

echo "✅ Deployment complete!"
echo "Run: source venv/bin/activate && python3 src/main.py"
```

Make executable and run:
```bash
chmod +x deploy.sh
./deploy.sh
```

---

## 📊 Monitoring & Maintenance

### Auto-restart on Crash

With systemd (see above), it auto-restarts on failure.

### Daily Stats Email

```bash
# Add to crontab
0 20 * * * cd /home/user/phone-shamer && ./venv/bin/python3 view_stats.py | mail -s "Daily Phone Stats" your@email.com
```

### Disk Space Monitor

```bash
# Add to crontab
0 0 * * * find /home/user/phone-shamer/data/screenshots -mtime +30 -delete
```

---

## ✅ Deployment Checklist

Before going live:

- [ ] Python 3.8+ installed
- [ ] System dependencies installed
- [ ] Virtual environment created
- [ ] Requirements installed
- [ ] Camera detected (`list_cameras.py`)
- [ ] `.env` configured (if using Instagram)
- [ ] Config adjusted for server specs
- [ ] Test run successful (30 seconds)
- [ ] Logging working
- [ ] Database created
- [ ] Screenshots saving
- [ ] Service/screen configured for persistence
- [ ] Monitoring set up

---

Happy deploying! 🚀
