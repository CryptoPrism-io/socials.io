# prompt: write a code for collecting start time and end time and then the difference , in 3 lines
import time

start_time = time.time()

import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
import os
import json
import gspread

# Load the Google credentials JSON from the environment variable
gcp_credentials_json = os.getenv('GCP_CREDENTIALS')

# Define the scope
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive','https://www.googleapis.com/auth/spreadsheets']


# Ensure the environment variable is set
if gcp_credentials_json:
    try:
        # Load credentials from the environment variable JSON
        credentials_dict = json.loads(gcp_credentials_json)
        credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
        print("Credentials successfully loaded.")
    except Exception as e:
        print(f"Error: Failed to parse credentials from environment variable. {e}")
        exit(1)
else:
    print("Error: GCP_CREDENTIALS environment variable is not set.")
    exit(1)

# Authorize the credentials
gc = gspread.authorize(credentials)

"""## Caption Generator"""
print("caption gen")

# Google Spreadsheet details
spreadsheet_key = '1Ppif1y284fLPVIIoRzAXbPi9eUXzAyjOBr5DR-6XjSM'  # Replace with your spreadsheet key

# Open the Google Spreadsheet
sh = gc.open_by_key(spreadsheet_key)

# Get all sheet names
sheet_names = [sheet.title for sheet in sh.worksheets()]

# Loop through each sheet and load its data into a DataFrame
for sheet_name in sheet_names:
    worksheet = sh.worksheet(sheet_name)
    data = worksheet.get_all_values()  # Fetch all data from the sheet
    df = pd.DataFrame(data[1:], columns=data[0])  # Convert to DataFrame with headers
    globals()[sheet_name] = df  # Store DataFrame in a variable with the sheet name

# Convert percentage columns to numeric if they're in string format - FIXED VERSION
Top50Coins['pct_1d_num'] = pd.to_numeric(Top50Coins['pct_1d'].str.replace('%', ''), errors='coerce').fillna(0)

# Get the top gainer and top loser - FIXED VERSION
try:
    top_gainer = Top50Coins.loc[Top50Coins['pct_1d_num'].idxmax()]
    top_loser = Top50Coins.loc[Top50Coins['pct_1d_num'].idxmin()]
except Exception as e:
    print(f"Error finding top gainer/loser: {e}")
    # Fallback values
    top_gainer = Top50Coins.iloc[0]
    top_loser = Top50Coins.iloc[1]

# Extract necessary information
gainer_symbol = top_gainer['symbol'] if 'symbol' in top_gainer else 'N/A'
gainer_pct = top_gainer['pct_1d'] if 'pct_1d' in top_gainer else '0%'
loser_symbol = top_loser['symbol'] if 'symbol' in top_loser else 'N/A'
loser_pct = top_loser['pct_1d'] if 'pct_1d' in top_loser else '0%'

import pandas as pd

# Assuming BTC_SNAPSHOT is your DataFrame for Bitcoin - FIXED VERSION
try:
    btc_row = BTC_SNAPSHOT.iloc[0]
    
    # Extract necessary information with safe fallbacks
    btc_slug = btc_row.get('slug', 'bitcoin')
    btc_rank = btc_row.get('cmc_rank', '1')
    btc_symbol = btc_row.get('symbol', 'BTC')
    btc_price = btc_row.get('price', '$0.00')
    btc_percent_change_24h = btc_row.get('percent_change24h', '0%')
    btc_volume_24h = btc_row.get('volume24h', '$0')
    btc_market_cap = btc_row.get('market_cap', '$0')
    btc_percent_change_7d = btc_row.get('percent_change7d', '0%')
    btc_percent_change_30d = btc_row.get('percent_change30d', '0%')
    btc_ytd_change = btc_row.get('ytd_price_change_percentage', '0%')
    btc_last_updated = btc_row.get('last_updated', 'N/A')
    btc_colour_24h = btc_row.get('colour_percent_change24h', 'green')
    btc_bullish = btc_row.get('bullish', '0')
    btc_bearish = btc_row.get('bearish', '0')
    btc_neutral = btc_row.get('neutral', '0')
    btc_sentiment_diff = btc_row.get('sentiment_diff', '0')
    btc_trend = btc_row.get('Trend', 'Neutral')
    
except Exception as e:
    print(f"Error extracting BTC data: {e}")
    # Fallback values
    btc_slug = 'bitcoin'
    btc_rank = '1'
    btc_symbol = 'BTC'
    btc_price = '$0.00'
    btc_percent_change_24h = '0%'
    btc_volume_24h = '$0'
    btc_market_cap = '$0'
    btc_percent_change_7d = '0%'
    btc_percent_change_30d = '0%'
    btc_ytd_change = '0%'
    btc_last_updated = 'N/A'
    btc_colour_24h = 'green'
    btc_bullish = '0'
    btc_bearish = '0'
    btc_neutral = '0'
    btc_sentiment_diff = '0'
    btc_trend = 'Neutral'

# Convert 'bearish_count' column to numeric - FIXED VERSION
try:
    ShortOpportunities['bearish_count'] = pd.to_numeric(ShortOpportunities['bearish_count'], errors='coerce').fillna(0)
    # Get top 2 short opportunities based on bearish count
    top_shorts = ShortOpportunities.nlargest(2, 'bearish_count')
except Exception as e:
    print(f"Error processing short opportunities: {e}")
    # Create fallback data
    top_shorts = pd.DataFrame({
        'slug': ['crypto1', 'crypto2'],
        'bearish_count': [0, 0],
        'market_cap': ['$0', '$0'],
        'percent_change24h': ['0%', '0%']
    })

# Convert 'bullish_count' column to numeric - FIXED VERSION
try:
    LongOpportunities['bullish_count'] = pd.to_numeric(LongOpportunities['bullish_count'], errors='coerce').fillna(0)
    # Get top 2 long opportunities based on bullish count
    top_longs = LongOpportunities.nlargest(2, 'bullish_count')
except Exception as e:
    print(f"Error processing long opportunities: {e}")
    # Create fallback data
    top_longs = pd.DataFrame({
        'slug': ['crypto1', 'crypto2'],
        'bullish_count': [0, 0],
        'market_cap': ['$0', '$0'],
        'percent_change24h': ['0%', '0%']
    })

# Safe data extraction function
def safe_get(dataframe, column, row=0, default='N/A'):
    try:
        return dataframe.iloc[row].get(column, default) if len(dataframe) > row else default
    except Exception:
        return default

# Generate Instagram Caption with bullet points - FIXED VERSION
try:
    caption = f"""

🚨 Crypto Opportunities Alert! 🚨

Crypto Market Overview:
- Today is {safe_get(MarketOverview, 'Todays_Date')}, {safe_get(MarketOverview, 'Todays_Day')} at {safe_get(MarketOverview, 'Current_Time')}!

* Market Stats:
  - Total Volume (24h): {safe_get(MarketOverview, 'total_volume24h_reported')} (Change: {safe_get(MarketOverview, 'total_volume24h_yesterday_percentage_change')}%)
  - Altcoin Volume (24h): {safe_get(MarketOverview, 'altcoin_volume24h_reported')}
  - Derivatives Volume (24h): {safe_get(MarketOverview, 'derivatives_volume24h_reported')} (Change: {safe_get(MarketOverview, 'derivatives24h_percentage_change')}%)

* DeFi Highlights:
  - DeFi Volume (24h): {safe_get(MarketOverview, 'defi_volume24h_reported')} (Change: {safe_get(MarketOverview, 'defi24h_percentage_change')}%)
  - DeFi Market Cap: {safe_get(MarketOverview, 'defi_market_cap')}

* Dominance Metrics:
  - Bitcoin Dominance: {safe_get(MarketOverview, 'btc_dominance')} (Change 24h: {safe_get(MarketOverview, 'btc_dominance24h_percentage_change')}%)
  - Ethereum Dominance: {safe_get(MarketOverview, 'eth_dominance')} (Change 24h: {safe_get(MarketOverview, 'eth_dominance24h_percentage_change')}%)

Bitcoin (BTC) Update:
- Rank: #{btc_rank}
- Current Price: {btc_price}
- 24h Change: {btc_percent_change_24h}% ({'🔴' if 'red' in str(btc_colour_24h).lower() else '🟢'} Update)
- 24h Volume: {btc_volume_24h}
- Market Cap: {btc_market_cap}
- Last Updated: {btc_last_updated}

* 7-Day Change: {btc_percent_change_7d}%
* 30-Day Change: {btc_percent_change_30d}%
* YTD Change: {btc_ytd_change}%

Market Sentiment:
- Bullish: {btc_bullish}
- Bearish: {btc_bearish}
- Neutral: {btc_neutral}
- Sentiment Diff: {btc_sentiment_diff}
- Current Trend: {btc_trend}

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

Stay ahead of the game! 🚀💎
"""
except Exception as e:
    print(f"Error generating caption: {e}")
    caption = "🚨 Crypto Market Update! Stay tuned for the latest data. #Crypto #MarketUpdate"

print(caption)

# Install the necessary library
#!pip install together

# @title Caption Generator LLM

import os
import requests
from together import Together
from PIL import Image
import io
import base64

# Set your Together API key (replace with your actual key)
os.environ["TOGETHER_API_KEY"] = "3fe68043428d4e823a69fa534f0ee3cb8a355ff265fd9afba5ff5c48f7a7dc03" # Replace with your actual API key

client = Together()

try:
    response = client.chat.completions.create(
        model="google/gemma-2-27b-it",
        messages=[  {
                    "role": "user",
                    "content": f"Can you write 2200 character instagram caption summarzing my crypto market recap for the day using the data :{caption}"
                    f"Make Sure it is well formatted, for instagram not as markdown so that user can read it on phone and has maximum information from :{caption}"
                    f"We need to Make sure it starts with a FOMO hook  to nudge user to read the caption "
                    f"and place random hooks and CTA it in captions at regular interval, to nudge user to , and follow us and like the post"
                    f"Make sure the Caption is well spaced out and INformation is not Cluttered use indents and brackets whereever necessary"
                    f"At begining of all headings and key data points Relevant Emojis are at the core pls make sure you encorporate them need to be colorfull and thoughtful "
                    f"Ready to ship on instagram (NO AI comments in the output like here is your caption etc), my handle is @cryptoprism.io and my website is cryptoprism.io also link in bio"
                    f"**-dont want this kind of formatting make sure the character count is under 2000"
            }],
        max_tokens= 1600,
        temperature=1,
        top_p=0.5,
        top_k=50,
        repetition_penalty=0.88,
        stop=["<|eot_id|>","<|eom_id|>"],
        stream=True
    )
    
    # Initialize an empty string to store the output
    caption1 = ""

    for token in response:
        if hasattr(token, 'choices') and token.choices:
            if hasattr(token.choices[0], 'delta') and hasattr(token.choices[0].delta, 'content'):
                if token.choices[0].delta.content:
                    caption1 += token.choices[0].delta.content  # Append each token's content to caption1

    # Now caption1 contains the complete output
    print(caption1)  # Display the generated caption

except Exception as e:
    print(f"Error generating AI caption: {e}")
    caption1 = caption  # Fallback to original caption

"""# Instagram Bot"""

#!pip install instagrapi

import json

try:
    drive_service = build('drive', 'v3', credentials=credentials)

    # List files
    files = drive_service.files().list(pageSize=10).execute().get('files', [])
    for file in files:
        print(file['name'], file['id'])
except Exception as e:
    print(f"Error accessing Google Drive: {e}")

try:
    from googleapiclient.http import MediaIoBaseDownload
    import io
    
    # Replace with the desired file ID (from the printed list)
    file_id = '1u1jr50hhm-9IJUjvYsZ7mEeGMSgLI8hv'
    file_name = 'instagram_settings.json'  # Name to save the downloaded file

    # Download the file
    request = drive_service.files().get_media(fileId=file_id)
    with io.FileIO(file_name, 'wb') as file:
        downloader = MediaIoBaseDownload(file, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            print(f"Download {int(status.progress() * 100)}% complete.")

    print(f"File downloaded as {file_name}")

    # Load the downloaded file content into a variable
    with open(file_name, 'r') as f:
        instagram_login = json.load(f)

    # Print or use the variable
    print(instagram_login)
    
except Exception as e:
    print(f"Error downloading Instagram settings: {e}")
    instagram_login = {}

try:
    from instagrapi import Client
    from pathlib import Path
    import os
    import io
    import json
    from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload

    # Define paths
    DRIVE_FILE_ID = '1u1jr50hhm-9IJUjvYsZ7mEeGMSgLI8hv'  # Replace with your file ID
    LOCAL_PATH = 'instagram_settings.json'

    # Function to download settings from Google Drive
    def download_from_drive(file_id, local_path):
        request = drive_service.files().get_media(fileId=file_id)
        with io.FileIO(local_path, 'wb') as file:
            downloader = MediaIoBaseDownload(file, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
                print(f"Download {int(status.progress() * 100)}% complete.")

    # Function to upload settings to Google Drive
    def upload_to_drive(file_id, local_path):
        try:
            media = MediaFileUpload(local_path, mimetype='application/json')
            drive_service.files().update(fileId=file_id, media_body=media).execute()
            print(f"Uploaded {local_path} to Google Drive")
        except Exception as e:
            print(f"Error uploading to Drive: {e}")



# previous code ---------------------------
"""
    try:
        # Download settings from Drive if they exist
        download_from_drive(DRIVE_FILE_ID, LOCAL_PATH)
        print("Downloaded existing settings from Drive")

        # Load existing settings and verify session
        cl = Client()
        cl.load_settings(LOCAL_PATH)
        cl.get_timeline_feed()  # Verify session is still valid
        print("Successfully loaded existing session")

    except Exception as e:
        print("Creating new session...")
        cl = Client()
        cl.login("cryptoprism.io", "jaimaakamakhya")
        cl.dump_settings(LOCAL_PATH)

        # Upload new settings to Drive
        upload_to_drive(DRIVE_FILE_ID, LOCAL_PATH)
        print(f"New session created and uploaded to Drive")

    print("Session is ready to use")
"""




        try:
        # Download settings from Drive if they exist
        download_from_drive(DRIVE_FILE_ID, LOCAL_PATH)
        print("Downloaded existing settings from Drive")

        # Load existing settings and verify session
        cl = Client()
        cl.load_settings(LOCAL_PATH)
        cl.get_timeline_feed()  # Verify session is still valid
        print("Successfully loaded existing session")

    except Exception as e:
        print("Session invalid or expired! Aborting without creating a new session.")
        raise RuntimeError("Instagram session invalid or expired. Manual intervention required.")

    # Check if media files exist, create dummy files if they don't
    media_files = []
    for i in range(1, 6):
        file_path = Path(f"{i}_output.jpg")
        if file_path.exists():
            media_files.append(file_path)
        else:
            print(f"Warning: {file_path} not found. Creating placeholder...")
            # Create a simple placeholder image if file doesn't exist
            from PIL import Image
            img = Image.new('RGB', (1080, 1080), color='black')
            img.save(file_path)
            media_files.append(file_path)

    # Upload the carousel post
    if media_files and caption1:
        try:
            media = cl.album_upload(media_files, caption1)
            print("Successfully uploaded to Instagram!")
        except Exception as e:
            print(f"Error uploading to Instagram: {e}")
    else:
        print("Missing media files or caption. Upload skipped.")

except Exception as e:
    print(f"Error with Instagram upload process: {e}")

# Calculate and display execution time
end_time = time.time()
execution_time = end_time - start_time
print(f"Script execution time: {execution_time:.2f} seconds")
