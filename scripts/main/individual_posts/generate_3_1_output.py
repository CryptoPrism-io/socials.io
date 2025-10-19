#!/usr/bin/env python3
"""
Generate 3_1_output.html - Top Gainers (+2% or more)
Individual post generator for Template 3.1
"""

import os
import sys
import asyncio
import shutil
from datetime import datetime

# Add parent directories to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from data.database import fetch_top_coins
from content.template_engine import get_template_renderer
from media.screenshot import generate_image_from_html

def generate_3_1_output():
    """Generate Template 3.1: Top Gainers (+2% or more)"""
    print("🚀 Generating Template 3.1: Top Gainers (+2% or more)")

    try:
        # Fetch data for top 100 coins for analysis
        df = fetch_top_coins(1, 100)

        if df.empty:
            print("❌ No data available for Template 3.1")
            return False

        # Filter for gainers with >2% increase
        gainers_df = df[df['percent_change24h'] > 2.0].nlargest(15, 'percent_change24h')

        # Get template renderer
        renderer = get_template_renderer()

        # Prepare output paths
        output_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'output_html')
        output_path = os.path.join(output_dir, "09_movers_gainers_output.html")

        # Fix logo handling - replace nan/null values with placeholder
        if not gainers_df.empty:
            gainers_df['logo'] = gainers_df['logo'].fillna('https://via.placeholder.com/40x40?text=?')
            gainers_df['logo'] = gainers_df['logo'].replace('nan', 'https://via.placeholder.com/40x40?text=?')

        # Split gainers into two columns (5 left, 5 right)
        if not gainers_df.empty:
            total_gainers = len(gainers_df)
            left_gainers = gainers_df.iloc[0:5].to_dict(orient='records') if total_gainers > 0 else []
            right_gainers = gainers_df.iloc[5:10].to_dict(orient='records') if total_gainers > 5 else []
        else:
            left_gainers = []
            right_gainers = []

        # Prepare template data
        template_data = {
            'gainers': gainers_df.to_dict(orient='records') if not gainers_df.empty else [],
            'left_gainers': left_gainers,
            'right_gainers': right_gainers,
            'current_date': datetime.now().strftime('%d %b, %Y'),
            'current_time': datetime.now().strftime('%I:%M %p').lower()
        }

        # Render template using generic render method
        from jinja2 import Environment, FileSystemLoader
        template_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'base_templates')
        env = Environment(loader=FileSystemLoader(template_dir))
        template = env.get_template('3_1.html')

        html_content = template.render(**template_data)

        # Write HTML file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"✅ Template 3.1 HTML generated: {output_path}")

        # Copy CSS file to output_html directory (always copy to get latest changes)
        css_source = os.path.join(template_dir, 'style3.css')
        css_dest = os.path.join(output_dir, 'style3.css')
        if os.path.exists(css_source):
            shutil.copy2(css_source, css_dest)
            print(f"📁 Copied style3.css to output_html directory")

        return True

    except Exception as e:
        print(f"❌ Template 3.1 generation error: {str(e)}")
        return False

async def generate_3_1_with_screenshot():
    """Generate Template 3.1 with screenshot"""
    print("📸 Generating Template 3.1 with screenshot...")

    # Generate HTML
    html_success = generate_3_1_output()
    if not html_success:
        return False

    # Generate screenshot
    try:
        output_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'output_html')
        image_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'output_images')
        output_path = os.path.join(output_dir, "09_movers_gainers_output.html")
        image_path = os.path.join(image_dir, "09_movers_gainers_output.jpg")

        await generate_image_from_html(output_path, image_path)
        print(f"✅ Template 3.1 screenshot generated: {image_path}")
        return True

    except Exception as e:
        print(f"❌ Template 3.1 screenshot error: {str(e)}")
        return False

if __name__ == "__main__":
    # Run with screenshot generation
    result = asyncio.run(generate_3_1_with_screenshot())

    if result:
        print("🎉 Template 3.1 generation completed successfully!")
    else:
        print("💥 Template 3.1 generation failed!")
        sys.exit(1)