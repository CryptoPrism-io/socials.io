import asyncio
from playwright.async_api import async_playwright
import pandas as pd
from sqlalchemy import create_engine
import os
from jinja2 import Environment, FileSystemLoader

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

# Data for page 1
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

        gcp_engine.dispose()
        
    except Exception as e:
        print(f"Error fetching data: {e}")
        top_100_cc = pd.DataFrame()  # Return an empty DataFrame in case of error
    return top_100_cc

# PAGE 1

import asyncio
from playwright.async_api import async_playwright
import pandas as pd
from jinja2 import Environment, FileSystemLoader

async def render_page_1():
    """Fetch data and render the HTML page using Jinja2, then convert the HTML to an image using Playwright."""
    # Fetch the data using the previously defined function
    coins = fetch_data_as_dataframe()

    if coins.empty:
        print("No data to render.")
        return

    # Set up Jinja2 environment
    env = Environment(loader=FileSystemLoader('instagram/templates'))
    template = env.get_template('1.html')

    # Render the template with the fetched data
    output = template.render(coins=coins.to_dict(orient='records'))

    # Save the output to an HTML file
    with open("output.html", "w") as f:
        f.write(output)

    print("Rendered page saved as 'output.html'.")

    # Use Playwright to convert the HTML file to an image
    await generate_image_from_html()

async def generate_image_from_html():
    """Launch Playwright, load the HTML file, and save a screenshot of it."""
    async with async_playwright() as p:
        # Launch a browser
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        await page.set_viewport_size({"width": 1080, "height": 1080})

        # Load the rendered HTML file
        await page.goto('file://' + os.path.abspath('output.html'))

        # Capture the screenshot of the page
        await page.screenshot(path='output_image.png')

        print("Screenshot saved as 'output_image.png'.")

        # Close the browser
        await browser.close()




if __name__=="__main__":

    asyncio.run(render_page_1())





