import os
import shutil
import time
from instagrapi import Client
from playwright.async_api import async_playwright
from dotenv import load_dotenv
import nest_asyncio
import asyncio

# Apply nest_asyncio to allow asyncio in the already running loop (for environments like Jupyter)
nest_asyncio.apply()

# Load environment variables from .env file (to securely store credentials)
load_dotenv()

# HTML content
html_content = """
<!DOCTYPE html>
<html lang='en'>
<head>
    <meta charset='UTF-8'>
    <meta name='viewport' content='width=device-width, initial-scale=1.0'>
    <title>Instagram Story</title>
    <style>
        body {
            width: 1080px;
            height: 1920px;
            background-color: white;
            display: flex;
            justify-content: center;
            align-items: center;
            font-family: Arial, sans-serif;
            font-size: 64px;
            font-weight: bold;
            color: black;
        }
    </style>
</head>
<body>
    cryptoprism.io(htmltopjg_usingplaywright)
</body>
</html>
"""

# Save HTML file
html_file = "story.html"
with open(html_file, "w", encoding="utf-8") as f:
    f.write(html_content)

# Generate Screenshot with Playwright (asynchronous version)
async def capture_screenshot():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)  # Headless mode for efficiency
        page = await browser.new_page()
        await page.set_viewport_size({"width": 1080, "height": 1920})
        await page.goto(f"file://{os.path.abspath(html_file)}")
        await page.wait_for_timeout(2000)  # Wait to render
        await page.screenshot(path="story.jpg", full_page=True)
        await browser.close()

# Main asynchronous function
async def main():
    await capture_screenshot()

# Run the asynchronous function
asyncio.run(main())

# Instagram login and photo upload section (Direct login, no settings file)
cl = Client()  # Directly initialize the client

try:
    # Directly login with credentials
    cl.login("cryptoprism.io", "jaimaakamakhya")  # Replace with your actual credentials
    print("Login successful.")

    # Upload the story
    try:
        cl.photo_upload(
            path="story.jpg",
            caption="cryptoprism.io"
        )
        print("Story posted successfully!")
    except Exception as e:
        print(f"Error posting story: {e}")

except Exception as e:
    print(f"Error logging in: {e}")
