"""Instagram publishing workflow with data processing and AI caption generation."""

import time
import os
import sys
from pathlib import Path

# Add parent directories to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from integrations.google_services import create_google_services_manager
from content.ai_generation_captions import generate_social_media_caption
from publishing.instagram import create_instagram_publisher

class PublishingWorkflow:
    """Complete Instagram publishing workflow."""

    def __init__(self):
        """Initialize the publishing workflow."""
        self.start_time = time.time()
        self.google_services = None
        self.instagram_publisher = None
        self.sheets_data = {}
        self.processed_data = {}

        # Environment variables
        self.crypto_spreadsheet_key = os.getenv('CRYPTO_SPREADSHEET_KEY')
        self.instagram_drive_file_id = os.getenv('INSTAGRAM_DRIVE_FILE_ID')

        self._validate_environment()

    def _validate_environment(self):
        """Validate required environment variables."""
        required_vars = {
            'GCP_CREDENTIALS': os.getenv('GCP_CREDENTIALS'),
            'OPENROUTER_API_KEY': os.getenv('OPENROUTER_API_KEY'),
            'INSTAGRAM_DRIVE_FILE_ID': self.instagram_drive_file_id,
            'CRYPTO_SPREADSHEET_KEY': self.crypto_spreadsheet_key,
            'INSTAGRAM_USERNAME': os.getenv('INSTAGRAM_USERNAME'),
            'INSTAGRAM_PASSWORD': os.getenv('INSTAGRAM_PASSWORD')
        }

        missing_vars = [var for var, value in required_vars.items() if not value]
        if missing_vars:
            print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
            print("❌ Please ensure all environment variables are set!")
            raise EnvironmentError("Missing required environment variables")

        print("✅ All environment variables loaded successfully")

    def setup_services(self):
        """Initialize Google services and Instagram publisher."""
        print("🔄 Setting up services...")

        # Initialize Google services
        try:
            self.google_services = create_google_services_manager()
            print("✅ Google services initialized")
        except Exception as e:
            print(f"❌ Failed to initialize Google services: {e}")
            return False

        # Initialize Instagram publisher
        try:
            drive_service = self.google_services.get_drive_service()
            self.instagram_publisher = create_instagram_publisher(
                drive_service, self.instagram_drive_file_id
            )
            print("✅ Instagram publisher initialized")
        except Exception as e:
            print(f"❌ Failed to initialize Instagram publisher: {e}")
            return False

        return True

    def load_spreadsheet_data(self):
        """Load data from Google Spreadsheet."""
        print("🔄 Loading spreadsheet data...")

        try:
            self.sheets_data = self.google_services.load_spreadsheet_data(
                self.crypto_spreadsheet_key
            )

            # Validate required sheets
            required_sheets = ['Top50Coins', 'BTC_SNAPSHOT', 'MarketOverview',
                             'ShortOpportunities', 'LongOpportunities']

            missing_sheets = self.google_services.validate_required_sheets(
                self.sheets_data, required_sheets
            )

            if len(missing_sheets) == len(required_sheets):
                print("❌ No required sheets found!")
                return False

            return True

        except Exception as e:
            print(f"❌ Failed to load spreadsheet data: {e}")
            return False

    def process_data(self):
        """Process loaded spreadsheet data."""
        print("🔄 Processing data...")

        try:
            # Process top coins data
            (top_gainer, top_loser, gainer_symbol, gainer_pct,
             loser_symbol, loser_pct) = self.google_services.process_top_coins_data(self.sheets_data)

            # Process BTC data
            btc_data = self.google_services.process_btc_snapshot_data(self.sheets_data)

            # Process trading opportunities
            top_shorts, top_longs = self.google_services.process_trading_opportunities(self.sheets_data)

            # Store processed data
            self.processed_data = {
                'top_gainer': top_gainer,
                'top_loser': top_loser,
                'gainer_symbol': gainer_symbol,
                'gainer_pct': gainer_pct,
                'loser_symbol': loser_symbol,
                'loser_pct': loser_pct,
                'btc_data': btc_data,
                'top_shorts': top_shorts,
                'top_longs': top_longs,
                'market_data': self.sheets_data.get('MarketOverview')
            }

            print("✅ Data processing completed")
            return True

        except Exception as e:
            print(f"❌ Data processing failed: {e}")
            return False

    def generate_caption(self):
        """Generate AI-enhanced caption."""
        print("🔄 Generating caption...")

        try:
            caption = generate_social_media_caption(
                market_data=self.processed_data.get('market_data'),
                btc_data=self.processed_data.get('btc_data'),
                gainer_data=self.processed_data.get('top_gainer'),
                loser_data=self.processed_data.get('top_loser'),
                top_shorts=self.processed_data.get('top_shorts'),
                top_longs=self.processed_data.get('top_longs')
            )

            if not caption or len(caption) < 50:
                print("⚠️ Generated caption too short, using fallback")
                caption = "🚨 Crypto Market Update! 📈\n\nDaily market analysis coming your way.\n\n#Crypto #MarketUpdate #CryptoPrism"

            self.processed_data['caption'] = caption
            print(f"✅ Caption generated: {len(caption)} characters")
            return True

        except Exception as e:
            print(f"❌ Caption generation failed: {e}")
            return False

    def publish_to_instagram(self):
        """Publish content to Instagram."""
        print("🔄 Publishing to Instagram...")

        try:
            # Define image directory
            image_dir = Path(__file__).parent.parent.parent.parent / 'output_images'

            # Publish content
            success = self.instagram_publisher.publish_content(
                image_dir=str(image_dir),
                caption=self.processed_data['caption'],
                num_slides=6,
                cleanup=True
            )

            if success:
                print("✅ Successfully published to Instagram!")
                return True
            else:
                print("❌ Instagram publishing failed")
                return False

        except Exception as e:
            print(f"❌ Instagram publishing error: {e}")
            return False

    def run_workflow(self):
        """Run the complete publishing workflow."""
        print("🚀 Starting Instagram Publishing Workflow")
        print("=" * 60)

        try:
            # Setup services
            if not self.setup_services():
                return False

            # Load spreadsheet data
            if not self.load_spreadsheet_data():
                return False

            # Process data
            if not self.process_data():
                return False

            # Generate caption
            if not self.generate_caption():
                return False

            # Publish to Instagram
            success = self.publish_to_instagram()

            # Calculate execution time
            end_time = time.time()
            execution_time = end_time - self.start_time

            # Print summary
            print("\n" + "=" * 60)
            if success:
                print("🎉 INSTAGRAM PUBLISHING WORKFLOW COMPLETE!")
            else:
                print("❌ INSTAGRAM PUBLISHING WORKFLOW FAILED!")
            print("=" * 60)

            if self.sheets_data:
                sheets_count = len([name for name in ['Top50Coins', 'BTC_SNAPSHOT', 'MarketOverview',
                                                     'ShortOpportunities', 'LongOpportunities']
                                  if name in self.sheets_data])
                print(f"✅ Data sources processed: {sheets_count} sheets")

            if 'caption' in self.processed_data:
                print(f"✅ Caption length: {len(self.processed_data['caption'])} characters")

            print(f"✅ Execution time: {execution_time:.2f} seconds")

            if success:
                print("✅ Session safely preserved for next run")
                print("🔗 Check your Instagram: @cryptoprism.io")

            print("=" * 60)

            return success

        except Exception as e:
            print(f"❌ Workflow failed: {e}")
            return False

def run_publishing_workflow():
    """Factory function to run the publishing workflow."""
    workflow = PublishingWorkflow()
    return workflow.run_workflow()

if __name__ == "__main__":
    success = run_publishing_workflow()
    if not success:
        exit(1)