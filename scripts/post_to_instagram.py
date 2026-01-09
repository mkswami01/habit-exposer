"""
Instagram poster with MANDATORY APPROVAL.
NOTHING posts without explicit user confirmation!
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv
from PIL import Image
import time

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Try to import instagrapi
try:
    from instagrapi import Client
    from instagrapi.exceptions import LoginRequired
except ImportError:
    print("❌ instagrapi not installed!")
    print("Run: pip install instagrapi")
    sys.exit(1)


class InstagramPoster:
    """Instagram poster with safety checks and approval requirements."""

    def __init__(self):
        """Initialize Instagram client."""
        # Load environment variables
        load_dotenv()

        self.username = os.getenv('INSTAGRAM_USERNAME')
        self.password = os.getenv('INSTAGRAM_PASSWORD')
        self.auto_post_enabled = os.getenv('AUTO_POST_ENABLED', 'false').lower() == 'true'

        self.client = None
        self.session_file = Path("data/.instagram_session.json")

        # Safety check
        if not self.username or not self.password:
            print("❌ Instagram credentials not found!")
            print("Create a .env file with:")
            print("  INSTAGRAM_USERNAME=your_username")
            print("  INSTAGRAM_PASSWORD=your_password")
            sys.exit(1)

    def login(self):
        """Login to Instagram with session management."""
        self.client = Client()

        print("🔐 Logging in to Instagram...")

        try:
            # Try to load existing session
            if self.session_file.exists():
                print("📂 Loading saved session...")
                self.client.load_settings(self.session_file)
                self.client.login(self.username, self.password)
                print("✅ Logged in using saved session!")
            else:
                # Fresh login
                print("🆕 Fresh login (this may trigger 2FA)...")
                self.client.login(self.username, self.password)

                # Save session for next time
                self.session_file.parent.mkdir(parents=True, exist_ok=True)
                self.client.dump_settings(self.session_file)
                print("✅ Logged in and session saved!")

            return True

        except LoginRequired as e:
            print(f"❌ Login failed: {e}")
            print("Possible reasons:")
            print("  - Wrong username/password")
            print("  - 2FA required (check your phone/email)")
            print("  - Session expired (delete data/.instagram_session.json)")
            return False

        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False

    def preview_post(self, image_path: str, caption: str):
        """Show preview of what will be posted."""
        print("\n" + "="*60)
        print("📸 POST PREVIEW")
        print("="*60)
        print(f"\n📁 Image: {image_path}")

        # Check if image exists
        if not Path(image_path).exists():
            print(f"❌ Image not found: {image_path}")
            return False

        # Show image info
        try:
            img = Image.open(image_path)
            print(f"📐 Size: {img.width}x{img.height}")
            print(f"📊 Format: {img.format}")
        except Exception as e:
            print(f"❌ Error reading image: {e}")
            return False

        print(f"\n📝 Caption ({len(caption)} chars):")
        print("-"*60)
        print(caption)
        print("-"*60)
        print()

        return True

    def get_approval(self) -> bool:
        """
        Get explicit user approval before posting.
        Returns True only if user types 'YES' exactly.
        """
        print("⚠️  WARNING: This will POST to your Instagram account!")
        print("⚠️  This action CANNOT be undone easily!")
        print()
        print("Type 'YES' (all caps) to confirm posting.")
        print("Type anything else to cancel.")
        print()

        response = input("👉 Your decision: ").strip()

        if response == "YES":
            # Double confirmation
            print()
            print("🚨 FINAL CONFIRMATION 🚨")
            print("Type 'POST NOW' to proceed.")
            print()
            response2 = input("👉 Final confirmation: ").strip()

            if response2 == "POST NOW":
                return True
            else:
                print("❌ Second confirmation failed. Cancelled.")
                return False
        else:
            print("❌ Cancelled. Nothing was posted.")
            return False

    def post_to_story(self, image_path: str, caption: str = "", dry_run: bool = True):
        """
        Post to Instagram Story with approval.

        Args:
            image_path: Path to image file
            caption: Text caption for story
            dry_run: If True, only preview without posting
        """
        print("\n🎬 Instagram Story Poster")
        print("="*60)

        # Show preview
        if not self.preview_post(image_path, caption):
            return False

        # Dry run mode
        if dry_run:
            print("🔒 DRY RUN MODE - Nothing will be posted")
            print("💡 To actually post, use: --no-dry-run")
            print()
            return True

        # Safety check
        if not self.auto_post_enabled:
            print("🔒 AUTO_POST_ENABLED=false in .env")
            print("💡 Set AUTO_POST_ENABLED=true if you want to enable posting")
            print()
            return False

        # Get approval
        if not self.get_approval():
            return False

        # Login if needed
        if not self.client:
            if not self.login():
                return False

        # Post to story
        try:
            print("\n📤 Posting to Instagram Story...")

            # Convert to Path
            photo_path = Path(image_path)

            # Upload
            self.client.photo_upload_to_story(photo_path, caption=caption)

            print()
            print("✅ SUCCESS! Posted to Instagram Story!")
            print(f"👁️  Check your Instagram app to see it")
            print()

            return True

        except Exception as e:
            print(f"\n❌ Failed to post: {e}")
            print("\nPossible issues:")
            print("  - Image format not supported (try JPG)")
            print("  - Instagram rate limiting")
            print("  - Session expired")
            print("  - Image dimensions too large")
            return False

    def post_to_feed(self, image_path: str, caption: str = "", dry_run: bool = True):
        """
        Post to Instagram Feed with approval.

        Args:
            image_path: Path to image file
            caption: Caption for post
            dry_run: If True, only preview without posting
        """
        print("\n📱 Instagram Feed Poster")
        print("="*60)

        # Show preview
        if not self.preview_post(image_path, caption):
            return False

        # Dry run mode
        if dry_run:
            print("🔒 DRY RUN MODE - Nothing will be posted")
            print("💡 To actually post, use: --no-dry-run")
            print()
            return True

        # Safety check
        if not self.auto_post_enabled:
            print("🔒 AUTO_POST_ENABLED=false in .env")
            print("💡 Set AUTO_POST_ENABLED=true if you want to enable posting")
            print()
            return False

        # Get approval
        if not self.get_approval():
            return False

        # Login if needed
        if not self.client:
            if not self.login():
                return False

        # Post to feed
        try:
            print("\n📤 Posting to Instagram Feed...")

            # Convert to Path
            photo_path = Path(image_path)

            # Upload
            self.client.photo_upload(photo_path, caption=caption)

            print()
            print("✅ SUCCESS! Posted to Instagram Feed!")
            print(f"👁️  Check your profile to see it")
            print()

            return True

        except Exception as e:
            print(f"\n❌ Failed to post: {e}")
            return False


def main():
    """CLI interface."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Post to Instagram with mandatory approval",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Preview only (safe, nothing posts)
  python3 post_to_instagram.py --image data/posts/shame_post.png --type story

  # Actually post (requires approval)
  python3 post_to_instagram.py --image data/posts/shame_post.png --type story --no-dry-run

  # Post to feed instead of story
  python3 post_to_instagram.py --image data/posts/shame_post.png --type feed --no-dry-run

Safety Features:
  - Dry run mode by default (preview only)
  - Double confirmation required
  - AUTO_POST_ENABLED flag in .env
  - Session management to avoid repeated logins
  - Nothing posts without explicit 'YES' + 'POST NOW' confirmations
        """
    )

    parser.add_argument(
        '--image',
        type=str,
        required=True,
        help='Path to image file to post'
    )
    parser.add_argument(
        '--caption',
        type=str,
        default='',
        help='Caption/text for the post'
    )
    parser.add_argument(
        '--type',
        choices=['story', 'feed'],
        default='story',
        help='Where to post (story or feed)'
    )
    parser.add_argument(
        '--no-dry-run',
        action='store_true',
        help='Actually post (without this, only preview)'
    )

    args = parser.parse_args()

    # Create poster
    poster = InstagramPoster()

    # Determine dry run mode
    dry_run = not args.no_dry_run

    if dry_run:
        print("\n🔒 RUNNING IN DRY-RUN MODE (Safe Preview)")
        print("Nothing will be posted to Instagram.")
        print("Use --no-dry-run to actually post.\n")
    else:
        print("\n⚠️  LIVE MODE - This can actually post!")
        print("You will be asked for confirmation.\n")

    # Post
    if args.type == 'story':
        success = poster.post_to_story(args.image, args.caption, dry_run=dry_run)
    else:
        success = poster.post_to_feed(args.image, args.caption, dry_run=dry_run)

    if success:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
