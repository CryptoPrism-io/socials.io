"""Media processing and screenshot generation module using Playwright."""

import asyncio
import os
from playwright.async_api import async_playwright

async def generate_image_from_html(output_html_file, output_image_path):
    """Launch Playwright, load the HTML file, and save a screenshot of it."""
    async with async_playwright() as p:
        # Launch a browser
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        await page.set_viewport_size({"width": 2160, "height": 2700})

        # Set device scale factor for even better quality
        await page.emulate_media(media='screen')
        await page.evaluate("() => { document.body.style.zoom = '1'; }")

        # Load the rendered HTML file
        await page.goto('file://' + os.path.abspath(output_html_file))

        # Capture the screenshot of the page with high quality settings
        await page.screenshot(
            path=output_image_path,
            type='jpeg',
            quality=95,
            full_page=True
        )

        print(f"Screenshot saved as {output_image_path}.")

        # Close the browser
        await browser.close()

async def generate_multiple_screenshots(html_files, output_dir):
    """Generate screenshots for multiple HTML files."""
    os.makedirs(output_dir, exist_ok=True)

    tasks = []
    for html_file in html_files:
        if os.path.exists(html_file):
            base_name = os.path.splitext(os.path.basename(html_file))[0]
            output_path = os.path.join(output_dir, f"{base_name}.jpg")
            tasks.append(generate_image_from_html(html_file, output_path))

    if tasks:
        await asyncio.gather(*tasks)
        print(f"Generated {len(tasks)} screenshots in {output_dir}")
    else:
        print("No valid HTML files found for screenshot generation")

def create_placeholder_image(output_path, slide_number=1, size=(1080, 1080)):
    """Create a placeholder image when content is not available."""
    from PIL import Image, ImageDraw, ImageFont

    img = Image.new('RGB', size, color=(20, 20, 30))
    draw = ImageDraw.Draw(img)

    try:
        # Try to use a better font
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
    except:
        try:
            # Windows font fallback
            font = ImageFont.truetype("arial.ttf", 60)
        except:
            font = ImageFont.load_default()

    text = f"Crypto Update\nSlide {slide_number}"
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    x = (size[0] - text_width) // 2
    y = (size[1] - text_height) // 2

    draw.text((x, y), text, fill=(255, 255, 255), font=font, align="center")
    img.save(output_path)
    print(f"Created placeholder image: {output_path}")

def prepare_media_files(output_dir, num_slides=6):
    """Prepare media files for Instagram upload, creating placeholders if needed."""
    from pathlib import Path

    media_files = []
    output_path = Path(output_dir)

    for i in range(1, num_slides + 1):
        file_path = output_path / f"{i}_output.jpg"
        if file_path.exists():
            media_files.append(file_path)
            print(f"✅ Found {file_path}")
        else:
            print(f"⚠️  {file_path} not found. Creating placeholder...")
            create_placeholder_image(str(file_path), i)
            media_files.append(file_path)

    print(f"✅ Prepared {len(media_files)} media files")
    return media_files

async def screenshot_workflow(html_output_dir, image_output_dir, num_pages=6):
    """Complete screenshot generation workflow for all pages."""
    html_files = []

    for i in range(1, num_pages + 1):
        html_file = os.path.join(html_output_dir, f"{i}_output.html")
        html_files.append(html_file)

    await generate_multiple_screenshots(html_files, image_output_dir)
    return prepare_media_files(image_output_dir, num_pages)