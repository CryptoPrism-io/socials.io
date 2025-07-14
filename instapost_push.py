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

# Clean Caption Generation with Character Limit Management
def safe_get(dataframe, column, row=0, default='N/A'):
    """Safely extract data from DataFrame"""
    try:
        if len(dataframe) > row and column in dataframe.columns:
            value = dataframe.iloc[row][column]
            return str(value).strip() if pd.notna(value) and str(value).strip() else default
        return default
    except Exception:
        return default

def truncate_caption(text, max_length=2200):
    """Truncate caption to fit character limit"""
    if len(text) <= max_length:
        return text
    
    # Find last complete line within limit
    truncated = text[:max_length]
    last_newline = truncated.rfind('\n')
    if last_newline > max_length * 0.8:
        return truncated[:last_newline]
    
    # Find last sentence
    for punct in ['. ', '! ', '? ']:
        last_punct = truncated.rfind(punct)
        if last_punct > max_length * 0.8:
            return truncated[:last_punct + len(punct)]
    
    return truncated[:truncated.rfind(' ')] + '...'

def generate_base_caption():
    """Generate base caption with error handling"""
    try:
        # Get market data
        market_data = {}
        if 'MarketOverview' in globals():
            market_data = {
                'date': safe_get(MarketOverview, 'Todays_Date'),
                'total_volume': safe_get(MarketOverview, 'total_volume24h_reported'),
                'volume_change': safe_get(MarketOverview, 'total_volume24h_yesterday_percentage_change'),
                'btc_dominance': safe_get(MarketOverview, 'btc_dominance'),
                'eth_dominance': safe_get(MarketOverview, 'eth_dominance')
            }
        
        # Build caption sections
        sections = ["🚨 Crypto Alert! Market Never Sleeps 🚨\n"]
        
        # Market overview
        if market_data.get('date', 'N/A') != 'N/A':
            sections.extend([
                f"📅 {market_data['date']}",
                f"💰 Volume: {market_data['total_volume']} ({market_data['volume_change']}%)",
                f"₿ BTC Dom: {market_data['btc_dominance']}% | Ⓔ ETH Dom: {market_data['eth_dominance']}%\n"
            ])
        
        # Bitcoin data
        if btc_data.get('price', 'N/A') != 'N/A':
            trend_emoji = '🔴' if 'red' in str(btc_data.get('colour_24h', '')).lower() else '🟢'
            sections.extend([
                f"₿ BITCOIN UPDATE {trend_emoji}",
                f"Price: {btc_data['price']} ({btc_data['percent_change_24h']}%)",
                f"Volume: {btc_data['volume_24h']}",
                f"Market Cap: {btc_data['market_cap']}\n"
            ])
        
        # Top movers
        if gainer_symbol != 'N/A':
            sections.extend([
                "📈 TOP MOVERS (24H)",
                f"🚀 Best: {gainer_symbol} +{gainer_pct}%",
                f"📉 Worst: {loser_symbol} {loser_pct}%\n"
            ])
        
        # Trading opportunities
        if len(top_shorts) > 0:
            sections.append("🔻 SHORT OPPORTUNITIES:")
            for i in range(min(2, len(top_shorts))):
                coin = safe_get(top_shorts, 'slug', i)
                bearish = safe_get(top_shorts, 'bearish_count', i)
                sections.append(f"• {coin} (Bearish: {bearish})")
        
        if len(top_longs) > 0:
            sections.append("\n🔺 LONG OPPORTUNITIES:")
            for i in range(min(2, len(top_longs))):
                coin = safe_get(top_longs, 'slug', i)
                bullish = safe_get(top_longs, 'bullish_count', i)
                sections.append(f"• {coin} (Bullish: {bullish})")
        
        # Engagement & hashtags
        sections.extend([
            "\n💎 What's your move? Drop your thoughts! 👇",
            "Follow @cryptoprism.io for daily insights!",
            "\n#Crypto #Bitcoin #Trading #MarketUpdate #CryptoPrism #BullishOrBearish"
        ])
        
        caption = '\n'.join(sections)
        return truncate_caption(caption, 2200)
        
    except Exception as e:
        print(f"⚠️ Error generating base caption: {e}")
        return "🚨 Crypto Market Update! 📈\n\nDaily market analysis coming your way.\n\n#Crypto #MarketUpdate #CryptoPrism"

def generate_ai_caption(base_caption):
    """Generate AI-enhanced caption with fallback"""
    if not TOGETHER_API_KEY:
        print("⚠️ No AI API key, using base caption")
        return base_caption
    
    try:
        client = Together(api_key=TOGETHER_API_KEY)
        
        prompt = f"""Create a 1900-character Instagram caption from this crypto data:

{base_caption}

Rules:
- MAX 1900 characters (strict)
- Hook opening line
- Mobile-friendly format
- Strategic emojis
- Include @cryptoprism.io mention
- 2-3 engagement CTAs
- End with hashtags
- NO markdown formatting
- NO "Here's your caption" responses

Make it engaging and scroll-stopping!"""

        response = client.chat.completions.create(
            model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.7
        )
        
        ai_caption = response.choices[0].message.content.strip()
        
        # Clean AI commentary
        lines = [line.strip() for line in ai_caption.split('\n') 
                if line.strip() and not any(phrase in line.lower() 
                for phrase in ['here is', 'here\'s', 'caption:'])]
        
        ai_caption = '\n'.join(lines)
        ai_caption = truncate_caption(ai_caption, 2000)
        
        if len(ai_caption) > 100:
            print(f"✅ AI caption generated ({len(ai_caption)} chars)")
            return ai_caption
        else:
            print("⚠️ AI caption too short, using base")
            return base_caption
            
    except Exception as e:
        print(f"⚠️ AI generation failed: {e}")
        return base_caption

# Replace your caption generation section with this:
print("🔄 Generating caption...")

# Generate base caption
base_caption = generate_base_caption()
print(f"✅ Base caption: {len(base_caption)} characters")

# Generate AI-enhanced version
caption1 = generate_ai_caption(base_caption)
print(f"✅ Final caption: {len(caption1)} characters")

# Ensure we have a caption
if not caption1 or len(caption1) < 50:
    caption1 = base_caption
    print("⚠️ Using base caption as fallback")



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
