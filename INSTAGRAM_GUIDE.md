# 📱 Instagram Auto-Posting Guide

Post your phone shame stats directly to Instagram Stories or Feed!

## ⚠️ IMPORTANT SAFETY FEATURES

This script has **MULTIPLE safety layers** to prevent accidental posting:

1. **🔒 Dry-run mode by default** - Nothing posts without `--no-dry-run` flag
2. **🔐 AUTO_POST_ENABLED flag** - Must be set to `true` in `.env`
3. **✋ Double confirmation** - Must type `YES` then `POST NOW`
4. **👁️ Preview before posting** - See exactly what will be posted
5. **📂 Session management** - Avoid repeated logins

**NOTHING posts without your explicit approval!**

---

## Setup

### Step 1: Install dependency

```bash
pip install instagrapi
```

### Step 2: Create `.env` file

Copy the example:
```bash
cp .env.example .env
```

Edit `.env` with your credentials:
```bash
INSTAGRAM_USERNAME=your_username_here
INSTAGRAM_PASSWORD=your_password_here
AUTO_POST_ENABLED=false  # Set to true ONLY when ready to post
```

**⚠️ NEVER commit `.env` to git!** (Already in `.gitignore`)

---

## Usage

### Safe Preview Mode (Default)

Preview without posting:

```bash
python3 post_to_instagram.py --image data/posts/shame_post.png --type story
```

This will:
- ✅ Show image preview
- ✅ Show caption
- ✅ Show image dimensions
- ❌ NOT post anything

---

### Actually Post (With Approval)

**Step 1:** Set `AUTO_POST_ENABLED=true` in `.env`

**Step 2:** Run with `--no-dry-run`:

```bash
python3 post_to_instagram.py \
  --image data/posts/shame_overlay_abc123.png \
  --type story \
  --no-dry-run
```

**Step 3:** You'll be asked:
```
⚠️  WARNING: This will POST to your Instagram account!
⚠️  This action CANNOT be undone easily!

Type 'YES' (all caps) to confirm posting.
👉 Your decision: YES

🚨 FINAL CONFIRMATION 🚨
Type 'POST NOW' to proceed.
👉 Final confirmation: POST NOW
```

Only after typing `YES` and `POST NOW` will it post!

---

## Post Types

### 1. Instagram Story (Recommended)

Stories disappear after 24 hours:

```bash
python3 post_to_instagram.py \
  --image data/posts/your_image.png \
  --type story \
  --caption "Caught again! 📱😅" \
  --no-dry-run
```

**Best for:**
- Daily updates
- Temporary shame
- Casual sharing

### 2. Instagram Feed

Permanent post to your profile:

```bash
python3 post_to_instagram.py \
  --image data/posts/your_image.png \
  --type feed \
  --caption "Weekly phone addiction report 📊 #digitaldetox" \
  --no-dry-run
```

**Best for:**
- Weekly reports
- Milestone posts
- Permanent accountability

---

## Workflow Examples

### Example 1: Generate + Preview + Post

```bash
# Step 1: Generate overlay post
python3 create_overlay_post.py --mode latest

# Step 2: Preview (safe)
python3 post_to_instagram.py \
  --image data/posts/shame_overlay_abc123.png \
  --type story \
  --caption "Caught red-handed again! 🚨 #phoneshamer"

# Step 3: If happy, post for real
python3 post_to_instagram.py \
  --image data/posts/shame_overlay_abc123.png \
  --type story \
  --caption "Caught red-handed again! 🚨 #phoneshamer" \
  --no-dry-run
```

### Example 2: Daily Auto-Shame Routine

```bash
# Run detection all day
python3 src/main.py

# End of day: Create today's posts
python3 create_overlay_post.py --mode all-today

# Review and post your favorite one
python3 post_to_instagram.py \
  --image data/posts/shame_overlay_[pick_one].png \
  --type story \
  --no-dry-run
```

### Example 3: Weekly Report

```bash
# Create weekly report
python3 create_shame_post.py --type weekly

# Post to feed (permanent)
python3 post_to_instagram.py \
  --image data/posts/weekly_report_2026-01-06.png \
  --type feed \
  --caption "This week's phone addiction stats... yikes! 📊 Time to detox! #digitalwellness" \
  --no-dry-run
```

---

## Captions & Hashtags

### Fun Caption Ideas:

**For Stories:**
- "Caught again! 🚨 Strike #7 today 📱"
- "My phone shamer caught me... again 😅"
- "This is embarrassing 😬 #phoneaddict"
- "Red-handed! Time for a digital detox 📵"

**For Feed Posts:**
- "Week 1 of phone tracking: 42 times caught! Time to improve 💪 #digitaldetox"
- "Real talk: I checked my phone 15 times today. Accountability starts here 📱"
- "My AI phone shamer keeps me honest 🤖 Who else needs this?"

### Popular Hashtags:
```
#phoneshamer #digitaldetox #screentime #phonefree
#digitalwellness #techaddiction #unplugged
#socialmediadetox #mindfultech #screenfreetime
```

---

## Session Management

### First Login

First time you run it, you'll need to login:
- May trigger 2FA (check your phone/email)
- Session is saved to `data/.instagram_session.json`
- Next time: no 2FA needed!

### If Session Expires

Delete the session file and login again:
```bash
rm data/.instagram_session.json
```

---

## Troubleshooting

### "instagrapi not installed"

```bash
pip install instagrapi
```

### "Instagram credentials not found"

Create `.env` file with your username/password (see Setup)

### "Login failed"

Reasons:
1. Wrong username/password
2. 2FA required (check phone/email)
3. Session expired (delete `data/.instagram_session.json`)
4. Instagram rate limiting (wait 30 minutes)

### "Failed to post: Image format"

Instagram prefers:
- **Format:** JPG (not PNG sometimes fails)
- **Dimensions:** 1080x1080 (square) or 1080x1920 (9:16 story)

Convert if needed:
```bash
# Convert PNG to JPG
python3 -c "from PIL import Image; img=Image.open('input.png').convert('RGB'); img.save('output.jpg', quality=95)"
```

### "Rate limiting"

Instagram limits posts per hour. If you get rate limited:
- Wait 30-60 minutes
- Don't post too frequently
- Use stories (less strict) instead of feed

---

## Security Best Practices

1. **Never share `.env`** - Contains your password!
2. **Use app-specific password** - If you have 2FA enabled, generate an app password
3. **Don't commit session file** - Already in `.gitignore`
4. **Rotate password periodically** - Update in `.env`
5. **Monitor login alerts** - Instagram will notify you of new logins

---

## Advanced: Automated Daily Posts

### Option 1: Manual Daily Routine

```bash
#!/bin/bash
# daily_shame_post.sh

# Create today's overlay
python3 create_overlay_post.py --mode latest

# Find latest post
LATEST=$(ls -t data/posts/shame_overlay_*.png | head -1)

# Preview first
python3 post_to_instagram.py --image "$LATEST" --type story

# If happy, post with --no-dry-run
```

### Option 2: Cron Job (Advanced Users)

**⚠️ Only if you're 100% sure about automation!**

```bash
# Edit crontab
crontab -e

# Post daily at 9 PM (requires AUTO_POST_ENABLED=true)
0 21 * * * cd /path/to/phone-shamer && python3 auto_post_daily.py
```

---

## FAQ

**Q: Will this post without asking?**
A: NO! Multiple confirmations required. Dry-run by default.

**Q: Can I schedule posts?**
A: Not built-in. Must run manually with approval each time.

**Q: What if I accidentally post?**
A: Delete immediately from Instagram app. Stories disappear in 24h anyway.

**Q: Does Instagram ban automation?**
A: Instagram discourages bots. This tool:
  - ✅ Uses official-like API (instagrapi)
  - ✅ Requires manual approval
  - ✅ Saves sessions (looks natural)
  - ⚠️ Use responsibly, don't spam

**Q: Can friends see these posts?**
A: Yes! That's the point - social accountability! You can:
  - Use "Close Friends" list for stories
  - Make posts private
  - Or just don't post publicly 😅

---

## Tips for Maximum Engagement

1. **Post at peak times** - 11am-1pm or 7pm-9pm
2. **Use stories first** - Less permanent, easier to test
3. **Tag friends** - "@friend caught me too 😅"
4. **Add polls** - "Should I put my phone down?"
5. **Be consistent** - Daily updates build habit
6. **Show progress** - "Week 1: 42 times → Week 2: 28 times!"

---

Happy (responsible) posting! 📱✨
