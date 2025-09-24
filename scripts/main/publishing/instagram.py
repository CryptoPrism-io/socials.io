"""Instagram publishing module with session management."""

import os
import json
import io
from pathlib import Path
from instagrapi import Client
from PIL import Image, ImageDraw, ImageFont

class InstagramPublisher:
    """Instagram publishing client with session management."""

    def __init__(self, drive_service, drive_file_id, local_session_path='instagram_settings.json'):
        """Initialize Instagram publisher with Google Drive session management."""
        self.drive_service = drive_service
        self.drive_file_id = drive_file_id
        self.local_session_path = local_session_path
        self.client = None
        self.username = os.getenv('INSTAGRAM_USERNAME')
        self.password = os.getenv('INSTAGRAM_PASSWORD')

    def download_session_from_drive(self):
        """Download Instagram session from Google Drive."""
        try:
            from googleapiclient.http import MediaIoBaseDownload

            request = self.drive_service.files().get_media(fileId=self.drive_file_id)
            with io.FileIO(self.local_session_path, 'wb') as file:
                downloader = MediaIoBaseDownload(file, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
            print(f"✅ Downloaded session from Drive to {self.local_session_path}")
            return True
        except Exception as e:
            print(f"❌ Error downloading session from Drive: {e}")
            return False

    def upload_session_to_drive(self):
        """Upload Instagram session to Google Drive."""
        try:
            from googleapiclient.http import MediaFileUpload

            media = MediaFileUpload(self.local_session_path, mimetype='application/json')
            self.drive_service.files().update(fileId=self.drive_file_id, media_body=media).execute()
            print(f"✅ Uploaded {self.local_session_path} to Google Drive")
            return True
        except Exception as e:
            print(f"❌ Error uploading session to Drive: {e}")
            return False

    def setup_client(self):
        """Setup Instagram client using existing session from Google Drive."""
        # Step 1: Always try to download from Google Drive first
        if not self.download_session_from_drive():
            print("❌ CRITICAL: Could not download session from Google Drive!")
            print("❌ STOPPING: Will not create new session to avoid Instagram device issues")
            return False

        # Step 2: Check if the downloaded file exists and is valid
        if not Path(self.local_session_path).exists():
            print("❌ CRITICAL: Settings file not found after download!")
            return False

        # Step 3: Try to load the settings file
        try:
            with open(self.local_session_path, 'r') as f:
                settings = json.load(f)
            print("✅ Settings file loaded successfully")
        except json.JSONDecodeError:
            print("❌ CRITICAL: Settings file is corrupted!")
            return False
        except Exception as e:
            print(f"❌ CRITICAL: Error reading settings file: {e}")
            return False

        # Step 4: Initialize client with existing settings
        try:
            self.client = Client()
            self.client.load_settings(self.local_session_path)
            print("✅ Instagram client initialized with existing session")

            # Step 5: Test the session with a simple, low-impact call
            try:
                user_info = self.client.user_info_by_username(self.client.username)
                print(f"✅ Session verified - logged in as: {user_info.username}")
                return True

            except Exception as session_error:
                print(f"⚠️  Session verification failed: {session_error}")
                print("⚠️  This might be temporary - proceeding with existing session anyway")
                print("⚠️  Instagram will prompt for re-auth if truly needed")
                return True

        except Exception as e:
            print(f"❌ CRITICAL: Could not initialize Instagram client: {e}")
            return False

    def create_placeholder_image(self, output_path, slide_number=1, size=(1080, 1080)):
        """Create a placeholder image when content is not available."""
        img = Image.new('RGB', size, color=(20, 20, 30))
        draw = ImageDraw.Draw(img)

        try:
            # Try to use a better font
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
        except:
            try:
                # Windows font fallback
                font = ImageFont.truetype("arial.ttf", 60)
            except:
                font = ImageFont.load_default()

        text = f"Crypto Update\nSlide {slide_number}"
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        x = (size[0] - text_width) // 2
        y = (size[1] - text_height) // 2

        draw.text((x, y), text, fill=(255, 255, 255), font=font, align="center")
        img.save(output_path)
        print(f"Created placeholder image: {output_path}")

    def prepare_media_files(self, image_dir, num_slides=6):
        """Prepare media files for Instagram upload, creating placeholders if needed."""
        media_files = []
        image_path = Path(image_dir)

        for i in range(1, num_slides + 1):
            file_path = image_path / f"{i}_output.jpg"
            if file_path.exists():
                media_files.append(file_path)
                print(f"✅ Found {file_path}")
            else:
                print(f"⚠️  {file_path} not found. Creating placeholder...")
                self.create_placeholder_image(str(file_path), i)
                media_files.append(file_path)

        print(f"✅ Prepared {len(media_files)} media files")
        return media_files

    def upload_carousel_post(self, media_files, caption):
        """Upload carousel post to Instagram."""
        if not self.client:
            print("❌ Instagram client not initialized")
            return False

        if not media_files or not caption:
            print("❌ Missing media files or caption for upload")
            return False

        try:
            print("🔄 Uploading to Instagram...")
            print(f"📝 Caption preview (first 200 chars): {caption[:200]}...")

            # Upload carousel post
            media = self.client.album_upload(media_files, caption)
            print("✅ Successfully uploaded to Instagram!")
            print(f"📱 Post ID: {media.id}")

            # Update the session file back to Google Drive after successful upload
            self.client.dump_settings(self.local_session_path)
            self.upload_session_to_drive()
            print("✅ Session updated and saved to Google Drive")

            return True

        except Exception as upload_error:
            print(f"❌ Upload failed: {upload_error}")
            print("❌ This could be due to:")
            print("   - Instagram rate limits")
            print("   - Session expired (try creating new session)")
            print("   - Network issues")
            print("   - Instagram policy violations")

            # Still try to save session updates
            try:
                self.client.dump_settings(self.local_session_path)
                self.upload_session_to_drive()
                print("✅ Session state saved despite upload failure")
            except:
                print("⚠️  Could not save session updates")

            return False

    def cleanup_temp_files(self, media_files=None):
        """Clean up temporary files."""
        print("🧹 Cleaning up temporary files...")
        try:
            # Remove session file
            if Path(self.local_session_path).exists():
                os.remove(self.local_session_path)

            # Remove media files if specified
            if media_files:
                for file_path in media_files:
                    if Path(file_path).exists():
                        os.remove(file_path)

            print("✅ Temporary files cleaned up")
        except Exception as e:
            print(f"⚠️  Error cleaning up: {e}")

    def publish_content(self, image_dir, caption, num_slides=6, cleanup=True):
        """Complete Instagram publishing workflow."""
        print("🔄 Starting Instagram publishing workflow...")

        # Setup client
        if not self.setup_client():
            print("❌ STOPPING: Could not establish Instagram session")
            return False

        # Prepare media files
        print("🔄 Preparing media files...")
        media_files = self.prepare_media_files(image_dir, num_slides)

        # Upload to Instagram
        success = self.upload_carousel_post(media_files, caption)

        # Cleanup
        if cleanup:
            self.cleanup_temp_files(media_files if not success else None)

        return success

def create_instagram_publisher(drive_service, drive_file_id):
    """Factory function to create Instagram publisher."""
    return InstagramPublisher(drive_service, drive_file_id)