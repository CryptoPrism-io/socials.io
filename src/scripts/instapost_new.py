"""
Updated Instagram post script that uses new path structure.
Can be run from project root and will use the structured directories.
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

# Add config to path
sys.path.insert(0, str(Path(__file__).parent))

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

def setup_jinja_environment():
    """Set up Jinja2 environment with new template directory."""
    return Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))

# Import all the data functions from the original script
# Note: You would need to copy all the data fetching functions here
# (fetch_data_as_dataframe, btc_snapshot, btc_losers, btc_gainers, etc.)

def main():
    """Main function that mimics the original script behavior."""
    print("Running restructured Instagram post generation...")

    # Ensure all directories exist
    ensure_directories()

    print("Directory structure ready!")
    print(f"Templates: {TEMPLATES_DIR}")
    print(f"HTML Output: {HTML_OUTPUT_DIR}")
    print(f"Images Output: {IMAGES_OUTPUT_DIR}")

if __name__ == "__main__":
    main()