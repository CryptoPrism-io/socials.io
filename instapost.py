import asyncio
from playwright.async_api import async_playwright
import pandas as pd
from sqlalchemy import create_engine
import os
from jinja2 import Environment, FileSystemLoader
from instagrapi import Client
from datetime import datetime

#commitcheck

# Database connection configuration
DB_CONFIG = {
    'host': '34.55.195.199',        # GCP PostgreSQL instance public IP
    'database': 'dbcp',             # Database name
    'user': 'yogass09',             # Username
    'password': 'jaimaakamakhya',   # Password
    'port': 5432                    # PostgreSQL default port
}

def get_gcp_engine():
    """Create and return a SQLAlchemy engine for the GCP PostgreSQL database."""
    connection_url = f"postgresql+psycopg2://{DB_CONFIG['user']}:{DB_CONFIG['password']}@" \
                     f"{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
    return create_engine(connection_url)

# Initialize the GCP engine
gcp_engine = get_gcp_engine()

async def generate_image_from_html(output_html_file, output_image_path):
    """Launch Playwright, load the HTML file, and save a screenshot of it."""
    async with async_playwright() as p:
        # Launch a browser
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        await page.set_viewport_size({"width": 1080, "height": 1080})

        # Load the rendered HTML file
        await page.goto('file://' + os.path.abspath(output_html_file))

        # Capture the screenshot of the page
        await page.screenshot(path=output_image_path)

        print(f"Screenshot saved as {output_image_path}.")

        # Close the browser
        await browser.close()



# Data for page 1 & 2
def fetch_data_as_dataframe():
    """Fetch data from the 'coins' table and return as a Pandas DataFrame."""
    query_top_100 = """
      SELECT slug, cmc_rank, last_updated, symbol, price, percent_change24h, market_cap, last_updated
      FROM crypto_listings_latest_1000
      WHERE cmc_rank < 50
      """
    
    try:
        # Use gcp_engine to execute the query and fetch data as a DataFrame
        top_100_cc  = pd.read_sql_query(query_top_100, gcp_engine)
        # Convert market_cap to billions and round to 2 decimal places
        top_100_cc['market_cap'] = (top_100_cc['market_cap'] / 1_000_000_000).round(2)
        top_100_cc['price'] = (top_100_cc['price']).round(2)
        top_100_cc['percent_change24h'] = (top_100_cc['percent_change24h']).round(2)

        # Create a list of slugs from the top_100_crypto DataFrame
        slugs = top_100_cc['slug'].tolist()
        # Prepare a string for the IN clause
        slugs_placeholder = ', '.join(f"'{slug}'" for slug in slugs)

        # Construct the SQL query
        query_logos = f"""
        SELECT logo, slug FROM "FE_CC_INFO_URL"
        WHERE slug IN ({slugs_placeholder})
        """

        # Execute the query and fetch the data into a DataFrame
        logos_and_slugs = pd.read_sql_query(query_logos, gcp_engine)

        # Merge the two DataFrames on the 'slug' column
        top_100_cc = pd.merge(top_100_cc, logos_and_slugs, on='slug', how='left')

        top_100_cc = top_100_cc.sort_values(by='cmc_rank', ascending=True)

        gcp_engine.dispose()
        
    except Exception as e:
        print(f"Error fetching data: {e}")
        top_100_cc = pd.DataFrame()  # Return an empty DataFrame in case of error
    return top_100_cc

# Data for BTC snapshot
def btc_snapshot():
    # @title bitcoing data only
  query_top_1 = """
  SELECT slug, cmc_rank, last_updated, symbol, price, percent_change24h, volume24h, market_cap, percent_change7d, percent_change30d, ytd_price_change_percentage
  FROM crypto_listings_latest_1000
  WHERE cmc_rank < 2
  """
  top_1_cc  = pd.read_sql_query(query_top_1, gcp_engine)
  
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


  # Format the 'tg_percent_change24h' column with 2 decimal places and add '%'
  top_1_cc['percent_change24h'] = top_1_cc['percent_change24h'].apply(lambda x: f"{x:.2f}" if not pd.isnull(x) else x)
  top_1_cc['percent_change7d'] = top_1_cc['percent_change7d'].apply(lambda x: f"{x:.2f}" if not pd.isnull(x) else x)
  top_1_cc['percent_change30d'] = top_1_cc['percent_change30d'].apply(lambda x: f"{x:.2f}" if not pd.isnull(x) else x)
  top_1_cc['ytd_price_change_percentage'] = top_1_cc['ytd_price_change_percentage'].apply(lambda x: f"{x:.2f}" if not pd.isnull(x) else x)

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
  dmv_bitcoin = pd.read_sql_query(query, gcp_engine)

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

    # Construct the SQL query
  query = f"""
  SELECT logo, slug FROM "FE_CC_INFO_URL"
  """

  # Execute the query and fetch the data into a DataFrame
  logos_and_slugs = pd.read_sql_query(query, gcp_engine)

  # Merge the two DataFrames on the 'slug' column
  top_1_cc = pd.merge(top_1_cc, logos_and_slugs, on='slug', how='left')

  return top_1_cc
  
  

# fetch for page 3
def fetch_for_3():
    """Fetch data from the 'coins' table and return as a Pandas DataFrame."""
    query_top_500 = """
      SELECT slug, cmc_rank, last_updated, symbol, price, percent_change24h, market_cap, last_updated
      FROM crypto_listings_latest_1000
      WHERE cmc_rank < 500
      """
    
    try:
        # Use gcp_engine to execute the query and fetch data as a DataFrame
        top_500_cc  = pd.read_sql_query(query_top_500, gcp_engine)
        # Convert market_cap to billions and round to 2 decimal places
        top_500_cc['market_cap'] = (top_500_cc['market_cap'] / 1_000_000_000).round(2)
        top_500_cc['price'] = (top_500_cc['price']).round(2)
        top_500_cc['percent_change24h'] = (top_500_cc['percent_change24h']).round(2)

        # Create a list of slugs from the top_100_crypto DataFrame
        slugs = top_500_cc['slug'].tolist()
        # Prepare a string for the IN clause
        slugs_placeholder = ', '.join(f"'{slug}'" for slug in slugs)

        # Construct the SQL query
        query_logos = f"""
        SELECT logo, slug FROM "FE_CC_INFO_URL"
        WHERE slug IN ({slugs_placeholder})
        """
        query_dmv = f"""
        SELECT *
        FROM "FE_DMV_SCORES"
        """
        
        # Execute the query and fetch data for dmv
        dmv = pd.read_sql_query(query_dmv, gcp_engine)

        # Execute the query and fetch the data into a DataFrame
        logos_and_slugs = pd.read_sql_query(query_logos, gcp_engine)

        # Merge the two DataFrames on the 'slug' column
        top_500_cc = pd.merge(top_500_cc, logos_and_slugs, on='slug', how='left')
        top_500_cc = pd.merge(top_500_cc, dmv, on='slug', how='left')

        top_500_cc['Durability_Score'] = (top_500_cc['Durability_Score']).round(2)
        top_500_cc['Momentum_Score'] = (top_500_cc['Momentum_Score']).round(2)
        top_500_cc['Valuation_Score'] = (top_500_cc['Valuation_Score']).round(2)

        gcp_engine.dispose()
        
    except Exception as e:
        print(f"Error fetching data: {e}")
        top_500_cc = pd.DataFrame()  # Return an empty DataFrame in case of error
    return top_500_cc

def fetch_for_4_long():
    """Fetch data from the 'coins' table and return as a Pandas DataFrame."""
    query_long_short = """
SELECT
  "FE_DMV_ALL"."id",
  "FE_DMV_ALL"."slug",
  "FE_DMV_ALL"."name",
  "FE_DMV_ALL"."bullish",
  "FE_DMV_ALL"."bearish",
  "crypto_listings_latest_1000"."symbol",
  "crypto_listings_latest_1000"."percent_change24h",
  "crypto_listings_latest_1000"."percent_change7d",
  "crypto_listings_latest_1000"."percent_change30d",
  "crypto_listings_latest_1000"."cmc_rank",
  "crypto_listings_latest_1000"."price",
  "crypto_listings_latest_1000"."market_cap",
  "FE_CC_INFO_URL"."logo",
  "FE_RATIOS"."m_rat_alpha",
  "FE_RATIOS"."d_rat_beta",
  "FE_RATIOS"."m_rat_omega"
FROM
  "FE_DMV_ALL"
JOIN
  "crypto_listings_latest_1000"
ON
  "FE_DMV_ALL"."slug" = "crypto_listings_latest_1000"."slug"
JOIN
  "FE_CC_INFO_URL"
ON
  "FE_DMV_ALL"."slug" = "FE_CC_INFO_URL"."slug"
JOIN
  "FE_RATIOS"
ON
  "FE_DMV_ALL"."slug" = "FE_RATIOS"."slug"
WHERE
  "crypto_listings_latest_1000"."cmc_rank" < 100
  AND "FE_RATIOS"."d_rat_beta" > 1
  AND "FE_RATIOS"."m_rat_omega" > 1
ORDER BY
  "FE_DMV_ALL"."bullish" DESC
LIMIT
  15;
"""

    
    try:
        # Use gcp_engine to execute the query and fetch data as a DataFrame
        long_short  = pd.read_sql_query(query_long_short, gcp_engine)
        # Convert market_cap to billions and round to 2 decimal places
        long_short['market_cap'] = (long_short['market_cap'] / 1_000_000_000).round(2)
        long_short['price'] = (long_short['price']).round(2)
        long_short['percent_change24h'] = (long_short['percent_change24h']).round(2)
        long_short['percent_change7d'] = (long_short['percent_change7d']).round(2)
        long_short['percent_change30d'] = (long_short['percent_change30d']).round(2)

        long_short['m_rat_alpha'] = (long_short['m_rat_alpha']).round(2)
        long_short['d_rat_beta'] = (long_short['d_rat_beta']).round(2)
        long_short['m_rat_omega'] = (long_short['m_rat_omega']).round(2)
        
        gcp_engine.dispose()
        
    except Exception as e:
        print(f"Error fetching data: {e}")
        long_short = pd.DataFrame()  # Return an empty DataFrame in case of error
    return long_short

def fetch_for_4_short():
    """Fetch data from the 'coins' table and return as a Pandas DataFrame."""
    query_long_short = """
SELECT
  "FE_DMV_ALL"."id",
  "FE_DMV_ALL"."slug",
  "FE_DMV_ALL"."name",
  "FE_DMV_ALL"."bullish",
  "FE_DMV_ALL"."bearish",
  "crypto_listings_latest_1000"."symbol",
  "crypto_listings_latest_1000"."percent_change24h",
  "crypto_listings_latest_1000"."percent_change7d",
  "crypto_listings_latest_1000"."percent_change30d",
  "crypto_listings_latest_1000"."cmc_rank",
  "crypto_listings_latest_1000"."price",
  "crypto_listings_latest_1000"."market_cap",
  "FE_CC_INFO_URL"."logo",
  "FE_RATIOS"."m_rat_alpha",
  "FE_RATIOS"."d_rat_beta",
  "FE_RATIOS"."m_rat_omega"
FROM
  "FE_DMV_ALL"
JOIN
  "crypto_listings_latest_1000"
ON
  "FE_DMV_ALL"."slug" = "crypto_listings_latest_1000"."slug"
JOIN
  "FE_CC_INFO_URL"
ON
  "FE_DMV_ALL"."slug" = "FE_CC_INFO_URL"."slug"
JOIN
  "FE_RATIOS"
ON
  "FE_DMV_ALL"."slug" = "FE_RATIOS"."slug"
WHERE
  "crypto_listings_latest_1000"."cmc_rank" < 100
  AND "FE_RATIOS"."d_rat_beta" > 1
  AND "FE_RATIOS"."m_rat_omega" < 2
ORDER BY
  "FE_DMV_ALL"."bearish" DESC
LIMIT
  15;
"""

    
    try:
        # Use gcp_engine to execute the query and fetch data as a DataFrame
        long_short  = pd.read_sql_query(query_long_short, gcp_engine)
        # Convert market_cap to billions and round to 2 decimal places
        long_short['market_cap'] = (long_short['market_cap'] / 1_000_000_000).round(2)
        long_short['price'] = (long_short['price']).round(2)
        long_short['percent_change24h'] = (long_short['percent_change24h']).round(2)
        long_short['percent_change7d'] = (long_short['percent_change7d']).round(2)
        long_short['percent_change30d'] = (long_short['percent_change30d']).round(2)

        long_short['m_rat_alpha'] = (long_short['m_rat_alpha']).round(2)
        long_short['d_rat_beta'] = (long_short['d_rat_beta']).round(2)
        long_short['m_rat_omega'] = (long_short['m_rat_omega']).round(2)

        gcp_engine.dispose()

    except Exception as e:
        print(f"Error fetching data: {e}")
        long_short = pd.DataFrame()  # Return an empty DataFrame in case of error
    return long_short

#Fetch for 5
def fetch_for_5():
    """Fetches global cryptocurrency data from the PostgreSQL database and returns it as a Pandas DataFrame."""

    query = """
    SELECT
        total_market_cap,
        total_volume24h_reported,
        altcoin_volume24h_reported,
        altcoin_market_cap,
        total_market_cap_yesterday_percentage_change,
        total_volume24h_yesterday_percentage_change,
        derivatives_volume24h_reported,
        derivatives24h_percentage_change,
        active_crypto_currencies,
        total_crypto_currencies,
        active_exchanges,
        total_exchanges,
        stablecoin_volume24h_reported,
        stablecoin_market_cap,
        stablecoin24h_percentage_change,
        defi_volume24h_reported,
        defi_market_cap,
        defi24h_percentage_change,
        btc_dominance24h_percentage_change,
        eth_dominance24h_percentage_change,
        btc_dominance,
        eth_dominance
    FROM
        crypto_global_latest  
    """

    try:
        # Execute the query and fetch the data into a DataFrame using the pre-initialized engine
        global_data = pd.read_sql_query(query, gcp_engine)

        # Apply necessary transformations and rounding.
        # Convert market caps and volumes to billions and round to 2 decimal places
        for col in ['total_market_cap', 'total_volume24h_reported', 'altcoin_volume24h_reported', 'altcoin_market_cap', 'stablecoin_volume24h_reported', 'stablecoin_market_cap', 'defi_volume24h_reported', 'defi_market_cap', 'derivatives_volume24h_reported']:
            global_data[col] = (global_data[col] / 1_000_000_000).round(2)

        # Round percentage change columns to 2 decimal places
        for col in ['total_market_cap_yesterday_percentage_change', 'total_volume24h_yesterday_percentage_change', 'derivatives24h_percentage_change', 'stablecoin24h_percentage_change', 'defi24h_percentage_change', 'btc_dominance24h_percentage_change', 'eth_dominance24h_percentage_change', 'btc_dominance', 'eth_dominance']:
            global_data[col] = global_data[col].round(2)

        # No need to dispose of the engine here, as it's initialized globally
        return global_data

    except Exception as e:
        print(f"An error occurred: {e}")
        return None  # Or raise the exception, depending on your error handling strategy

# PAGE 1

import asyncio
from playwright.async_api import async_playwright
import pandas as pd
from jinja2 import Environment, FileSystemLoader

async def render_page_1():
    """Fetch data and render the HTML page using Jinja2, then convert the HTML to an image using Playwright."""
    # Fetch the data using the previously defined function
    coins = fetch_data_as_dataframe()
    snap = btc_snapshot()
    

    if coins.empty:
        print("No data to render.")
        return

    # Set up Jinja2 environment
    env = Environment(loader=FileSystemLoader(os.getcwd()))  # Loads from the current directory
    template = env.get_template('1.html')

    
    # Render the template with the fetched data
    output = template.render(coins=coins.to_dict(orient='records'), snap=snap.to_dict(orient='records'))

    # Save the output to an HTML file
    with open("1_output.html", "w") as f:
        f.write(output)

    print("Rendered page saved as 'output.html'.")

    # Use Playwright to convert the HTML file to an image
    await generate_image_from_html("1_output.html", "1_output.jpg")
    #cl = Client()  # Directly initialize the client

    """try:
        # Directly login with credentials
        cl.login("cryptoprism.io", "jaimaakamakhya")  # Replace with your actual credentials
        print("Login successful.")

        # Upload the story
        try:
            cl.photo_upload(
                path="output_image.jpg",
                caption="cryptoprism.io"
            )
            print("Story posted successfully!")
        except Exception as e:
            print(f"Error posting story: {e}")

    except Exception as e:
        print(f"Error logging in: {e}")"""

# PAGE 2
async def render_page_2():
    """Fetch data and render the HTML page using Jinja2, then convert the HTML to an image using Playwright."""
    # Fetch the data using the previously defined function
    df2 = fetch_data_as_dataframe()
    df2 = df2.sort_values('cmc_rank', ascending=True)

    # Skip first 15 rows and take next 21 rows (ranks 16-36)
    df2 = df2.iloc[15:36]
    
    # Split into three DataFrames of 7 rows each
    df2_part1 = df2.iloc[0:7]    # First 7 rows (ranks 16-22)
    df2_part2 = df2.iloc[7:14]   # Next 7 rows (ranks 23-29)
    df2_part3 = df2.iloc[14:21]  # Last 7 rows (ranks 30-36)

    # Convert each DataFrame to dictionary
    coins_part1 = df2_part1.to_dict(orient='records')
    coins_part2 = df2_part2.to_dict(orient='records')
    coins_part3 = df2_part3.to_dict(orient='records')

    # Set up Jinja2 environment
    env = Environment(loader=FileSystemLoader(os.getcwd())) 
    template = env.get_template('2.html')

    # Render the template with the fetched data
    output = template.render(coins1=coins_part1, 
                         coins2=coins_part2, 
                         coins3=coins_part3)

    # Save the output to an HTML file
    with open("2_output.html", "w") as f:
        f.write(output)

    print("Rendered page saved as 'output.html'.")

    # Use Playwright to convert the HTML file to an image
    await generate_image_from_html("2_output.html", "2_output.jpg")

# PAGE 3
async def render_page_3():
    """Fetch data and render the HTML page using Jinja2, then convert the HTML to an image using Playwright."""
    # Fetch the data using the previously defined function
    df3 = fetch_for_3()
    df3.head()
    
    df3l = df3.sort_values('percent_change24h', ascending=True)  # top losers
    df3l = df3l.iloc[0:4]
    df3g = df3.sort_values('percent_change24h', ascending=False)  # top gainers
    df3g = df3g.iloc[0:4]  # get first 4 rows (highest percent change)

    df3l_new = df3l.to_dict(orient='records')
    df3g_new = df3g.to_dict(orient='records')

    # Set up Jinja2 environment
    env = Environment(loader=FileSystemLoader(os.getcwd())) 
    template = env.get_template('3.html')

    # Render the template with the fetched data
    output = template.render(coin1=df3l_new, 
                             coin2=df3g_new)

    # Save the output to an HTML file
    with open("3_output.html", "w") as f:
        f.write(output)

    print("Rendered page saved as 'output.html'.")

    # Use Playwright to convert the HTML file to an image
    await generate_image_from_html("3_output.html", '3_output.jpg')

#PAGE 4
async def render_page_4():
    """Fetch data and render the HTML page using Jinja2, then convert the HTML to an image using Playwright."""
    # Fetch the data using the previously defined function
    long_short = fetch_for_4_long()
    short = fetch_for_4_short()
    
    # Create DataFrame for long positions (sorted by bullish in descending order)
    df_long = long_short.sort_values('bullish', ascending=False)
    df_long = df_long.head(4)
    # Create DataFrame for short positions (sorted by bearish in ascending order)
    df_short = short.sort_values('bearish', ascending=True)
    df_short = df_short.head(4)

    # Convert DataFrames to dictionaries for template rendering
    long_positions = df_long.to_dict(orient='records')
    short_positions = df_short.to_dict(orient='records')

    # Set up Jinja2 environment
    env = Environment(loader=FileSystemLoader(os.getcwd())) 
    template = env.get_template('4.html')

    # Render the template with the fetched data
    output = template.render(coins1=long_positions,
                             coins2=short_positions)

    # Save the output to an HTML file
    with open("4_output.html", "w", encoding="utf-8") as f:
        f.write(output)

    print("Rendered page saved as '4_output.html'.")

    # Use Playwright to convert the HTML file to an image
    await generate_image_from_html("4_output.html", '4_output.jpg')

# PAGE 5
async def render_page_5():
    """Fetch data and render the HTML page using Jinja2, then convert the HTML to an image using Playwright."""
    
    #fetch
    global_data = fetch_for_5()
    coins = global_data.to_dict(orient='records')
    

    now = datetime.now()
    formatted_date = now.strftime("%d %b, %Y")  # Example: 15 Feb, 2025
    formatted_time = now.strftime("%I:%M:%S %p")  # Example: 02:07:45 PM Monday

    # Set up Jinja2 environment
    env = Environment(loader=FileSystemLoader(os.getcwd())) 
    template = env.get_template('5.html')

    # Render the template with the fetched data
    output = template.render(coins=coins, current_date=formatted_date, current_time=formatted_time)

    # Save the output to an HTML file
    with open("5_output.html", "w", encoding="utf-8") as f:
        f.write(output)

    print("Rendered page saved as '5_output.html'.")

    # Use Playwright to convert the HTML file to an image
    await generate_image_from_html("5_output.html", '5_output.jpg')

if __name__=="__main__":

    asyncio.run(render_page_1())
    asyncio.run(render_page_2())
    asyncio.run(render_page_3())
    asyncio.run(render_page_4())
    asyncio.run(render_page_5())

