from flask import Flask, render_template
import pandas as pd
from sqlalchemy import create_engine
import imgkit
import os


app = Flask(__name__)

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
        
    except Exception as e:
        print(f"Error fetching data: {e}")
        top_100_cc = pd.DataFrame()  # Return an empty DataFrame in case of error
    return top_100_cc

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
        
    except Exception as e:
        print(f"Error fetching data: {e}")
        top_500_cc = pd.DataFrame()  # Return an empty DataFrame in case of error
    return top_500_cc

def fetch_for_4():
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
ORDER BY
  "FE_DMV_ALL"."bullish" DESC
LIMIT
    10;
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
ORDER BY
  "FE_DMV_ALL"."bearish" ASC
LIMIT
    10;
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
        
    
        
    except Exception as e:
        print(f"Error fetching data: {e}")
        long_short = pd.DataFrame()  # Return an empty DataFrame in case of error
    return long_short
    
def render_template_to_png(template_name, output_dir, coins):
    """
    Render a Flask template with a list of dictionaries (`coins`) and save it as a PNG image.

    Parameters:
        template_name (str): The name of the HTML template to render.
        output_dir (str): The directory where the PNG image will be saved.
        coins (list): A list of dictionaries to pass to the template as `coins`.

    Returns:
        str: The file path of the generated PNG image.
    """
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Render the HTML template with the coins data
    rendered_html = render_template(template_name, coins=coins)

    # Define the output file name
    output_file = os.path.join(output_dir, f"{template_name.split('.')[0]}.png")

    # Convert the rendered HTML to PNG using imgkit
    imgkit.from_string(rendered_html, output_file)

    return output_file

@app.route('/')
def display_coins():
    """Route to display coins data on an HTML page."""
    df = fetch_data_as_dataframe()
    df = df.sort_values('cmc_rank', ascending=True)
    
    # Convert DataFrame to list of dictionaries
    coins = df.to_dict(orient='records')

    output_dir = os.path.join(os.getcwd(), 'output_images')
    output_file = render_template_to_png('index.html', output_dir, coins)

    return  render_template('index.html', coins=coins)

@app.route('/2')
def display_page2():
    """Route to display the second page with coins ranked 16-36, split into three equal parts."""
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
    
    return render_template('2.html', 
                         coins1=coins_part1, 
                         coins2=coins_part2, 
                         coins3=coins_part3)

@app.route('/3')
def display_page3():
    """Route to display the third page with coins ranked 37-57, split into three equal parts."""
    df3 = fetch_for_3()
    
    df3l = df3.sort_values('percent_change24h', ascending=True)  # top losers
    df3l = df3l.iloc[0:4]
    df3g = df3.sort_values('percent_change24h', ascending=False)  # top gainers
    df3g = df3g.iloc[0:4]  # get first 4 rows (highest percent change)

   

    df3l_new = df3l.to_dict(orient='records')
    df3g_new = df3g.to_dict(orient='records')
    
    
    return render_template('3.html', coin1=df3l_new, coin2=df3g_new)

@app.route('/4')
def display_page4():
    """Route to display the fourth page with long and short positions."""
    long_short = fetch_for_4()
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
    print(short_positions)
    
    return render_template('4.html', coins1=long_positions, coins2=short_positions)

@app.route('/5')
def display_page5():
    html5 =  render_template('5.html')
    return html5

@app.teardown_appcontext
def shutdown_session(exception=None):
    """Dispose of the database connection after each request."""
    gcp_engine.dispose()

if __name__ == '__main__':
    


    app.run(debug=True)
