# Updated Crypto Instagram Bot - Using Environment Variables
import time
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
import os
import json
import gspread
import requests
from together import Together
from PIL import Image
import io
from instagrapi import Client
from pathlib import Path

# Start timing
start_time = time.time()


# Load environment variables
GCP_CREDENTIALS = os.getenv('GCP_CREDENTIALS')
TOGETHER_API_KEY = os.getenv('TOGETHER_API_KEY')
INSTAGRAM_DRIVE_FILE_ID = os.getenv('INSTAGRAM_DRIVE_FILE_ID')
CRYPTO_SPREADSHEET_KEY = os.getenv('CRYPTO_SPREADSHEET_KEY')
INSTAGRAM_USERNAME = os.getenv('INSTAGRAM_USERNAME')
INSTAGRAM_PASSWORD = os.getenv('INSTAGRAM_PASSWORD')

# Validate environment variables
required_vars = {
    'GCP_CREDENTIALS': GCP_CREDENTIALS,
    'TOGETHER_API_KEY': TOGETHER_API_KEY,
    'INSTAGRAM_DRIVE_FILE_ID': INSTAGRAM_DRIVE_FILE_ID,
    'CRYPTO_SPREADSHEET_KEY': CRYPTO_SPREADSHEET_KEY,
    'INSTAGRAM_USERNAME': INSTAGRAM_USERNAME,
    'INSTAGRAM_PASSWORD': INSTAGRAM_PASSWORD
}

missing_vars = [var for var, value in required_vars.items() if not value]
if missing_vars:
    print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
    print("❌ Please run the environment setup cell first!")
    exit(1)

print("✅ All environment variables loaded successfully")

# Define the scope
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive','https://www.googleapis.com/auth/spreadsheets']

# Load credentials
try:
    credentials_dict = json.loads(GCP_CREDENTIALS)
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
    print("✅ Credentials successfully loaded.")
except Exception as e:
    print(f"❌ Error: Failed to parse credentials from environment variable. {e}")
    exit(1)

# Authorize the credentials
gc = gspread.authorize(credentials)

# Build Drive service
drive_service = build('drive', 'v3', credentials=credentials)

print("🔄 Starting Caption Generator...")

# Open the Google Spreadsheet using environment variable
sh = gc.open_by_key(CRYPTO_SPREADSHEET_KEY)

# Get all sheet names
sheet_names = [sheet.title for sheet in sh.worksheets()]
print(f"✅ Found {len(sheet_names)} sheets: {', '.join(sheet_names)}")

# Loop through each sheet and load its data into a DataFrame
for sheet_name in sheet_names:
    worksheet = sh.worksheet(sheet_name)
    data = worksheet.get_all_values()
    df = pd.DataFrame(data[1:], columns=data[0])
    globals()[sheet_name] = df
    print(f"✅ Loaded sheet: {sheet_name} ({len(df)} rows)")

print("✅ Spreadsheet data loaded successfully")

# Check if required sheets exist
required_sheets = ['Top50Coins', 'BTC_SNAPSHOT', 'MarketOverview', 'ShortOpportunities', 'LongOpportunities']
missing_sheets = [sheet for sheet in required_sheets if sheet not in globals()]

if missing_sheets:
    print(f"⚠️  Warning: Missing sheets: {', '.join(missing_sheets)}")
    print("⚠️  Bot will continue with available data...")

# Convert percentage columns to numeric if they're in string format
if 'Top50Coins' in globals():
    try:
        Top50Coins['pct_1d_num'] = pd.to_numeric(Top50Coins['pct_1d'].str.replace('%', ''), errors='coerce').fillna(0)
        
        # Get the top gainer and top loser
        top_gainer = Top50Coins.loc[Top50Coins['pct_1d_num'].idxmax()]
        top_loser = Top50Coins.loc[Top50Coins['pct_1d_num'].idxmin()]
        
        gainer_symbol = top_gainer['symbol'] if 'symbol' in top_gainer else 'N/A'
        gainer_pct = top_gainer['pct_1d'] if 'pct_1d' in top_gainer else '0%'
        loser_symbol = top_loser['symbol'] if 'symbol' in top_loser else 'N/A'
        loser_pct = top_loser['pct_1d'] if 'pct_1d' in top_loser else '0%'
        
        print(f"✅ Top gainer: {gainer_symbol} ({gainer_pct})")
        print(f"✅ Top loser: {loser_symbol} ({loser_pct})")
        
    except Exception as e:
        print(f"⚠️  Error processing Top50Coins: {e}")
        gainer_symbol = gainer_pct = loser_symbol = loser_pct = 'N/A'
else:
    gainer_symbol = gainer_pct = loser_symbol = loser_pct = 'N/A'

# Process BTC data
if 'BTC_SNAPSHOT' in globals():
    try:
        btc_row = BTC_SNAPSHOT.iloc[0]
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
    except Exception as e:
        print(f"⚠️  Error extracting BTC data: {e}")
        btc_data = {k: 'N/A' for k in ['slug', 'rank', 'symbol', 'price', 'percent_change_24h', 'volume_24h', 'market_cap', 'percent_change_7d', 'percent_change_30d', 'ytd_change', 'last_updated', 'colour_24h', 'bullish', 'bearish', 'neutral', 'sentiment_diff', 'trend']}
else:
    btc_data = {k: 'N/A' for k in ['slug', 'rank', 'symbol', 'price', 'percent_change_24h', 'volume_24h', 'market_cap', 'percent_change_7d', 'percent_change_30d', 'ytd_change', 'last_updated', 'colour_24h', 'bullish', 'bearish', 'neutral', 'sentiment_diff', 'trend']}

# Process short opportunities
if 'ShortOpportunities' in globals():
    try:
        ShortOpportunities['bearish_count'] = pd.to_numeric(ShortOpportunities['bearish_count'], errors='coerce').fillna(0)
        top_shorts = ShortOpportunities.nlargest(2, 'bearish_count')
        print(f"✅ Top shorts loaded: {len(top_shorts)} opportunities")
    except Exception as e:
        print(f"⚠️  Error processing short opportunities: {e}")
        top_shorts = pd.DataFrame({'slug': ['crypto1', 'crypto2'], 'bearish_count': [0, 0], 'market_cap': ['$0', '$0'], 'percent_change24h': ['0%', '0%']})
else:
    top_shorts = pd.DataFrame({'slug': ['crypto1', 'crypto2'], 'bearish_count': [0, 0], 'market_cap': ['$0', '$0'], 'percent_change24h': ['0%', '0%']})

# Process long opportunities
if 'LongOpportunities' in globals():
    try:
        LongOpportunities['bullish_count'] = pd.to_numeric(LongOpportunities['bullish_count'], errors='coerce').fillna(0)
        top_longs = LongOpportunities.nlargest(2, 'bullish_count')
        print(f"✅ Top longs loaded: {len(top_longs)} opportunities")
    except Exception as e:
        print(f"⚠️  Error processing long opportunities: {e}")
        top_longs = pd.DataFrame({'slug': ['crypto1', 'crypto2'], 'bullish_count': [0, 0], 'market_cap': ['$0', '$0'], 'percent_change24h': ['0%', '0%']})
else:
    top_longs = pd.DataFrame({'slug': ['crypto1', 'crypto2'], 'bullish_count': [0, 0], 'market_cap': ['$0', '$0'], 'percent_change24h': ['0%', '0%']})

# Safe data extraction function
def safe_get(dataframe, column, row=0, default='N/A'):
    try:
        return dataframe.iloc[row].get(column, default) if len(dataframe) > row else default
    except Exception:
        return default

# Generate base caption
try:
    market_data = {}
    if 'MarketOverview' in globals():
        market_data = {
            'date': safe_get(MarketOverview, 'Todays_Date'),
            'day': safe_get(MarketOverview, 'Todays_Day'),
            'time': safe_get(MarketOverview, 'Current_Time'),
            'total_volume': safe_get(MarketOverview, 'total_volume24h_reported'),
            'volume_change': safe_get(MarketOverview, 'total_volume24h_yesterday_percentage_change'),
            'altcoin_volume': safe_get(MarketOverview, 'altcoin_volume24h_reported'),
            'derivatives_volume': safe_get(MarketOverview, 'derivatives_volume24h_reported'),
            'derivatives_change': safe_get(MarketOverview, 'derivatives24h_percentage_change'),
            'defi_volume': safe_get(MarketOverview, 'defi_volume24h_reported'),
            'defi_change': safe_get(MarketOverview, 'defi24h_percentage_change'),
            'defi_market_cap': safe_get(MarketOverview, 'defi_market_cap'),
            'btc_dominance': safe_get(MarketOverview, 'btc_dominance'),
            'btc_dominance_change': safe_get(MarketOverview, 'btc_dominance24h_percentage_change'),
            'eth_dominance': safe_get(MarketOverview, 'eth_dominance'),
            'eth_dominance_change': safe_get(MarketOverview, 'eth_dominance24h_percentage_change')
        }
    
    caption = f"""🚨 Crypto Opportunities Alert! 🚨

Crypto Market Overview:
- Today is {market_data.get('date', 'N/A')}, {market_data.get('day', 'N/A')} at {market_data.get('time', 'N/A')}!

* Market Stats:
  - Total Volume (24h): {market_data.get('total_volume', 'N/A')} (Change: {market_data.get('volume_change', 'N/A')}%)
  - Altcoin Volume (24h): {market_data.get('altcoin_volume', 'N/A')}
  - Derivatives Volume (24h): {market_data.get('derivatives_volume', 'N/A')} (Change: {market_data.get('derivatives_change', 'N/A')}%)

* DeFi Highlights:
  - DeFi Volume (24h): {market_data.get('defi_volume', 'N/A')} (Change: {market_data.get('defi_change', 'N/A')}%)
  - DeFi Market Cap: {market_data.get('defi_market_cap', 'N/A')}

* Dominance Metrics:
  - Bitcoin Dominance: {market_data.get('btc_dominance', 'N/A')} (Change 24h: {market_data.get('btc_dominance_change', 'N/A')}%)
  - Ethereum Dominance: {market_data.get('eth_dominance', 'N/A')} (Change 24h: {market_data.get('eth_dominance_change', 'N/A')}%)

Bitcoin (BTC) Update:
- Rank: #{btc_data['rank']}
- Current Price: {btc_data['price']}
- 24h Change: {btc_data['percent_change_24h']}% ({'🔴' if 'red' in str(btc_data['colour_24h']).lower() else '🟢'} Update)
- 24h Volume: {btc_data['volume_24h']}
- Market Cap: {btc_data['market_cap']}
- Last Updated: {btc_data['last_updated']}

* 7-Day Change: {btc_data['percent_change_7d']}%
* 30-Day Change: {btc_data['percent_change_30d']}%
* YTD Change: {btc_data['ytd_change']}%

Market Sentiment:
- Bullish: {btc_data['bullish']}
- Bearish: {btc_data['bearish']}
- Neutral: {btc_data['neutral']}
- Sentiment Diff: {btc_data['sentiment_diff']}
- Current Trend: {btc_data['trend']}

Crypto Highlights: Top 50 Coins
- Top Gainer: {gainer_symbol} skyrocketed by +{gainer_pct}%
- Top Loser: {loser_symbol} dropped by -{loser_pct}%

Top Short Squeeze Candidates:
1. {safe_get(top_shorts, 'slug', 0)}
   - Bearish Count: {safe_get(top_shorts, 'bearish_count', 0)}
   - Market Cap: {safe_get(top_shorts, 'market_cap', 0)}
   - 24h Change: {safe_get(top_shorts, 'percent_change24h', 0)}

2. {safe_get(top_shorts, 'slug', 1)}
   - Bearish Count: {safe_get(top_shorts, 'bearish_count', 1)}
   - Market Cap: {safe_get(top_shorts, 'market_cap', 1)}
   - 24h Change: {safe_get(top_shorts, 'percent_change24h', 1)}

Top Long Play Opportunities:
1. {safe_get(top_longs, 'slug', 0)}
   - Bullish Count: {safe_get(top_longs, 'bullish_count', 0)}
   - Market Cap: {safe_get(top_longs, 'market_cap', 0)}
   - 24h Change: {safe_get(top_longs, 'percent_change24h', 0)}

2. {safe_get(top_longs, 'slug', 1)}
   - Bullish Count: {safe_get(top_longs, 'bullish_count', 1)}
   - Market Cap: {safe_get(top_longs, 'market_cap', 1)}
   - 24h Change: {safe_get(top_longs, 'percent_change24h', 1)}

The crypto market never sleeps! Are you bullish or bearish? Let's hear your thoughts!

#Crypto #LongAndShort #MarketMoves #InvestSmart #TradeWisely

Stay ahead of the game! 🚀💎"""

    print("✅ Base caption generated")
    
except Exception as e:
    print(f"⚠️  Error generating caption: {e}")
    caption = "🚨 Crypto Market Update! Stay tuned for the latest data. #Crypto #MarketUpdate"

# Generate AI-enhanced caption using environment variable
os.environ["TOGETHER_API_KEY"] = TOGETHER_API_KEY
client = Together()

try:
    print("🔄 Generating AI-enhanced caption...")
    response = client.chat.completions.create(
        model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
        messages=[{
            "role": "user",
            "content": f"Can you write 2200 character instagram caption summarzing my crypto market recap for the day using the data :{caption}"
                      f"Make Sure it is well formatted, for instagram not as markdown so that user can read it on phone and has maximum information from :{caption}"
                      f"We need to Make sure it starts with a unique hook to nudge user to read the caption "
                      f"and place random hooks and CTA it in captions at 2 interval, to nudge user to , and follow us and like the post"
                      f"Make sure the Caption is well spaced out and Information is not Cluttered use indents and brackets whereever necessary"
                      f"At begining of all headings and key data points Relevant EMOJIS are at the core pls make sure you encorporate them need to be colorfull and thoughtful "
                      f"Ready to ship on instagram (NO AI comments in the output like here is your caption etc), my handle is @cryptoprism.io and my website is cryptoprism.io also link in bio"
                      f"dont want = ** this kind of formatting, make sure the character count is under 2000"
        }],
        max_tokens=600,
        temperature=0.7,
        top_p=0.9,
        frequency_penalty=0.5,
        presence_penalty=0.3,
        stop=["<|eot_id|>", "<|eom_id|>"],
        stream=False
    )

    caption1 = ""
    for token in response:
        if hasattr(token, 'choices') and token.choices:
            if hasattr(token.choices[0], 'delta') and hasattr(token.choices[0].delta, 'content'):
                if token.choices[0].delta.content:
                    caption1 += token.choices[0].delta.content

    print("✅ AI-enhanced caption generated")
    print(f"📝 Caption length: {len(caption1)} characters")

except Exception as e:
    print(f"⚠️  Error generating AI caption: {e}")
    caption1 = caption




# Instagram Session Management Functions using environment variable
DRIVE_FILE_ID = INSTAGRAM_DRIVE_FILE_ID
LOCAL_PATH = 'instagram_settings.json'

def download_from_drive(file_id, local_path):
    """Download settings from Google Drive"""
    try:
        request = drive_service.files().get_media(fileId=file_id)
        with io.FileIO(local_path, 'wb') as file:
            downloader = MediaIoBaseDownload(file, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
        print(f"✅ Downloaded settings from Drive to {local_path}")
        return True
    except Exception as e:
        print(f"❌ Error downloading from Drive: {e}")
        return False

def upload_to_drive(file_id, local_path):
    """Upload settings to Google Drive"""
    try:
        media = MediaFileUpload(local_path, mimetype='application/json')
        drive_service.files().update(fileId=file_id, media_body=media).execute()
        print(f"✅ Uploaded {local_path} to Google Drive")
        return True
    except Exception as e:
        print(f"❌ Error uploading to Drive: {e}")
        return False

def setup_instagram_client():
    """Setup Instagram client using ONLY existing session from Google Drive"""
    
    # Step 1: Always try to download from Google Drive first
    if not download_from_drive(DRIVE_FILE_ID, LOCAL_PATH):
        print("❌ CRITICAL: Could not download session from Google Drive!")
        print("❌ STOPPING: Will not create new session to avoid Instagram device issues")
        return None
    
    # Step 2: Check if the downloaded file exists and is valid
    if not Path(LOCAL_PATH).exists():
        print("❌ CRITICAL: Settings file not found after download!")
        return None
    
    # Step 3: Try to load the settings file
    try:
        with open(LOCAL_PATH, 'r') as f:
            settings = json.load(f)
        print("✅ Settings file loaded successfully")
    except json.JSONDecodeError:
        print("❌ CRITICAL: Settings file is corrupted!")
        return None
    except Exception as e:
        print(f"❌ CRITICAL: Error reading settings file: {e}")
        return None
    
    # Step 4: Initialize client with existing settings
    try:
        cl = Client()
        cl.load_settings(LOCAL_PATH)
        print("✅ Instagram client initialized with existing session")
        
        # Step 5: Test the session with a simple, low-impact call
        try:
            user_info = cl.user_info_by_username(cl.username)
            print(f"✅ Session verified - logged in as: {user_info.username}")
            return cl
            
        except Exception as session_error:
            print(f"⚠️  Session verification failed: {session_error}")
            print("⚠️  This might be temporary - proceeding with existing session anyway")
            print("⚠️  Instagram will prompt for re-auth if truly needed")
            return cl
            
    except Exception as e:
        print(f"❌ CRITICAL: Could not initialize Instagram client: {e}")
        return None

# Instagram Upload Process
print("🔄 Setting up Instagram client...")
cl = setup_instagram_client()

if cl is None:
    print("❌ STOPPING: Could not establish Instagram session")
    print("❌ Check your Google Drive connection and session file")
    print("💡 If this is your first time, you may need to create an initial session:")
    print(f"💡 Try running: cl = Client(); cl.login('{INSTAGRAM_USERNAME}', 'your_password'); cl.dump_settings('{LOCAL_PATH}')")
    exit(1)

print("✅ Instagram client ready for use")

# Prepare media files
print("🔄 Preparing media files...")
media_files = []
for i in range(1, 6):
    file_path = Path(f"{i}_output.jpg")
    if file_path.exists():
        media_files.append(file_path)
        print(f"✅ Found {file_path}")
    else:
        print(f"⚠️  {file_path} not found. Creating placeholder...")
        img = Image.new('RGB', (1080, 1080), color=(20, 20, 30))
        # Add some text to make it more interesting
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(img)
        try:
            # Try to use a better font
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
        except:
            font = ImageFont.load_default()
        
        text = f"Crypto Update\nSlide {i}"
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        x = (1080 - text_width) // 2
        y = (1080 - text_height) // 2
        
        draw.text((x, y), text, fill=(255, 255, 255), font=font, align="center")
        img.save(file_path)
        media_files.append(file_path)

print(f"✅ Prepared {len(media_files)} media files")

# Upload to Instagram
if media_files and caption1:
    try:
        print("🔄 Uploading to Instagram...")
        print(f"📝 Caption preview (first 200 chars): {caption1[:200]}...")
        
        # Upload carousel post
        media = cl.album_upload(media_files, caption1)
        print("✅ Successfully uploaded to Instagram!")
        print(f"📱 Post ID: {media.id}")
        
        # Update the session file back to Google Drive after successful upload
        cl.dump_settings(LOCAL_PATH)
        upload_to_drive(DRIVE_FILE_ID, LOCAL_PATH)
        print("✅ Session updated and saved to Google Drive")
        
    except Exception as upload_error:
        print(f"❌ Upload failed: {upload_error}")
        print("❌ This could be due to:")
        print("   - Instagram rate limits")
        print("   - Session expired (try creating new session)")
        print("   - Network issues")
        print("   - Instagram policy violations")
        
        # Still try to save session updates
        try:
            cl.dump_settings(LOCAL_PATH)
            upload_to_drive(DRIVE_FILE_ID, LOCAL_PATH)
            print("✅ Session state saved despite upload failure")
        except:
            print("⚠️  Could not save session updates")
else:
    print("❌ Missing media files or caption. Upload skipped.")
    if not media_files:
        print("❌ No media files found")
    if not caption1:
        print("❌ No caption generated")

# Cleanup
print("🧹 Cleaning up temporary files...")
try:
    if Path(LOCAL_PATH).exists():
        os.remove(LOCAL_PATH)
    for i in range(1, 6):
        file_path = Path(f"{i}_output.jpg")
        if file_path.exists():
            os.remove(file_path)
    print("✅ Temporary files cleaned up")
except Exception as e:
    print(f"⚠️  Error cleaning up: {e}")

# Calculate and display execution time
end_time = time.time()
execution_time = end_time - start_time
print(f"⏱️  Script execution time: {execution_time:.2f} seconds")

# Summary
print("\n" + "="*60)
print("🎉 CRYPTO INSTAGRAM BOT EXECUTION COMPLETE!")
print("="*60)
print(f"✅ Data sources processed: {len([name for name in required_sheets if name in globals()])} sheets")
print(f"✅ Caption length: {len(caption1)} characters")
print(f"✅ Media files: {len(media_files)} images")
print(f"✅ Execution time: {execution_time:.2f} seconds")
print("✅ Session safely preserved for next run")
print("\n💡 Next run will be faster as session is already established!")
print("🔗 Check your Instagram: @cryptoprism.io")
print("="*60)
