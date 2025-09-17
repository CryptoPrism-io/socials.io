"""
Restructured Instagram post generation script.
Uses new path configuration for better organization.
"""
import asyncio
from playwright.async_api import async_playwright
import pandas as pd
from sqlalchemy import create_engine
import os
import sys
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from instagrapi import Client
from datetime import datetime

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import path configuration
from config.paths import (
    TEMPLATES_DIR, HTML_OUTPUT_DIR, IMAGES_OUTPUT_DIR,
    get_html_output_path, get_image_output_path, ensure_directories
)

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
    # Ensure output directories exist
    ensure_directories()

    async with async_playwright() as p:
        # Launch a browser
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        await page.set_viewport_size({"width": 1080, "height": 1080})

        # Load the rendered HTML file - use absolute path
        html_path = Path(output_html_file).absolute()
        await page.goto(f'file://{html_path}')

        # Ensure image output directory exists
        image_path = Path(output_image_path)
        image_path.parent.mkdir(parents=True, exist_ok=True)

        # Capture the screenshot of the page
        await page.screenshot(path=str(image_path))

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

def setup_jinja_environment():
    """Set up Jinja2 environment with new template directory."""
    return Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))

async def render_page_1():
    """Fetch data and render the HTML page using Jinja2, then convert the HTML to an image using Playwright."""
    # Ensure directories exist
    ensure_directories()

    # Fetch data
    btc_df = btc_snapshot()
    losers = btc_losers()
    top100 = fetch_data_as_dataframe()
    gainerss = btc_gainers()

    # Set up Jinja2 environment with new template directory
    env = setup_jinja_environment()
    template = env.get_template('1.html')

    # Render the template with the fetched data
    rendered_html = template.render(
        snap=btc_df.to_dict('records'),
        gainer=gainerss.to_dict('records'),
        loser=losers.to_dict('records'),
        t100=top100.to_dict('records')
    )

    # Save rendered HTML to new output directory
    output_html_path = get_html_output_path(1)
    with open(output_html_path, 'w', encoding='utf-8') as f:
        f.write(rendered_html)

    print(f"Rendered HTML saved as {output_html_path}")

    # Generate image from HTML using new paths
    output_image_path = get_image_output_path(1)
    await generate_image_from_html(str(output_html_path), str(output_image_path))

async def render_page_2():
    """Render page 2 using new path structure."""
    ensure_directories()

    # Fetch data (same logic as original)
    top100 = fetch_data_as_dataframe()

    # Set up Jinja2 environment
    env = setup_jinja_environment()
    template = env.get_template('2.html')

    # Render the template
    rendered_html = template.render(
        top100=top100.to_dict('records')
    )

    # Save rendered HTML
    output_html_path = get_html_output_path(2)
    with open(output_html_path, 'w', encoding='utf-8') as f:
        f.write(rendered_html)

    print(f"Rendered HTML saved as {output_html_path}")

    # Generate image
    output_image_path = get_image_output_path(2)
    await generate_image_from_html(str(output_html_path), str(output_image_path))

# Note: This is a restructured version with only the key functions shown.
# The complete script would include all the missing functions like btc_snapshot(),
# btc_losers(), btc_gainers(), etc. from the original file.

def main():
    """Main function to test restructured functionality."""
    print("Testing restructured Instagram post generation...")

    # Test that we can set up Jinja environment
    try:
        env = setup_jinja_environment()
        print("+ Jinja2 environment setup successful")
    except Exception as e:
        print(f"! Jinja2 environment setup failed: {e}")

    # Test path generation
    html_path = get_html_output_path(1)
    image_path = get_image_output_path(1)

    print(f"HTML output path: {html_path}")
    print(f"Image output path: {image_path}")

    print("Restructured script ready for testing!")

if __name__ == "__main__":
    main()