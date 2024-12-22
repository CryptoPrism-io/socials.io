import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Load the Google credentials JSON from the environment variable
gcp_credentials_json = os.getenv('GCP_CREDENTIALS')

# Define the required scope for Google Sheets API
scope = ['https://spreadsheets.google.com/feeds']

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


# @title library and aws con
import pandas as pd
import numpy as np
import mysql.connector
import gspread
import psycopg2

 # Connect to PostgreSQL database
con = psycopg2.connect(
        host="34.55.195.199",
        database="dbcp",
        user="yogass09",
        password="jaimaakamakhya",
        port=5432
    )

# prompt: using con can you give me a list of all the tab;es

import pandas as pd

# Execute a query to get a list of tables
with con.cursor() as cur:
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
    tables = cur.fetchall()

# Convert the list of tuples to a list of strings
table_names = [table[0] for table in tables]

# Print the list of table names
table_names

"""# Top 50//Sheet 1"""

# @title Fetch for Top 50 coins

query_top_100 = """
SELECT slug, cmc_rank, last_updated, symbol, price, percent_change24h, market_cap, last_updated
FROM crypto_listings_latest_1000
WHERE cmc_rank < 50
"""
top_100_cc  = pd.read_sql_query(query_top_100, con)

# Create a list of slugs from the top_100_crypto DataFrame
slugs = top_100_cc['slug'].tolist()
# Prepare a string for the IN clause
slugs_placeholder = ', '.join(f"'{slug}'" for slug in slugs)

# Construct the SQL query
query = f"""
SELECT logo, slug FROM "FE_CC_INFO_URL"
"""

# Execute the query and fetch the data into a DataFrame
logos_and_slugs = pd.read_sql_query(query, con)

# Merge the two DataFrames on the 'slug' column
df_top_100_daily = pd.merge(top_100_cc, logos_and_slugs, on='slug', how='left')

"""SORTING"""

# @title decimals for price and pct
import pandas as pd

# Convert 'price' column to numeric, handling potential errors
df_top_100_daily['price'] = pd.to_numeric(df_top_100_daily['price'], errors='coerce')

# Format the 'price' column with '$' and 2 decimal places
df_top_100_daily['price_usd'] = df_top_100_daily['price'].apply(lambda x: f"${x:.2f}" if not pd.isnull(x) else x)

# Convert 'percent_change24h' column to numeric, handling potential errors
df_top_100_daily['percent_change24h'] = pd.to_numeric(df_top_100_daily['percent_change24h'], errors='coerce')

# Format the 'percent_change24h' column with 2 decimal places and add '%'
df_top_100_daily['pct_1d'] = df_top_100_daily['percent_change24h'].apply(lambda x: f"{x:.2f}%" if not pd.isnull(x) else x)

"""Color Code for Metrics"""

# @title Color Code for Top 50
# Add a new column based on the value of 'percent_change24h'
df_top_100_daily['colour'] = df_top_100_daily['percent_change24h'].apply(
    lambda x: '/#8DFF7E' if x > 0 else '/#FF726D'
)

# @title  Mcap color
import pandas as pd

def format_market_cap(market_cap):
    """Formats market cap with units (Million, Billion, Trillion)."""
    if pd.isnull(market_cap):
        return market_cap
    market_cap = float(market_cap)
    if market_cap >= 1e12:
        return f"${market_cap / 1e12:.2f} T"
    elif market_cap >= 1e9:
        return f"${market_cap / 1e9:.2f} B"
    elif market_cap >= 1e6:
        return f"${market_cap / 1e6:.2f} M"
    else:
        return f"${market_cap:.2f}"

# Apply the formatting function to the 'market_cap' column
df_top_100_daily['mcap_units'] = df_top_100_daily['market_cap'].apply(format_market_cap)

# Select specific columns from the DataFrame
df_gsheet  = df_top_100_daily[['logo','slug', 'cmc_rank', 'price_usd', 'pct_1d', 'mcap_units', 'symbol', 'colour',"last_updated"]]

# prompt: with df_gsheet can you put the coloum cmc_rank as ascending
df_gsheet = df_gsheet.sort_values('cmc_rank', ascending=True)

# df_gsheet.head()

df_gsheet.head()

import gspread_dataframe as gd

spreadsheet_key = '1Ppif1y284fLPVIIoRzAXbPi9eUXzAyjOBr5DR-6XjSM'
sheet_name = 'Top50Coins'

try:
    sh = gc.open_by_key(spreadsheet_key)
    worksheet = sh.worksheet(sheet_name)

    # Directly set the entire DataFrame to the worksheet
    gd.set_with_dataframe(worksheet, df_gsheet)

    print(f"Data successfully pushed to Google Sheet: {spreadsheet_key}")
except Exception as e:
    print(f"Error pushing data to Google Sheet: {e}")

"""# Top 5 Gainers and Losers //TopGainer/TopLosers"""

query_top_500 = """
SELECT slug, cmc_rank, last_updated, symbol, price, percent_change24h, market_cap
FROM crypto_listings_latest_1000
WHERE cmc_rank < 300
ORDER BY percent_change24h DESC
LIMIT 5
"""

top_5_cc = pd.read_sql_query(query_top_500, con)

top_5_cc.head()

# @title fetch top 5
query_top_500 = """
SELECT slug, cmc_rank, last_updated, symbol, price, percent_change24h, market_cap
FROM crypto_listings_latest_1000
WHERE cmc_rank < 300
ORDER BY percent_change24h ASC
LIMIT 5
"""

bottom_5_cc = pd.read_sql_query(query_top_500, con)

# @title renamig tg and tl
# prompt: bottom_5_cc and top_5_cc should be merged but have col names starting with tg_ for all coloums in top_5_cc and tl_for all cols in bottom_5_cc

import pandas as pd
# Rename columns in top_5_cc with 'tg_' prefix
top_5_cc_renamed = top_5_cc.add_prefix('tg_')

# Rename columns in bottom_5_cc with 'tl_' prefix
bottom_5_cc_renamed = bottom_5_cc.add_prefix('tl_')

# Merge the two DataFrames
top_gainers_losers = pd.merge(top_5_cc_renamed, bottom_5_cc_renamed, left_index=True, right_index=True, how='outer')

# @title fetch dmv data for for tl/tg_slug
# prompt: fetch DMV_ALL for sql from aws where slugs are in tg_slug and tl_slug -- in my pandas df top_gainers_losers

import pandas as pd
# Create a list of slugs from the top_gainers_losers DataFrame
tg_slugs = top_gainers_losers['tg_slug'].dropna().tolist()
tl_slugs = top_gainers_losers['tl_slug'].dropna().tolist()
all_slugs = tg_slugs + tl_slugs


# Prepare a string for the IN clause
slugs_placeholder = ', '.join(f"'{slug}'" for slug in all_slugs)


# Construct the SQL query
query = f"""
SELECT *
FROM "FE_DMV_SCORES"
"""

# Execute the query and fetch the data into a DataFrame
tgtl_dmv_scores = pd.read_sql_query(query, con)

# @title Merging df's tg and dmv data
# prompt: tgtl_dmv_scores merge with top_gainers_losers

import pandas as pd
merged_df = pd.merge(top_gainers_losers, tgtl_dmv_scores, left_on='tg_slug', right_on='slug', how='left')
merged_df = merged_df.drop('slug', axis=1)
merged_df = pd.merge(merged_df, tgtl_dmv_scores, left_on='tl_slug', right_on='slug', how='left', suffixes=('_tg', '_tl'))
merged_df = merged_df.drop('slug', axis=1)

"""**Color Code for DMV**"""

# @title DMV color coding

def color_code(score):
  if score > 33:
    return '/#8DFF7E'
  elif score < 0:
    return '/#FF726D'
  else:
    return '/#FF8C42'

merged_df['colours_tg_d'] = merged_df['Durability_Score_tg'].apply(color_code)
merged_df['colours_tg_m'] = merged_df['Momentum_Score_tg'].apply(color_code)
merged_df['colours_tg_v'] = merged_df['Valuation_Score_tg'].apply(color_code)
merged_df['colours_tl_d'] = merged_df['Durability_Score_tl'].apply(color_code)
merged_df['colours_tl_m'] = merged_df['Momentum_Score_tl'].apply(color_code)
merged_df['colours_tl_v'] = merged_df['Valuation_Score_tl'].apply(color_code)

"""print(merged_df[['Durability_Score_tg', 'colours_tg_d', 'Momentum_Score_tg', 'colours_tg_m', 'Valuation_Score_tg', 'colours_tg_v',
                 'Durability_Score_tl', 'colours_tl_d', 'Momentum_Score_tl', 'colours_tl_m', 'Valuation_Score_tl', 'colours_tl_v']])"""

def color_code(score):
  if score > 0:
    return '/#8DFF7E'
  elif score < 0:
    return '/#FF726D'
  else:
    return '/#FFA500'

merged_df['colours_tg_pct'] = merged_df['tg_percent_change24h'].apply(color_code)
merged_df['colours_tl_pct'] = merged_df['tl_percent_change24h'].apply(color_code)

# Format the 'tg_percent_change24h' column with 2 decimal places and add '%'
merged_df['tg_percent_change24h'] = merged_df['tg_percent_change24h'].apply(lambda x: f"{x:.2f}%" if not pd.isnull(x) else x)
merged_df['tl_percent_change24h'] = merged_df['tl_percent_change24h'].apply(lambda x: f"{x:.2f}%" if not pd.isnull(x) else x)

"""Formatting"""

# @title adding $ and formating coloums for tg/tl
# prompt: merged_df can you make sure all coloums have 2 decimal numbers

import pandas as pd
# Loop through each column and format numeric values to 2 decimal places
for column in merged_df.columns:
  if pd.api.types.is_numeric_dtype(merged_df[column]):
    merged_df[column] = merged_df[column].apply(lambda x: round(x, 2) if not pd.isnull(x) else x)

# Add a '$' sign before the price column
merged_df['tl_price'] = '$' + merged_df['tl_price'].astype(str)
merged_df['tg_price'] = '$' + merged_df['tg_price'].astype(str)

# Apply the formatting function to the 'market_cap' column
merged_df['tg_market_cap'] = merged_df['tg_market_cap'].apply(format_market_cap)
merged_df['tl_market_cap'] = merged_df['tl_market_cap'].apply(format_market_cap)

# @title adding logo url to dfs
## First merge: tg_slug to tg_logo
merged_df = pd.merge(
    merged_df,
    logos_and_slugs,
    left_on='tg_slug',
    right_on='slug',
    how='left'
)
merged_df = merged_df.rename(columns={'logo': 'tg_logo'})
merged_df = merged_df.drop('slug', axis=1)

# Second merge: tl_slug to tl_logo
merged_df = pd.merge(
    merged_df,
    logos_and_slugs,
    left_on='tl_slug',
    right_on='slug',
    how='left'
)
merged_df = merged_df.rename(columns={'logo': 'tl_logo'})
merged_df = merged_df.drop('slug', axis=1)

import gspread_dataframe as gd

spreadsheet_key = '1Ppif1y284fLPVIIoRzAXbPi9eUXzAyjOBr5DR-6XjSM'
sheet_name = 'TopGainer/TopLosers'

try:
    sh = gc.open_by_key(spreadsheet_key)
    worksheet = sh.worksheet(sheet_name)

    # Clear existing data
    worksheet.clear()

    # Push the entire DataFrame to the worksheet
    gd.set_with_dataframe(worksheet, merged_df)

    print(f"Sample data successfully pushed to Sheet2 in Google Sheet: {spreadsheet_key}")
except Exception as e:
    print(f"Error pushing sample data to Sheet2 in Google Sheet: {e}")

"""# BTC Overview //BTC_SNAPSHOT"""

# @title bitcoing data only
query_top_1 = """
SELECT slug, cmc_rank, last_updated, symbol, price, percent_change24h, volume24h, market_cap, percent_change7d, percent_change30d, ytd_price_change_percentage
FROM crypto_listings_latest_1000
WHERE cmc_rank < 2
"""
top_1_cc  = pd.read_sql_query(query_top_1, con)

"""Formatting"""

# @title mcap and vol numerical and currency formatting
import pandas as pd

def format_market_cap(market_cap):
    """Formats market cap with units (Million, Billion, Trillion)."""
    if pd.isnull(market_cap):
        return market_cap
    market_cap = float(market_cap)
    if market_cap >= 1e12:
        return f"${market_cap / 1e12:.2f} T"
    elif market_cap >= 1e9:
        return f"${market_cap / 1e9:.2f} B"
    elif market_cap >= 1e6:
        return f"${market_cap / 1e6:.2f} M"
    else:
        return f"${market_cap:.2f}"

# Apply the formatting function to the 'market_cap' column
top_1_cc['market_cap'] = top_1_cc['market_cap'].apply(format_market_cap)
# Apply the formatting function to the 'market_cap' column
top_1_cc['volume24h'] = top_1_cc['volume24h'].apply(format_market_cap)

"""Color Code for PCT_Change"""

# @title color code for pct changes
def color_code(score):
  if score > 0:
    return '/#8DFF7E'
  elif score < 0:
    return '/#FF726D'
  else:
    return '/#FFA500'

top_1_cc['colour_percent_change24h'] = top_1_cc['percent_change24h'].apply(color_code)
top_1_cc['colour_percent_change7d'] = top_1_cc['percent_change7d'].apply(color_code)
top_1_cc['colour_percent_change30d'] = top_1_cc['percent_change30d'].apply(color_code)
top_1_cc['colour_ytd_price_change_percentage'] = top_1_cc['ytd_price_change_percentage'].apply(color_code)

# Format the 'tg_percent_change24h' column with 2 decimal places and add '%'
top_1_cc['percent_change24h'] = top_1_cc['percent_change24h'].apply(lambda x: f"{x:.2f}%" if not pd.isnull(x) else x)
top_1_cc['percent_change7d'] = top_1_cc['percent_change7d'].apply(lambda x: f"{x:.2f}%" if not pd.isnull(x) else x)
top_1_cc['percent_change30d'] = top_1_cc['percent_change30d'].apply(lambda x: f"{x:.2f}%" if not pd.isnull(x) else x)
top_1_cc['ytd_price_change_percentage'] = top_1_cc['ytd_price_change_percentage'].apply(lambda x: f"{x:.2f}%" if not pd.isnull(x) else x)

# Format the 'price' column with '$' and 2 decimal places
top_1_cc['price'] = top_1_cc['price'].apply(lambda x: f"${x:.2f}" if not pd.isnull(x) else x)

# top_1_cc.head()

# @title fetching dmv values for bitcoin
# Construct the SQL query
query = f"""
SELECT *
FROM "FE_DMV_ALL"
WHERE slug = 'bitcoin'
"""
# Execute the query and fetch the data into a DataFrame
dmv_bitcoin = pd.read_sql_query(query, con)

# @title count of bullish bearing and neautal for btc
# prompt: at dmv_bitcoin can you help me count the number '1' '-1' and '0' in the first row and create a add three more colums bullish- Number of '1' in the first row bearishNumber of '-1' in the first row and Number of '0' in the first row is neutral
dmv_bitcoin_first_row = dmv_bitcoin.iloc[0].tolist()
bullish_count = dmv_bitcoin_first_row.count(1)
bearish_count = dmv_bitcoin_first_row.count(-1)
neutral_count = dmv_bitcoin_first_row.count(0)

# Print counts
print(f"Bullish (1): {bullish_count}")
print(f"Bearish (-1): {bearish_count}")
print(f"Neutral (0): {neutral_count}")

# Adding the counts to the top_1_cc DataFrame
top_1_cc['bullish'] = bullish_count
top_1_cc['bearish'] = bearish_count
top_1_cc['neutral'] = neutral_count

# prompt: i want to add a new coloum as Trend and classify it as bearish bullish or consolidating what logic can i use --- # Adding the counts to the top_1_cc DataFrame
# top_1_cc['bullish'] = bullish_count
# top_1_cc['bearish'] = bearish_count
# top_1_cc['neutral'] = neutral_count for these

# Calculate the difference between bullish and bearish counts
top_1_cc['sentiment_diff'] = top_1_cc['bullish'] - top_1_cc['bearish']

# Define a function to classify the trend
def classify_trend(sentiment_diff):
    if sentiment_diff > 4:  # Adjust threshold as needed
        return "Bullish"
    elif sentiment_diff < -4: # Adjust threshold as needed
        return "Bearish"
    else:
        return "Consolidating"

# Apply the function to create the 'Trend' column
top_1_cc['Trend'] = top_1_cc['sentiment_diff'].apply(classify_trend)

# prompt: add a color code as well bullish bearish and consolidating with relevant color using the same format /#color_code

# Define a function to assign color codes based on the trend
def trend_color(trend):
    if trend == "Bullish":
        return "/#49FF38"  # Green for bullish
    elif trend == "Bearish":
        return "/#FF3838"  # Red for bearish
    elif trend == "Consolidating":
        return "/#FFB338" # Orange for consolidating
    else:
        return "/#FFFFFF"  # Default to white if trend is undefined


# Apply the function to create the 'Trend_color' column
top_1_cc['Trend_color'] = top_1_cc['Trend'].apply(trend_color)

top_1_cc['Trend_color'].head()

import gspread_dataframe as gd

spreadsheet_key = '1Ppif1y284fLPVIIoRzAXbPi9eUXzAyjOBr5DR-6XjSM'
sheet_name = 'BTC_SNAPSHOT'

try:
    sh = gc.open_by_key(spreadsheet_key)
    worksheet = sh.worksheet(sheet_name)

    # Clear existing data
    worksheet.clear()

    # Push the entire DataFrame to the worksheet
    gd.set_with_dataframe(worksheet, top_1_cc)

    print(f"BTC snapshot data successfully pushed to Google Sheet: {spreadsheet_key}")
except Exception as e:
    print(f"Error pushing BTC snapshot data to Google Sheet: {e}")

"""# Long and Short //LongOpportunitiespportunities Sheet5"""

# Construct the SQL query
query = f"""
SELECT *
FROM "FE_DMV_ALL"
"""

# Execute the query and fetch the data into a DataFrame
dmv_all = pd.read_sql_query(query, con)

query_for_dmv_all = """
SELECT slug, cmc_rank, last_updated, symbol, price, percent_change24h, market_cap, turnover, percent_change7d, percent_change30d
FROM crypto_listings_latest_1000
"""
listing_for_dmv_all  = pd.read_sql_query(query_for_dmv_all, con)

# @title bbn counts from dmv _ signals

dmv_all['bullish_count'] = dmv_all.apply(lambda row: row.tolist().count(1), axis=1)
dmv_all['bearish_count'] = dmv_all.apply(lambda row: row.tolist().count(-1), axis=1)
dmv_all['neutral_count'] = dmv_all.apply(lambda row: row.tolist().count(0), axis=1)

def classify_sentiment(row):
    bullish_count = row['bullish_count']
    bearish_count = row['bearish_count']

    if bullish_count > bearish_count:
        return 'Bullish'
    elif bearish_count > bullish_count:
        return 'Bearish'
    else:
        return 'Neutral'

dmv_all['sentiment'] = dmv_all.apply(classify_sentiment, axis=1)

# Merge listing_for_dmv_all and dmv_all on 'slug'
dmv_all = pd.merge(listing_for_dmv_all, dmv_all, on='slug', how='left')

# Apply the formatting function to the 'market_cap' column
dmv_all['market_cap'] = dmv_all['market_cap'].apply(format_market_cap)

# dmv_all.head()

# @title # color code for pct
def color_code(score):
  if score > 0:
    return '/#8DFF7E'
  elif score < 0:
    return '/#FF726D'
  else:
    return '/#FFA500'

dmv_all['colour_percent_change24h'] = dmv_all['percent_change24h'].apply(color_code)
dmv_all['colour_percent_change7d'] = dmv_all['percent_change7d'].apply(color_code)
dmv_all['colour_percent_change30d'] = dmv_all['percent_change30d'].apply(color_code)


# Format the 'tg_percent_change24h' column with 2 decimal places and add '%'
dmv_all['percent_change24h'] = dmv_all['percent_change24h'].apply(lambda x: f"{x:.2f}%" if not pd.isnull(x) else x)
dmv_all['percent_change7d'] = dmv_all['percent_change7d'].apply(lambda x: f"{x:.2f}%" if not pd.isnull(x) else x)
dmv_all['percent_change30d'] = dmv_all['percent_change30d'].apply(lambda x: f"{x:.2f}%" if not pd.isnull(x) else x)


# Format the 'price' column with '$' and 2 decimal places
dmv_all['price'] = dmv_all['price'].apply(lambda x: f"${x:.4f}" if not pd.isnull(x) else x)


# Select only the desired columns
dmv_all_reduced = dmv_all[['slug', 'bullish_count', 'bearish_count', 'neutral_count', 'sentiment','cmc_rank','price', 'percent_change24h' , 'percent_change7d', 'percent_change30d',  'market_cap','symbol','turnover','colour_percent_change30d', 'colour_percent_change7d', 'colour_percent_change24h']]

"""filter rank"""

# @title removing stablecoins
# prompt: dmv_all_reduced filter where cmc_rank is less than 350

dmv_all_filtered = dmv_all_reduced[dmv_all_reduced['cmc_rank'] < 199 ]

# Create a list of symbols to remove
symbols_to_remove = ['USDT', 'USDC', 'BUSD', 'DAI', 'TUSD', 'PYUSD', 'PAXG', 'FDUSD', 'USDN', 'MUSD', 'XDC', 'XAUt', 'USDD','XEC','CRO',"USDe"]

# Filter the DataFrame to remove rows with symbols in the list
dmv_all_filtered = dmv_all_filtered[~dmv_all_filtered['symbol'].isin(symbols_to_remove)]

"""Sentiment Sort"""

# prompt: dmv_all_reduced want to keep top 10 bullish and top 10 bearish in 4 colms  like there should be 2 slugs bearish slug and bullish slug

import pandas as pd
# Sort dmv_all_reduced by bullish_count in descending order to get top 10 bullish
top_10_bullish = dmv_all_filtered.sort_values('bullish_count', ascending=False).head(10)

# Sort dmv_all_reduced by bearish_count in descending order to get top 10 bearish
top_10_bearish = dmv_all_filtered.sort_values('bearish_count', ascending=False).head(10)

# Create a new DataFrame with the top 10 bullish and top 10 bearish slugs
top_bullish_bearish = pd.DataFrame({
    'Top 10 Bullish Slugs': top_10_bullish['slug'].tolist(),
    'Top 10 Bullish Counts': top_10_bullish['bullish_count'].tolist(),
    'Top 10 Bearish Slugs': top_10_bearish['slug'].tolist(),
    'Top 10 Bearish Counts': top_10_bearish['bearish_count'].tolist(),
})

"""Ratio Query"""

# prompt: sql_query(querry_ratios, con)  Select m_rat_alpha,d_rat_beta , m_rat_omega and slug from FE_RATIOS
querry_ratios = """
SELECT m_rat_alpha, d_rat_beta, m_rat_omega, slug
FROM "FE_RATIOS"
"""
ratios_df = pd.read_sql_query(querry_ratios, con)

# Loop through each column and format numeric values to 2 decimal places
for column in ratios_df.columns:
  if pd.api.types.is_numeric_dtype(ratios_df[column]):
    ratios_df[column] = ratios_df[column].apply(lambda x: round(x, 2) if not pd.isnull(x) else x)

# @title adding logos
# prompt: top_10_bullish join with ratios_df
# Select only the 'slug' and 'logo' columns from logos_and_slugs
logos_only = logos_and_slugs[['slug', 'logo']]

# Merge top_10_bullish with ratios_df on 'slug'
top_10_bullish = pd.merge(top_10_bullish, ratios_df, on='slug', how='left')

# Merge top_10_bullish with the filtered logos_only DataFrame
top_10_bullish = pd.merge(top_10_bullish, logos_only, on='slug', how='left')

# Merge top_10_bullish with ratios_df on 'slug'
top_10_bearish = pd.merge(top_10_bearish, ratios_df, on='slug', how='left')

top_10_bearish = pd.merge(top_10_bearish, logos_only, on='slug', how='left')

# top_10_bearish.head(10)
# top_10_bullish.head(10)

import gspread_dataframe as gd

spreadsheet_key = '1Ppif1y284fLPVIIoRzAXbPi9eUXzAyjOBr5DR-6XjSM'
sheet_name = 'ShortOpportunities'

try:
    # List all available sheets in the spreadsheet for verification
    sh = gc.open_by_key(spreadsheet_key)
    print("Available sheets:", [worksheet.title for worksheet in sh.worksheets()])

    # Try to access the specific worksheet
    worksheet = sh.worksheet(sheet_name)

    # Clear existing data
    worksheet.clear()

    # Push the entire DataFrame to the worksheet
    gd.set_with_dataframe(worksheet, top_10_bearish)

    print(f"Long Opportunities data successfully pushed to Google Sheet: {spreadsheet_key}")
except Exception as e:
    print(f"Error pushing Long Opportunities data to Google Sheet: {e}")

import gspread_dataframe as gd

spreadsheet_key = '1Ppif1y284fLPVIIoRzAXbPi9eUXzAyjOBr5DR-6XjSM'
sheet_name = 'LongOpportunities'

try:
    # List all available sheets in the spreadsheet for verification
    sh = gc.open_by_key(spreadsheet_key)
    print("Available sheets:", [worksheet.title for worksheet in sh.worksheets()])

    # Try to access the specific worksheet
    worksheet = sh.worksheet(sheet_name)

    # Clear existing data
    worksheet.clear()

    # Push the entire DataFrame to the worksheet
    gd.set_with_dataframe(worksheet, top_10_bullish)

    print(f"Long Opportunities data successfully pushed to Google Sheet: {spreadsheet_key}")
except Exception as e:
    print(f"Error pushing Long Opportunities data to Google Sheet: {e}")

"""# GLL //MarketOverview"""

# @title pulling global listings latest
query_gll  = """
SELECT *
FROM crypto_global_latest
"""

gll  = pd.read_sql_query(query_gll, con)

# gll.head()

# @title filtering cols , keeping only required
# prompt: total_market_cap
# total_volume24h_reported
# altcoin_volume24h_reported
# altcoin_market_cap
# total_market_cap_yesterday_percentage_change
# total_volume24h_yesterday_percentage_change
# derivatives_volume24h_reported
# derivatives24h_percentage_change
# active_crypto_currencies
# total_crypto_currencies
# active_exchanges
# total_exchanges
# stablecoin_volume24h_reported
# stablecoin_market_cap
# stablecoin24h_percentage_change
# defi_volume24h_reported
# defi_market_cap
# defi24h_percentage_change
# btc_dominance24h_percentage_change
# eth_dominance24h_percentage_change
# btc_dominance
# eth_dominance
# keep only these in gll

# Select only the desired columns from the gll DataFrame
gll = gll[[
    'total_market_cap',
    'total_volume24h_reported',
    'altcoin_volume24h_reported',
    'altcoin_market_cap',
    'total_market_cap_yesterday_percentage_change',
    'total_volume24h_yesterday_percentage_change',
    'derivatives_volume24h_reported',
    'derivatives24h_percentage_change',
    'active_crypto_currencies',
    'total_crypto_currencies',
    'active_exchanges',
    'total_exchanges',
    'stablecoin_volume24h_reported',
    'stablecoin_market_cap',
    'stablecoin24h_percentage_change',
    'defi_volume24h_reported',
    'defi_market_cap',
    'defi24h_percentage_change',
    'btc_dominance24h_percentage_change',
    'eth_dominance24h_percentage_change',
    'btc_dominance',
    'eth_dominance'
]]

# Now, gll_selected contains only the desired columns.
# gll.info()

# @title Color Code for gll percentage change
# prompt: apply color code function and add a new coloum for all percentage change coloums in gll

def color_code(score):
  if score > 0:
    return '/#8DFF7E'
  elif score < 0:
    return '/#FF726D'
  else:
    return '/#FFA500'

percentage_change_columns = [col for col in gll.columns if 'percentage_change' in col]

for col in percentage_change_columns:
    gll[f'colours_{col}'] = gll[col].apply(color_code)

gll.info()

"""formatting"""

# @title decimals
# prompt: gll can you make all cols into 2 decimals

# Loop through each column and format numeric values to 2 decimal places
for column in gll.columns:
  if pd.api.types.is_numeric_dtype(gll[column]):
    gll[column] = gll[column].apply(lambda x: round(x, 2) if not pd.isnull(x) else x)

# Loop through columns in gll DataFrame
for column in gll.columns:
  if column.endswith('percentage_change') and pd.api.types.is_numeric_dtype(gll[column]):
    # Replace the original column with a new one where numeric values have '%' appended
    gll[column] = gll[column].apply(lambda x: f"{x:.2f}%" if not pd.isnull(x) else x)

# @title mcap format units
# prompt: gll in here apply the market_cap function to all coloums which have market_cap in them

def format_market_cap(market_cap):
    """Formats market cap with units (Million, Billion, Trillion)."""
    if pd.isnull(market_cap):
        return market_cap
    market_cap = float(market_cap)
    if market_cap >= 1e12:
        return f"${market_cap / 1e12:.2f} T"
    elif market_cap >= 1e9:
        return f"${market_cap / 1e9:.2f} B"
    elif market_cap >= 1e6:
        return f"${market_cap / 1e6:.2f} M"
    else:
        return f"${market_cap:.2f}"


        # Assuming you have a DataFrame named 'gll' and a function named 'format_market_cap'


# List of columns to apply the format_market_cap function
columns_to_format = [
    'total_market_cap',
    'defi_market_cap',
    'stablecoin_market_cap',
    'total_volume24h_reported',
    'defi_volume24h_reported',
    'altcoin_volume24h_reported',
    'stablecoin_volume24h_reported',
    'altcoin_market_cap',
    'derivatives_volume24h_reported'
]

# Apply the format_market_cap function to the specified columns
for column in columns_to_format:
    gll[column] = gll[column].apply(format_market_cap)

# prompt: add a coloum in gll to put todays date  and another coloum to add a time only  starting with day as in monday tuesday whatever it tis today  .. also make sure keeping the formatting convert them to str also add time ... for todays date can you write like 22nd Oct, 2024

from datetime import datetime, date

# ... (Your existing code) ...

# @title Add date and day columns to gll

# Get today's date in the desired format
today = date.today()
day_number = today.strftime("%d")
day_suffix = "th" if 11 <= int(day_number) <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(int(day_number) % 10, "th")
todays_date_str = f"{day_number}{day_suffix} {today.strftime('%b, %Y')}"

# Get today's day name
today_day_name = date.today().strftime("%A")


# Add the columns to the gll DataFrame
gll['Todays_Date'] = todays_date_str
gll['Todays_Day'] = today_day_name


# Convert 'Todays_Date' and 'Todays_Day' to string type if they are not already
gll['Todays_Date'] = gll['Todays_Date'].astype(str)
gll['Todays_Day'] = gll['Todays_Day'].astype(str)


# Get current time
current_time = datetime.now().strftime("%H:%M:%S")
gll['Current_Time'] = current_time
gll['Current_Time'] = gll['Current_Time'].astype(str)

# ... (rest of your code) ...

# @title ALT SEASON COLOUM

query_for_dmv_all = """
SELECT slug, cmc_rank, percent_change90d
FROM crypto_listings_latest_1000
WHERE cmc_rank < 101
"""
seasons_df  = pd.read_sql_query(query_for_dmv_all, con)

# Create a list of symbols to remove
symbols_to_remove = ['USDT', 'USDC', 'BUSD', 'DAI', 'TUSD', 'PYUSD', 'PAXG', 'FDUSD', 'USDN', 'MUSD', 'XDC', 'XAUt', 'USDD','XEC','CRO']

# Filter the DataFrame to remove rows with symbols in the list
seasons_df = seasons_df[~seasons_df['slug'].isin(symbols_to_remove)]


# Extract Bitcoin's 24h percentage change
bitcoin_return = float(top_1_cc['percent_change24h'].iloc[0].replace('%', ''))


# Function to compare returns and assign 1 or -1
def compare_returns(row):
  try:
    coin_return = float(row['percent_change90d'])
    if coin_return > bitcoin_return:
      return 1
    else:
      return -1
  except (ValueError, TypeError):
    return 0 # Handle cases with missing or invalid data


# Apply the comparison function and create a new column
seasons_df['vs_bitcoin_90d'] = seasons_df.apply(compare_returns, axis=1)

#Example of adding a new row (replace with your actual data)
new_row = pd.DataFrame({'slug': ['new_coin'], 'cmc_rank': [102], 'percent_change90d': [10], 'vs_bitcoin_90d' : [1]}) #Example data
seasons_df = pd.concat([seasons_df, new_row], ignore_index = True)


# prompt: can you count 1 and -1 for seasons_df and define a logic to a new df with single coloum which has coloum name as alt_season and give value yes if count of 1 is more than 72 else no

# Count 1 and -1 in 'vs_bitcoin_90d' column
count_1 = seasons_df['vs_bitcoin_90d'].value_counts().get(1, 0)
count_minus_1 = seasons_df['vs_bitcoin_90d'].value_counts().get(-1, 0)

# Create a new DataFrame
new_df = pd.DataFrame({'alt_season': ['YES' if count_1 > 72 else 'NO']})

# Add the 'alt_season' column to the 'gll' DataFrame
gll = pd.concat([gll, new_df], axis=1)

def color_code_yes_no(value):
    """
    Colors YES in Green, NO in Red, Other in white
    """
    if value == 'YES':
        return '/#8DFF7E'  # Green for YES
    elif value == 'NO':
        return '/#FF726D'  # Red for NO
    else:
        return '/#FFFFFF'  # Default to white for other values

# Assuming gll is your DataFrame and 'alt_season' is the column you want to color-code
# Get the single value from the 'alt_season' column and convert to string
alt_season_value = str(gll['alt_season'].iloc[0])  # Convert to string

# Apply the color_code_yes_no function to the single value
color_code = color_code_yes_no(alt_season_value)

# Assign the color code to a new column in the DataFrame
gll['colour_alt_season'] = color_code  # Assign the color code to all rows

import gspread_dataframe as gd

spreadsheet_key = '1Ppif1y284fLPVIIoRzAXbPi9eUXzAyjOBr5DR-6XjSM'
sheet_name = 'MarketOverview'

try:
   sh = gc.open_by_key(spreadsheet_key)
   worksheet = sh.worksheet(sheet_name)

   # Clear existing data
   worksheet.clear()

   # Push the entire DataFrame to the worksheet
   gd.set_with_dataframe(worksheet, gll)

   print(f"Data successfully pushed to MarketOverview in Google Sheet: {spreadsheet_key}")
except Exception as e:
   print(f"Error pushing data to MarketOverview in Google Sheet: {e}")

con.close()
