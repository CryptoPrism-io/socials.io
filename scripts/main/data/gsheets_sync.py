import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import numpy as np
import mysql.connector
import gspread
import psycopg2
import gspread_dataframe as gd
from datetime import date, datetime, timedelta
import time

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

# Connect to PostgreSQL database
con = psycopg2.connect(
        host="34.55.195.199",
        database="dbcp",
        user="yogass09",
        password="jaimaakamakhya",
        port=5432
    )

# Execute a query to get a list of tables
with con.cursor() as cur:
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
    tables = cur.fetchall()

# Convert the list of tuples to a list of strings
table_names = [table[0] for table in tables]

# Print the list of table names
print("Available tables:", table_names)

# ==================== UTILITY FUNCTIONS ====================

def safe_float(value):
    """Safely convert value to float, return None if conversion fails"""
    if value is None or pd.isna(value):
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None

def safe_string(value):
    """Safely convert value to string"""
    if value is None or pd.isna(value):
        return ""
    return str(value).strip()

# Fixed color_code function for percentage changes (handles None/NaN)
def color_code_percentage(score):
    """Color code for percentage changes - handles None/NaN values"""
    if score is None or pd.isna(score):
        return '/#808080'  # Gray for missing data
    try:
        score = float(score)
        if score > 0:
            return '/#8DFF7E'
        elif score < 0:
            return '/#FF726D'
        else:
            return '/#FFA500'
    except (ValueError, TypeError):
        return '/#808080'  # Gray for invalid data

# Fixed color_code function for DMV scores (handles None/NaN)
def color_code_dmv(score):
    """Color code for DMV scores - handles None/NaN values"""
    if score is None or pd.isna(score):
        return '/#808080'  # Gray for missing data
    try:
        score = float(score)
        if score > 33:
            return '/#8DFF7E'
        elif score < 0:
            return '/#FF726D'
        else:
            return '/#FF8C42'
    except (ValueError, TypeError):
        return '/#808080'  # Gray for invalid data

# Fixed trend color function
def trend_color(trend):
    """Color code for trend values - handles None/NaN"""
    if trend is None or pd.isna(trend):
        return '/#808080'  # Gray for missing data
    
    trend_str = str(trend).strip()
    if trend_str == "Bullish":
        return "/#49FF38"  # Green for bullish
    elif trend_str == "Bearish":
        return "/#FF3838"  # Red for bearish
    elif trend_str == "Consolidating":
        return "/#FFB338"  # Orange for consolidating
    else:
        return "/#808080"  # Gray for undefined

# Fixed color_code function for yes/no values
def color_code_yes_no(value):
    """Color code for YES/NO values - handles None/NaN"""
    if value is None or pd.isna(value):
        return '/#808080'  # Gray for missing data
    
    value_str = str(value).upper().strip()
    if value_str == 'YES':
        return '/#8DFF7E'  # Green for YES
    elif value_str == 'NO':
        return '/#FF726D'  # Red for NO
    else:
        return '/#808080'  # Gray for other values

def format_market_cap(market_cap):
    """Formats market cap with units (Million, Billion, Trillion)."""
    if pd.isnull(market_cap):
        return market_cap
    try:
        market_cap = float(market_cap)
        if market_cap >= 1e12:
            return f"${market_cap / 1e12:.2f} T"
        elif market_cap >= 1e9:
            return f"${market_cap / 1e9:.2f} B"
        elif market_cap >= 1e6:
            return f"${market_cap / 1e6:.2f} M"
        else:
            return f"${market_cap:.2f}"
    except (ValueError, TypeError):
        return str(market_cap)

def clean_dataframe_for_gsheets(df):
    """
    Clean DataFrame by replacing NaN, None, inf, and other problematic values
    with empty strings or appropriate defaults for Google Sheets
    """
    df_cleaned = df.copy()
    
    # Replace NaN, None, inf, -inf with empty strings
    df_cleaned = df_cleaned.replace([np.nan, np.inf, -np.inf, None, 'nan', 'NaN', 'null', 'NULL'], '')
    
    # Convert any remaining float NaN to empty string
    for col in df_cleaned.columns:
        if df_cleaned[col].dtype == 'object':
            df_cleaned[col] = df_cleaned[col].astype(str).replace(['nan', 'None', 'NaT'], '')
        elif df_cleaned[col].dtype in ['float64', 'float32']:
            df_cleaned[col] = df_cleaned[col].fillna('')
        elif df_cleaned[col].dtype in ['int64', 'int32']:
            df_cleaned[col] = df_cleaned[col].fillna(0)
    
    return df_cleaned

def safe_push_to_gsheet(df, sheet_name, spreadsheet_key):
    """Safely push DataFrame to Google Sheets with error handling"""
    try:
        # Clean the DataFrame
        df_cleaned = clean_dataframe_for_gsheets(df)
        
        # Push to Google Sheets
        sh = gc.open_by_key(spreadsheet_key)
        worksheet = sh.worksheet(sheet_name)
        worksheet.clear()
        gd.set_with_dataframe(worksheet, df_cleaned)
        
        print(f"✓ Successfully pushed data to {sheet_name}")
        return True
        
    except Exception as e:
        print(f"✗ Error pushing data to {sheet_name}: {e}")
        return False

# ==================== TOP 50 COINS ====================

print("Processing Top 50 coins...")

query_top_100 = """
SELECT slug, cmc_rank, last_updated, symbol, price, percent_change24h, market_cap
FROM crypto_listings_latest_1000
WHERE cmc_rank < 50
"""
top_100_cc = pd.read_sql_query(query_top_100, con)

# Create a list of slugs from the top_100_crypto DataFrame
slugs = top_100_cc['slug'].tolist()

# Construct the SQL query for logos
query = """
SELECT logo, slug FROM "FE_CC_INFO_URL"
"""

# Execute the query and fetch the data into a DataFrame
logos_and_slugs = pd.read_sql_query(query, con)

# Merge the two DataFrames on the 'slug' column
df_top_100_daily = pd.merge(top_100_cc, logos_and_slugs, on='slug', how='left')

# Convert 'price' column to numeric, handling potential errors
df_top_100_daily['price'] = pd.to_numeric(df_top_100_daily['price'], errors='coerce')

# Format the 'price' column with '$' and 2 decimal places
df_top_100_daily['price_usd'] = df_top_100_daily['price'].apply(lambda x: f"${x:.2f}" if not pd.isnull(x) else "N/A")

# Convert 'percent_change24h' column to numeric, handling potential errors
df_top_100_daily['percent_change24h'] = pd.to_numeric(df_top_100_daily['percent_change24h'], errors='coerce')

# Format the 'percent_change24h' column with 2 decimal places and add '%'
df_top_100_daily['pct_1d'] = df_top_100_daily['percent_change24h'].apply(lambda x: f"{x:.2f}%" if not pd.isnull(x) else "N/A")

# Add color coding for percentage change
df_top_100_daily['colour'] = df_top_100_daily['percent_change24h'].apply(color_code_percentage)

# Apply the formatting function to the 'market_cap' column
df_top_100_daily['mcap_units'] = df_top_100_daily['market_cap'].apply(format_market_cap)

# Select specific columns from the DataFrame
df_gsheet = df_top_100_daily[['logo','slug', 'cmc_rank', 'price_usd', 'pct_1d', 'mcap_units', 'symbol', 'colour']]

# Sort by cmc_rank ascending
df_gsheet = df_gsheet.sort_values('cmc_rank', ascending=True)

# Add date time 
df_gsheet['last_updated'] = date.today()

print("Top 50 coins processed successfully")

# ==================== TOP GAINERS AND LOSERS ====================

print("Processing Top Gainers and Losers...")

# Top 5 gainers
query_top_gainers = """
SELECT slug, cmc_rank, last_updated, symbol, price, percent_change24h, market_cap
FROM crypto_listings_latest_1000
WHERE cmc_rank < 300
ORDER BY percent_change24h DESC
LIMIT 5
"""
top_5_cc = pd.read_sql_query(query_top_gainers, con)

# Top 5 losers
query_top_losers = """
SELECT slug, cmc_rank, last_updated, symbol, price, percent_change24h, market_cap
FROM crypto_listings_latest_1000
WHERE cmc_rank < 300
ORDER BY percent_change24h ASC
LIMIT 5
"""
bottom_5_cc = pd.read_sql_query(query_top_losers, con)

# Rename columns with prefixes
top_5_cc_renamed = top_5_cc.add_prefix('tg_')
bottom_5_cc_renamed = bottom_5_cc.add_prefix('tl_')

# Merge the two DataFrames
top_gainers_losers = pd.merge(top_5_cc_renamed, bottom_5_cc_renamed, left_index=True, right_index=True, how='outer')

# Fetch DMV data
tg_slugs = top_gainers_losers['tg_slug'].dropna().tolist()
tl_slugs = top_gainers_losers['tl_slug'].dropna().tolist()
all_slugs = tg_slugs + tl_slugs

# Get DMV scores
query_dmv = """
SELECT *
FROM "FE_DMV_SCORES"
"""
tgtl_dmv_scores = pd.read_sql_query(query_dmv, con)

# Merge DMV data
merged_df = pd.merge(top_gainers_losers, tgtl_dmv_scores, left_on='tg_slug', right_on='slug', how='left')
merged_df = merged_df.drop('slug', axis=1)
merged_df = pd.merge(merged_df, tgtl_dmv_scores, left_on='tl_slug', right_on='slug', how='left', suffixes=('_tg', '_tl'))
merged_df = merged_df.drop('slug', axis=1)

# Clean numeric columns first
numeric_cols = ['Durability_Score_tg', 'Momentum_Score_tg', 'Valuation_Score_tg',
                'Durability_Score_tl', 'Momentum_Score_tl', 'Valuation_Score_tl',
                'tg_percent_change24h', 'tl_percent_change24h']

for col in numeric_cols:
    if col in merged_df.columns:
        merged_df[col] = pd.to_numeric(merged_df[col], errors='coerce')

# DMV color coding
merged_df['colours_tg_d'] = merged_df['Durability_Score_tg'].apply(color_code_dmv)
merged_df['colours_tg_m'] = merged_df['Momentum_Score_tg'].apply(color_code_dmv)
merged_df['colours_tg_v'] = merged_df['Valuation_Score_tg'].apply(color_code_dmv)
merged_df['colours_tl_d'] = merged_df['Durability_Score_tl'].apply(color_code_dmv)
merged_df['colours_tl_m'] = merged_df['Momentum_Score_tl'].apply(color_code_dmv)
merged_df['colours_tl_v'] = merged_df['Valuation_Score_tl'].apply(color_code_dmv)

# Percentage change color coding
merged_df['colours_tg_pct'] = merged_df['tg_percent_change24h'].apply(color_code_percentage)
merged_df['colours_tl_pct'] = merged_df['tl_percent_change24h'].apply(color_code_percentage)

# Format percentage changes
merged_df['tg_percent_change24h'] = merged_df['tg_percent_change24h'].apply(lambda x: f"{x:.2f}%" if not pd.isnull(x) else "N/A")
merged_df['tl_percent_change24h'] = merged_df['tl_percent_change24h'].apply(lambda x: f"{x:.2f}%" if not pd.isnull(x) else "N/A")

# Format numeric columns to 2 decimal places
for column in merged_df.columns:
    if pd.api.types.is_numeric_dtype(merged_df[column]):
        merged_df[column] = merged_df[column].apply(lambda x: round(x, 2) if not pd.isnull(x) else x)

# Add $ sign to prices
if 'tl_price' in merged_df.columns:
    merged_df['tl_price'] = '$' + merged_df['tl_price'].astype(str)
if 'tg_price' in merged_df.columns:
    merged_df['tg_price'] = '$' + merged_df['tg_price'].astype(str)

# Format market caps
if 'tg_market_cap' in merged_df.columns:
    merged_df['tg_market_cap'] = merged_df['tg_market_cap'].apply(format_market_cap)
if 'tl_market_cap' in merged_df.columns:
    merged_df['tl_market_cap'] = merged_df['tl_market_cap'].apply(format_market_cap)

# Add logos
merged_df = pd.merge(merged_df, logos_and_slugs, left_on='tg_slug', right_on='slug', how='left')
merged_df = merged_df.rename(columns={'logo': 'tg_logo'})
merged_df = merged_df.drop('slug', axis=1)

merged_df = pd.merge(merged_df, logos_and_slugs, left_on='tl_slug', right_on='slug', how='left')
merged_df = merged_df.rename(columns={'logo': 'tl_logo'})
merged_df = merged_df.drop('slug', axis=1)

print("Top Gainers and Losers processed successfully")

# ==================== BTC OVERVIEW ====================

print("Processing BTC Overview...")

query_top_1 = """
SELECT slug, cmc_rank, last_updated, symbol, price, percent_change24h, volume24h, market_cap, percent_change7d, percent_change30d, ytd_price_change_percentage
FROM crypto_listings_latest_1000
WHERE cmc_rank < 2
"""
top_1_cc = pd.read_sql_query(query_top_1, con)

# Clean numeric columns
numeric_btc_cols = ['price', 'percent_change24h', 'volume24h', 'market_cap', 
                    'percent_change7d', 'percent_change30d', 'ytd_price_change_percentage']

for col in numeric_btc_cols:
    if col in top_1_cc.columns:
        top_1_cc[col] = pd.to_numeric(top_1_cc[col], errors='coerce')

# Format market cap and volume
top_1_cc['market_cap'] = top_1_cc['market_cap'].apply(format_market_cap)
top_1_cc['volume24h'] = top_1_cc['volume24h'].apply(format_market_cap)

# Color code for percentage changes
top_1_cc['colour_percent_change24h'] = top_1_cc['percent_change24h'].apply(color_code_percentage)
top_1_cc['colour_percent_change7d'] = top_1_cc['percent_change7d'].apply(color_code_percentage)
top_1_cc['colour_percent_change30d'] = top_1_cc['percent_change30d'].apply(color_code_percentage)
top_1_cc['colour_ytd_price_change_percentage'] = top_1_cc['ytd_price_change_percentage'].apply(color_code_percentage)

# Format percentage columns
top_1_cc['percent_change24h'] = top_1_cc['percent_change24h'].apply(lambda x: f"{x:.2f}%" if not pd.isnull(x) else "N/A")
top_1_cc['percent_change7d'] = top_1_cc['percent_change7d'].apply(lambda x: f"{x:.2f}%" if not pd.isnull(x) else "N/A")
top_1_cc['percent_change30d'] = top_1_cc['percent_change30d'].apply(lambda x: f"{x:.2f}%" if not pd.isnull(x) else "N/A")
top_1_cc['ytd_price_change_percentage'] = top_1_cc['ytd_price_change_percentage'].apply(lambda x: f"{x:.2f}%" if not pd.isnull(x) else "N/A")

# Format price
top_1_cc['price'] = top_1_cc['price'].apply(lambda x: f"${x:.2f}" if not pd.isnull(x) else "N/A")

# Fetch DMV values for Bitcoin
query_dmv_btc = """
SELECT *
FROM "FE_DMV_ALL"
WHERE slug = 'bitcoin'
"""
dmv_bitcoin = pd.read_sql_query(query_dmv_btc, con)

# Count bullish, bearish, neutral signals
if not dmv_bitcoin.empty:
    dmv_bitcoin_first_row = dmv_bitcoin.iloc[0].tolist()
    bullish_count = dmv_bitcoin_first_row.count(1)
    bearish_count = dmv_bitcoin_first_row.count(-1)
    neutral_count = dmv_bitcoin_first_row.count(0)
else:
    bullish_count = bearish_count = neutral_count = 0

# Add counts to DataFrame
top_1_cc['bullish'] = bullish_count
top_1_cc['bearish'] = bearish_count
top_1_cc['neutral'] = neutral_count

# Calculate sentiment difference and trend
top_1_cc['sentiment_diff'] = top_1_cc['bullish'] - top_1_cc['bearish']

def classify_trend(sentiment_diff):
    try:
        sentiment_diff = float(sentiment_diff)
        if sentiment_diff > 4:
            return "Bullish"
        elif sentiment_diff < -4:
            return "Bearish"
        else:
            return "Consolidating"
    except (ValueError, TypeError):
        return "Consolidating"

top_1_cc['Trend'] = top_1_cc['sentiment_diff'].apply(classify_trend)
top_1_cc['Trend_color'] = top_1_cc['Trend'].apply(trend_color)

print("BTC Overview processed successfully")

# ==================== LONG AND SHORT OPPORTUNITIES ====================

print("Processing Long and Short Opportunities...")

# Get all DMV data
query_dmv_all = """
SELECT *
FROM "FE_DMV_ALL"
"""
dmv_all = pd.read_sql_query(query_dmv_all, con)

# Get listing data for DMV
query_for_dmv_all = """
SELECT slug, cmc_rank, last_updated, symbol, price, percent_change24h, market_cap, turnover, percent_change7d, percent_change30d
FROM crypto_listings_latest_1000
"""
listing_for_dmv_all = pd.read_sql_query(query_for_dmv_all, con)

# Calculate sentiment counts for each row
dmv_all['bullish_count'] = dmv_all.apply(lambda row: row.tolist().count(1), axis=1)
dmv_all['bearish_count'] = dmv_all.apply(lambda row: row.tolist().count(-1), axis=1)
dmv_all['neutral_count'] = dmv_all.apply(lambda row: row.tolist().count(0), axis=1)

def classify_sentiment(row):
    try:
        bullish_count = int(row['bullish_count'])
        bearish_count = int(row['bearish_count'])
        
        if bullish_count > bearish_count:
            return 'Bullish'
        elif bearish_count > bullish_count:
            return 'Bearish'
        else:
            return 'Neutral'
    except (ValueError, TypeError):
        return 'Neutral'

dmv_all['sentiment'] = dmv_all.apply(classify_sentiment, axis=1)

# Merge with listing data
dmv_all = pd.merge(listing_for_dmv_all, dmv_all, on='slug', how='left')

# Clean numeric columns
dmv_numeric_cols = ['price', 'percent_change24h', 'percent_change7d', 'percent_change30d', 'market_cap']
for col in dmv_numeric_cols:
    if col in dmv_all.columns:
        dmv_all[col] = pd.to_numeric(dmv_all[col], errors='coerce')

# Apply formatting
dmv_all['market_cap'] = dmv_all['market_cap'].apply(format_market_cap)

# Color code percentages
dmv_all['colour_percent_change24h'] = dmv_all['percent_change24h'].apply(color_code_percentage)
dmv_all['colour_percent_change7d'] = dmv_all['percent_change7d'].apply(color_code_percentage)
dmv_all['colour_percent_change30d'] = dmv_all['percent_change30d'].apply(color_code_percentage)

# Format percentages
dmv_all['percent_change24h'] = dmv_all['percent_change24h'].apply(lambda x: f"{x:.2f}%" if not pd.isnull(x) else "N/A")
dmv_all['percent_change7d'] = dmv_all['percent_change7d'].apply(lambda x: f"{x:.2f}%" if not pd.isnull(x) else "N/A")
dmv_all['percent_change30d'] = dmv_all['percent_change30d'].apply(lambda x: f"{x:.2f}%" if not pd.isnull(x) else "N/A")

# Format price
dmv_all['price'] = dmv_all['price'].apply(lambda x: f"${x:.4f}" if not pd.isnull(x) else "N/A")

# Select desired columns
dmv_all_reduced = dmv_all[['slug', 'bullish_count', 'bearish_count', 'neutral_count', 'sentiment',
                          'cmc_rank','price', 'percent_change24h' , 'percent_change7d', 'percent_change30d',  
                          'market_cap','symbol','turnover','colour_percent_change30d', 'colour_percent_change7d', 
                          'colour_percent_change24h']]

# Filter by rank and remove stablecoins
dmv_all_filtered = dmv_all_reduced[dmv_all_reduced['cmc_rank'] < 199]

symbols_to_remove = ['USDT', 'USDC', 'BUSD', 'DAI', 'TUSD', 'PYUSD', 'PAXG', 'FDUSD', 'USDN', 'MUSD', 'XDC', 'XAUt', 'USDD','XEC','CRO',"USDe"]
dmv_all_filtered = dmv_all_filtered[~dmv_all_filtered['symbol'].isin(symbols_to_remove)]

# Get top 10 bullish and bearish
top_10_bullish = dmv_all_filtered.sort_values('bullish_count', ascending=False).head(10)
top_10_bearish = dmv_all_filtered.sort_values('bearish_count', ascending=False).head(10)

# Get ratios data
query_ratios = """
SELECT m_rat_alpha, d_rat_beta, m_rat_omega, slug
FROM "FE_RATIOS"
"""
ratios_df = pd.read_sql_query(query_ratios, con)

# Format ratios to 2 decimal places
for column in ratios_df.columns:
    if pd.api.types.is_numeric_dtype(ratios_df[column]):
        ratios_df[column] = ratios_df[column].apply(lambda x: round(x, 2) if not pd.isnull(x) else x)

# Add ratios and logos to bullish/bearish dataframes
logos_only = logos_and_slugs[['slug', 'logo']]

top_10_bullish = pd.merge(top_10_bullish, ratios_df, on='slug', how='left')
top_10_bullish = pd.merge(top_10_bullish, logos_only, on='slug', how='left')

top_10_bearish = pd.merge(top_10_bearish, ratios_df, on='slug', how='left')
top_10_bearish = pd.merge(top_10_bearish, logos_only, on='slug', how='left')

print("Long and Short Opportunities processed successfully")

# ==================== GLOBAL LISTINGS LATEST ====================

print("Processing Market Overview...")

query_gll = """
SELECT *
FROM crypto_global_latest
"""
gll = pd.read_sql_query(query_gll, con)

# Select only desired columns
gll = gll[[
    'total_market_cap', 'total_volume24h_reported', 'altcoin_volume24h_reported',
    'altcoin_market_cap', 'total_market_cap_yesterday_percentage_change',
    'total_volume24h_yesterday_percentage_change', 'derivatives_volume24h_reported',
    'derivatives24h_percentage_change', 'active_crypto_currencies', 'total_crypto_currencies',
    'active_exchanges', 'total_exchanges', 'stablecoin_volume24h_reported',
    'stablecoin_market_cap', 'stablecoin24h_percentage_change', 'defi_volume24h_reported',
    'defi_market_cap', 'defi24h_percentage_change', 'btc_dominance24h_percentage_change',
    'eth_dominance24h_percentage_change', 'btc_dominance', 'eth_dominance'
]]

# Clean numeric columns
gll_numeric_cols = [col for col in gll.columns if gll[col].dtype in ['float64', 'int64']]
for col in gll_numeric_cols:
    gll[col] = pd.to_numeric(gll[col], errors='coerce')

# Apply color coding to percentage change columns
percentage_change_columns = [col for col in gll.columns if 'percentage_change' in col]
for col in percentage_change_columns:
    gll[f'colours_{col}'] = gll[col].apply(color_code_percentage)

# Format numeric values to 2 decimal places
for column in gll.columns:
    if pd.api.types.is_numeric_dtype(gll[column]):
        gll[column] = gll[column].apply(lambda x: round(x, 2) if not pd.isnull(x) else x)

# Format percentage columns
for column in gll.columns:
    if column.endswith('percentage_change') and pd.api.types.is_numeric_dtype(gll[column]):
        gll[column] = gll[column].apply(lambda x: f"{x:.2f}%" if not pd.isnull(x) else "N/A")

# Format market cap and volume columns
columns_to_format = [
    'total_market_cap', 'defi_market_cap', 'stablecoin_market_cap',
    'total_volume24h_reported', 'defi_volume24h_reported', 'altcoin_volume24h_reported',
    'stablecoin_volume24h_reported', 'altcoin_market_cap', 'derivatives_volume24h_reported'
]

for column in columns_to_format:
    if column in gll.columns:
        gll[column] = gll[column].apply(format_market_cap)

# Add date and time information
today = date.today()
day_number = today.strftime("%d")
day_suffix = "th" if 11 <= int(day_number) <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(int(day_number) % 10, "th")
todays_date_str = f"{day_number}{day_suffix} {today.strftime('%b, %Y')}"
today_day_name = date.today().strftime("%A")
current_time = datetime.now().strftime("%H:%M:%S")

gll['Todays_Date'] = todays_date_str
gll['Todays_Day'] = today_day_name
gll['Current_Time'] = current_time

# Convert to strings
gll['Todays_Date'] = gll['Todays_Date'].astype(str)
gll['Todays_Day'] = gll['Todays_Day'].astype(str)
gll['Current_Time'] = gll['Current_Time'].astype(str)

# Alt season calculation
query_seasons = """
SELECT slug, cmc_rank, percent_change90d
FROM crypto_listings_latest_1000
WHERE cmc_rank < 101
"""
seasons_df = pd.read_sql_query(query_seasons, con)

# Remove stablecoins
seasons_df = seasons_df[~seasons_df['slug'].isin(symbols_to_remove)]

# Get Bitcoin's 24h percentage change
try:
    bitcoin_return_str = top_1_cc['percent_change24h'].iloc[0]
    if isinstance(bitcoin_return_str, str) and '%' in bitcoin_return_str:
        bitcoin_return = float(bitcoin_return_str.replace('%', ''))
    else:
        bitcoin_return = float(bitcoin_return_str)
except (ValueError, TypeError, IndexError):
    bitcoin_return = 0

def compare_returns(row):
    try:
        coin_return = float(row['percent_change90d'])
        if coin_return > bitcoin_return:
            return 1
        else:
            return -1
    except (ValueError, TypeError):
        return 0

seasons_df['vs_bitcoin_90d'] = seasons_df.apply(compare_returns, axis=1)

# Count altcoin season indicator
count_1 = seasons_df['vs_bitcoin_90d'].value_counts().get(1, 0)
count_minus_1 = seasons_df['vs_bitcoin_90d'].value_counts().get(-1, 0)

alt_season_value = 'YES' if count_1 > 72 else 'NO'
gll['alt_season'] = alt_season_value
gll['colour_alt_season'] = color_code_yes_no(alt_season_value)

print("Market Overview processed successfully")

# ==================== PUSH TO GOOGLE SHEETS ====================

print("\nPushing data to Google Sheets...")

spreadsheet_key = '1Ppif1y284fLPVIIoRzAXbPi9eUXzAyjOBr5DR-6XjSM'

# Push all dataframes to their respective sheets
safe_push_to_gsheet(df_gsheet, 'Top50Coins', spreadsheet_key)
safe_push_to_gsheet(merged_df, 'TopGainer/TopLosers', spreadsheet_key)
safe_push_to_gsheet(top_1_cc, 'BTC_SNAPSHOT', spreadsheet_key)
safe_push_to_gsheet(top_10_bearish, 'ShortOpportunities', spreadsheet_key)
safe_push_to_gsheet(top_10_bullish, 'LongOpportunities', spreadsheet_key)
safe_push_to_gsheet(gll, 'MarketOverview', spreadsheet_key)

print("\n" + "="*50)
print("ALL PROCESSING COMPLETED SUCCESSFULLY")
print("="*50)

# Close database connection
con.close()
print("Database connection closed.")
