# 📱 Social Media Post Generator Guide

Generate fun, shareable "shame posts" from your phone detection stats!

## Post Types

### 1. 📊 Daily Summary Post
Perfect for Instagram/Twitter daily updates!

**Command:**
```bash
python3 create_shame_post.py --type daily
```

**What it includes:**
- 📱 Big bold number of times caught
- 📊 Bar chart showing peak hours
- 😄 Fun caption that changes based on usage:
  - 0-3 times: "Not bad! Room for improvement"
  - 4-10 times: "Whoa! Phone addiction level rising"
  - 11-20 times: "YIKES! Put that phone down!"
  - 21+ times: "🚨 EMERGENCY! INTERVENTION NEEDED!"

**Output:** `data/posts/shame_post_YYYY-MM-DD.png` (1080x1080)

**Example captions:**
- "Not bad! Only 3 phone checks today 📱"
- "Whoa! 12 times on the phone today! 😅"
- "🚨 EMERGENCY! 25 PHONE CHECKS TODAY! 🚨"

---

### 2. 📈 Weekly Report Post
Great for weekend recaps!

**Command:**
```bash
python3 create_shame_post.py --type weekly
```

**What it includes:**
- 📊 Total phone checks for the week
- 📉 Bar chart showing daily breakdown (Mon-Sun)
- 📐 Average usage per day
- 😬 Judgment: "Not bad!" or "Time to detox!"

**Output:** `data/posts/weekly_report_YYYY-MM-DD.png` (1080x1080)

**Perfect for:**
- Weekend accountability posts
- Tracking progress over time
- Friendly competition with friends

---

### 3. 📸 Screenshot Post ("Caught!")
The most embarrassing one - actual evidence!

**Command:**
```bash
python3 create_shame_post.py --type screenshot
```

**What it includes:**
- 📷 Your latest screenshot with detection boxes
- 🚨 Big red "CAUGHT!" banner
- ⏰ Exact timestamp when busted
- 🎨 Instagram-friendly square format

**Output:** `data/posts/caught_XXXXXXXX.png` (1080x1080)

**Perfect for:**
- Maximum embarrassment factor
- Proving you caught them red-handed
- Accountability partner check-ins

---

## Usage Examples

### Create today's post:
```bash
python3 create_shame_post.py --type daily
```

### Create post for specific date:
```bash
python3 create_shame_post.py --type daily --date 2026-01-05
```

### Create weekly report:
```bash
python3 create_shame_post.py --type weekly
```

### Create "caught" post with latest screenshot:
```bash
python3 create_shame_post.py --type screenshot
```

---

## Post Specifications

All posts are optimized for social media:

- **Format:** PNG
- **Size:** 1080x1080 pixels (Instagram square)
- **Quality:** 95%
- **Colors:** Dark theme with vibrant accents
- **Fonts:** System fonts (Helvetica)
- **Location:** `data/posts/`

---

## Tips for Sharing

### Instagram
- Perfect square format (1080x1080)
- Use hashtags: `#phoneshamer #digitaldetox #screentime #phonefree`
- Best times to post: 11am-1pm or 7pm-9pm
- Add story version for 24-hour updates

### Twitter/X
- Works great as single image tweet
- Add funny caption from the image
- Tag friends for accountability
- Use hashtags: `#PhoneAddict #DigitalWellness`

### Facebook
- Share in stories or main feed
- Great for accountability groups
- Add context about your digital detox journey

---

## Customization Ideas

Want to customize the posts? Edit `create_shame_post.py`:

### Change Colors:
```python
# Dark background
img = Image.new('RGB', (1080, 1080), color=(45, 52, 54))

# Red circle for numbers
fill=(231, 76, 60)

# Blue bars for charts
fill=(52, 152, 219)
```

### Add Custom Captions:
```python
CAPTIONS = {
    'low': [
        "Your custom message here! 📱",
        "Another option",
    ],
    # ... etc
}
```

### Change Fonts:
```python
# Use your own font
title_font = ImageFont.truetype("/path/to/font.ttf", 80)
```

---

## Fun Ideas

### 30-Day Challenge
Post daily stats for 30 days and track improvement!

### Friend Competition
Challenge friends to see who can have the lowest count!

### Before/After
Post week 1 vs week 4 to show progress!

### Streak Counter
Add days since last phone usage (customize the script)!

---

## Troubleshooting

**"No events found"**
- Run the detection system first to collect data
- Check `python3 view_stats.py` to see if you have events

**Fonts look weird**
- Script uses system Helvetica font
- Falls back to default if not found
- Edit script to use your preferred font

**Post doesn't look good**
- Make sure you have events to display
- Try different post types
- Customize colors/fonts in the script

---

## Examples of Good Posts

### Daily Post Caption Ideas:
- "Day 5 of digital detox - caught myself 8 times today 😅 #phoneshamer"
- "Phone usage: 3 times! Progress! 💪 Who else is trying to cut down?"
- "Yikes... 15 times today. Tomorrow's goal: under 10! 📵"

### Weekly Report Captions:
- "Weekly accountability: 42 times this week! Time for a phone fast 📱🚫"
- "This week vs last week: 30 times → 18 times! Improvement! 📈"
- "Confession time: 67 phone checks this week... anyone else? 😬"

### Screenshot Captions:
- "BUSTED! 🚨 My own system caught me at 2:47 PM 😂"
- "Red-handed! The evidence is clear... I have a problem 📱"
- "When your phone shame system exposes you 💀"

---

Happy shaming! 📱✨
