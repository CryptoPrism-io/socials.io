"""Google Services integration module for Drive and Sheets operations."""

import os
import json
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build

class GoogleServicesManager:
    """Manager for Google Sheets and Drive operations."""

    def __init__(self):
        """Initialize Google services with credentials from environment."""
        self.gcp_credentials_json = os.getenv('GCP_CREDENTIALS')
        self.scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive',
            'https://www.googleapis.com/auth/spreadsheets'
        ]
        self.credentials = None
        self.gc = None
        self.drive_service = None
        self._initialize_services()

    def _initialize_services(self):
        """Initialize Google services with credentials."""
        if not self.gcp_credentials_json:
            raise ValueError("GCP_CREDENTIALS environment variable is not set")

        try:
            # Load credentials from environment variable
            credentials_dict = json.loads(self.gcp_credentials_json)
            self.credentials = ServiceAccountCredentials.from_json_keyfile_dict(
                credentials_dict, self.scope
            )
            print("✅ Credentials successfully loaded.")

            # Authorize gspread client
            self.gc = gspread.authorize(self.credentials)

            # Build Drive service
            self.drive_service = build('drive', 'v3', credentials=self.credentials)

        except Exception as e:
            print(f"❌ Error: Failed to initialize Google services. {e}")
            raise

    def get_drive_service(self):
        """Get Google Drive service instance."""
        return self.drive_service

    def load_spreadsheet_data(self, spreadsheet_key):
        """Load all sheets from a Google Spreadsheet into DataFrames."""
        try:
            # Open spreadsheet
            sh = self.gc.open_by_key(spreadsheet_key)

            # Get all sheet names
            sheet_names = [sheet.title for sheet in sh.worksheets()]
            print(f"✅ Found {len(sheet_names)} sheets: {', '.join(sheet_names)}")

            # Load each sheet into a DataFrame
            sheets_data = {}
            for sheet_name in sheet_names:
                worksheet = sh.worksheet(sheet_name)
                data = worksheet.get_all_values()
                if data:
                    df = pd.DataFrame(data[1:], columns=data[0])
                    sheets_data[sheet_name] = df
                    print(f"✅ Loaded sheet: {sheet_name} ({len(df)} rows)")
                else:
                    sheets_data[sheet_name] = pd.DataFrame()
                    print(f"⚠️  Empty sheet: {sheet_name}")

            print("✅ Spreadsheet data loaded successfully")
            return sheets_data

        except Exception as e:
            print(f"❌ Error loading spreadsheet: {e}")
            return {}

    def validate_required_sheets(self, sheets_data, required_sheets):
        """Validate that required sheets are present in the data."""
        missing_sheets = [sheet for sheet in required_sheets if sheet not in sheets_data]

        if missing_sheets:
            print(f"⚠️  Warning: Missing sheets: {', '.join(missing_sheets)}")
            print("⚠️  Bot will continue with available data...")

        return missing_sheets

    def process_top_coins_data(self, sheets_data):
        """Process Top50Coins sheet data to extract gainers and losers."""
        if 'Top50Coins' not in sheets_data:
            return None, None, 'N/A', 'N/A', 'N/A', 'N/A'

        try:
            top50_coins = sheets_data['Top50Coins']

            # Convert percentage columns to numeric
            top50_coins['pct_1d_num'] = pd.to_numeric(
                top50_coins['pct_1d'].str.replace('%', ''), errors='coerce'
            ).fillna(0)

            # Get top gainer and loser
            top_gainer = top50_coins.loc[top50_coins['pct_1d_num'].idxmax()]
            top_loser = top50_coins.loc[top50_coins['pct_1d_num'].idxmin()]

            gainer_symbol = top_gainer['symbol'] if 'symbol' in top_gainer else 'N/A'
            gainer_pct = top_gainer['pct_1d'] if 'pct_1d' in top_gainer else '0%'
            loser_symbol = top_loser['symbol'] if 'symbol' in top_loser else 'N/A'
            loser_pct = top_loser['pct_1d'] if 'pct_1d' in top_loser else '0%'

            print(f"✅ Top gainer: {gainer_symbol} ({gainer_pct})")
            print(f"✅ Top loser: {loser_symbol} ({loser_pct})")

            return top_gainer, top_loser, gainer_symbol, gainer_pct, loser_symbol, loser_pct

        except Exception as e:
            print(f"⚠️  Error processing Top50Coins: {e}")
            return None, None, 'N/A', 'N/A', 'N/A', 'N/A'

    def process_btc_snapshot_data(self, sheets_data):
        """Process BTC_SNAPSHOT sheet data."""
        if 'BTC_SNAPSHOT' not in sheets_data:
            return {k: 'N/A' for k in [
                'slug', 'rank', 'symbol', 'price', 'percent_change_24h', 'volume_24h',
                'market_cap', 'percent_change_7d', 'percent_change_30d', 'ytd_change',
                'last_updated', 'colour_24h', 'bullish', 'bearish', 'neutral',
                'sentiment_diff', 'trend'
            ]}

        try:
            btc_snapshot = sheets_data['BTC_SNAPSHOT']
            btc_row = btc_snapshot.iloc[0]

            btc_data = {
                'slug': btc_row.get('slug', 'bitcoin'),
                'rank': btc_row.get('cmc_rank', '1'),
                'symbol': btc_row.get('symbol', 'BTC'),
                'price': btc_row.get('price', '$0.00'),
                'percent_change_24h': btc_row.get('percent_change24h', '0%'),
                'volume_24h': btc_row.get('volume24h', '$0'),
                'market_cap': btc_row.get('market_cap', '$0'),
                'percent_change_7d': btc_row.get('percent_change7d', '0%'),
                'percent_change_30d': btc_row.get('percent_change30d', '0%'),
                'ytd_change': btc_row.get('ytd_price_change_percentage', '0%'),
                'last_updated': btc_row.get('last_updated', 'N/A'),
                'colour_24h': btc_row.get('colour_percent_change24h', 'green'),
                'bullish': btc_row.get('bullish', '0'),
                'bearish': btc_row.get('bearish', '0'),
                'neutral': btc_row.get('neutral', '0'),
                'sentiment_diff': btc_row.get('sentiment_diff', '0'),
                'trend': btc_row.get('Trend', 'Neutral')
            }

            print(f"✅ BTC data loaded: {btc_data['price']} ({btc_data['percent_change_24h']})")
            return btc_data

        except Exception as e:
            print(f"⚠️  Error extracting BTC data: {e}")
            return {k: 'N/A' for k in [
                'slug', 'rank', 'symbol', 'price', 'percent_change_24h', 'volume_24h',
                'market_cap', 'percent_change_7d', 'percent_change_30d', 'ytd_change',
                'last_updated', 'colour_24h', 'bullish', 'bearish', 'neutral',
                'sentiment_diff', 'trend'
            ]}

    def process_trading_opportunities(self, sheets_data):
        """Process short and long opportunities from sheets data."""
        # Process short opportunities
        if 'ShortOpportunities' in sheets_data:
            try:
                short_opps = sheets_data['ShortOpportunities']
                short_opps['bearish_count'] = pd.to_numeric(
                    short_opps['bearish_count'], errors='coerce'
                ).fillna(0)
                top_shorts = short_opps.nlargest(2, 'bearish_count')
                print(f"✅ Top shorts loaded: {len(top_shorts)} opportunities")
            except Exception as e:
                print(f"⚠️  Error processing short opportunities: {e}")
                top_shorts = pd.DataFrame({
                    'slug': ['crypto1', 'crypto2'],
                    'bearish_count': [0, 0],
                    'market_cap': ['$0', '$0'],
                    'percent_change24h': ['0%', '0%']
                })
        else:
            top_shorts = pd.DataFrame({
                'slug': ['crypto1', 'crypto2'],
                'bearish_count': [0, 0],
                'market_cap': ['$0', '$0'],
                'percent_change24h': ['0%', '0%']
            })

        # Process long opportunities
        if 'LongOpportunities' in sheets_data:
            try:
                long_opps = sheets_data['LongOpportunities']
                long_opps['bullish_count'] = pd.to_numeric(
                    long_opps['bullish_count'], errors='coerce'
                ).fillna(0)
                top_longs = long_opps.nlargest(2, 'bullish_count')
                print(f"✅ Top longs loaded: {len(top_longs)} opportunities")
            except Exception as e:
                print(f"⚠️  Error processing long opportunities: {e}")
                top_longs = pd.DataFrame({
                    'slug': ['crypto1', 'crypto2'],
                    'bullish_count': [0, 0],
                    'market_cap': ['$0', '$0'],
                    'percent_change24h': ['0%', '0%']
                })
        else:
            top_longs = pd.DataFrame({
                'slug': ['crypto1', 'crypto2'],
                'bullish_count': [0, 0],
                'market_cap': ['$0', '$0'],
                'percent_change24h': ['0%', '0%']
            })

        return top_shorts, top_longs

def create_google_services_manager():
    """Factory function to create Google Services Manager."""
    return GoogleServicesManager()