

 #prompt: write a code for collecting start time and end time and then the difference , in 3 lines
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

# Convert percentage columns to numeric if they're in string format
Top50Coins['pct_1d_num'] = Top50Coins['pct_1d'].str.replace('%', '').astype(float)

# Get the top gainer and top loser
top_gainer = Top50Coins.loc[Top50Coins['pct_1d_num'].idxmax()]
top_loser = Top50Coins.loc[Top50Coins['pct_1d_num'].idxmin()]

# Extract necessary information
gainer_symbol = top_gainer['symbol']
gainer_pct = top_gainer['pct_1d']
loser_symbol = top_loser['symbol']
loser_pct = top_loser['pct_1d']


import pandas as pd

# Assuming BTC_SNAPSHOT is your DataFrame for Bitcoin
btc_row = BTC_SNAPSHOT.iloc[0]

# Extract necessary information
btc_slug = btc_row['slug']
btc_rank = btc_row['cmc_rank']
btc_symbol = btc_row['symbol']
btc_price = btc_row['price']
btc_percent_change_24h = btc_row['percent_change24h']
btc_volume_24h = btc_row['volume24h']
btc_market_cap = btc_row['market_cap']
btc_percent_change_7d = btc_row['percent_change7d']
btc_percent_change_30d = btc_row['percent_change30d']
btc_ytd_change = btc_row['ytd_price_change_percentage']
btc_last_updated = btc_row['last_updated']
btc_colour_24h = btc_row['colour_percent_change24h']
btc_bullish = btc_row['bullish']
btc_bearish = btc_row['bearish']
btc_neutral = btc_row['neutral']
btc_sentiment_diff = btc_row['sentiment_diff']
btc_trend = btc_row['Trend']

# Convert 'bearish_count' column to numeric
ShortOpportunities['bearish_count'] = pd.to_numeric(ShortOpportunities['bearish_count'])

# Get top 2 short opportunities based on bearish count
top_shorts = ShortOpportunities.nlargest(2, 'bearish_count')


LongOpportunities['bullish_count'] = pd.to_numeric(LongOpportunities['bullish_count'])

# Get top 2 long opportunities based on bullish count
top_longs = LongOpportunities.nlargest(2, 'bullish_count')

# Generate Instagram Caption with bullet points
caption = f"""

🚨 Crypto Opportunities Alert! 🚨

Crypto Market Overview:
- Today is {MarketOverview['Todays_Date'][0]}, {MarketOverview['Todays_Day'][0]} at {MarketOverview['Current_Time'][0]}!

* Market Stats:
  - Total Volume (24h): {MarketOverview['total_volume24h_reported'][0]} (Change: {MarketOverview['total_volume24h_yesterday_percentage_change'][0]}%)
  - Altcoin Volume (24h): {MarketOverview['altcoin_volume24h_reported'][0]}
  - Derivatives Volume (24h): {MarketOverview['derivatives_volume24h_reported'][0]} (Change: {MarketOverview['derivatives24h_percentage_change'][0]}%)

* DeFi Highlights:
  - DeFi Volume (24h): {MarketOverview['defi_volume24h_reported'][0]} (Change: {MarketOverview['defi24h_percentage_change'][0]}%)
  - DeFi Market Cap: {MarketOverview['defi_market_cap'][0]}

* Dominance Metrics:
  - Bitcoin Dominance: {MarketOverview['btc_dominance'][0]} (Change 24h: {MarketOverview['btc_dominance24h_percentage_change'][0]}%)
  - Ethereum Dominance: {MarketOverview['eth_dominance'][0]} (Change 24h: {MarketOverview['eth_dominance24h_percentage_change'][0]}%)

Bitcoin (BTC) Update:
- Rank: #{btc_rank}
- Current Price: {btc_price}
- 24h Change: {btc_percent_change_24h}% ({'🔴' if btc_colour_24h == 'red' else '🟢'} Update)
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
1. {top_shorts.iloc[0]['slug']}
   - Bearish Count: {top_shorts.iloc[0]['bearish_count']}
   - Market Cap: {top_shorts.iloc[0]['market_cap']}
   - 24h Change: {top_shorts.iloc[0]['percent_change24h']}

2. {top_shorts.iloc[1]['slug']}
   - Bearish Count: {top_shorts.iloc[1]['bearish_count']}
   - Market Cap: {top_shorts.iloc[1]['market_cap']}
   - 24h Change: {top_shorts.iloc[1]['percent_change24h']}

Top Long Play Opportunities:
1. {top_longs.iloc[0]['slug']}
   - Bullish Count: {top_longs.iloc[0]['bullish_count']}
   - Market Cap: {top_longs.iloc[0]['market_cap']}
   - 24h Change: {top_longs.iloc[0]['percent_change24h']}

2. {top_longs.iloc[1]['slug']}
   - Bullish Count: {top_longs.iloc[1]['bullish_count']}
   - Market Cap: {top_longs.iloc[1]['market_cap']}
   - 24h Change: {top_longs.iloc[1]['percent_change24h']}

The crypto market never sleeps! Are you bullish or bearish? Let’s hear your thoughts!

#Crypto #LongAndShort #MarketMoves #InvestSmart #TradeWisely

Stay ahead of the game! 🚀💎
"""

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
 #Initialize an empty string to store the output
caption1 = ""

for token in response:
    if hasattr(token, 'choices'):
        caption1 += token.choices[0].delta.content  # Append each token's content to caption1

# Now caption1 contains the complete output
print(caption1)  # Display the generated caption


"""# Instagram Bot"""

#!pip install instagrapi

import json
drive_service = build('drive', 'v3', credentials=credentials)

# List files
files = drive_service.files().list(pageSize=10).execute().get('files', [])
for file in files:
    print(file['name'], file['id'])

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
    media = MediaFileUpload(local_path, mimetype='application/json')
    drive_service.files().update(fileId=file_id, media_body=media).execute()
    print(f"Uploaded {local_path} to Google Drive")

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

media_files = [
    Path("1_output.jpg"),
    Path("2_output.jpg"),
    Path("3_output.jpg"),
    Path("4_output.jpg"),
    Path("5_output.jpg")
]


# Define the caption for your carousel post
caption = caption
# Upload the carousel post
media = cl.album_upload(media_files, caption1)

# Print the media IDs of the uploaded post
print("suceesfully uploaded")
