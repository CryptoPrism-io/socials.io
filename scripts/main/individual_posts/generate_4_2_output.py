#!/usr/bin/env python3
"""
Generate 4_2_output.html - Short Call Positions
Individual post generator for Template 4.2
Uses sentiment analysis and trading ratios to identify bearish opportunities
"""

import os
import sys
import asyncio
from datetime import datetime

# Add parent directories to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from data.database import fetch_trading_opportunities
from content.template_engine import get_template_renderer
from media.screenshot import generate_image_from_html

def generate_4_2_output():
    """Generate Template 4.2: Short Call Positions"""
    print("🚀 Generating Template 4.2: Short Call Positions")

    try:
        # Fetch short trading opportunities (top 10 for 2-column display: 5 left, 5 right)
        short_df = fetch_trading_opportunities("short", 10)

        if short_df.empty:
            print("❌ No short call opportunities data available")
            return False

        # Prepare output paths
        output_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'output_html')
        output_path = os.path.join(output_dir, "07_trading_short_calls_output.html")

        # Fix logo handling - replace nan/null values with placeholder
        if not short_df.empty:
            short_df['logo'] = short_df['logo'].fillna('https://via.placeholder.com/40x40?text=?')
            short_df['logo'] = short_df['logo'].replace('nan', 'https://via.placeholder.com/40x40?text=?')

        # Split positions into two columns (5 left, 5 right)
        if not short_df.empty:
            total_positions = len(short_df)
            left_positions = short_df.iloc[0:5].to_dict(orient='records') if total_positions > 0 else []
            right_positions = short_df.iloc[5:10].to_dict(orient='records') if total_positions > 5 else []
        else:
            left_positions = []
            right_positions = []

        # Prepare template data
        template_data = {
            'positions': short_df.to_dict(orient='records') if not short_df.empty else [],
            'left_positions': left_positions,
            'right_positions': right_positions,
            'current_date': datetime.now().strftime('%d %b, %Y'),
            'current_time': datetime.now().strftime('%I:%M %p').lower()
        }

        # Render template using Jinja2
        from jinja2 import Environment, FileSystemLoader
        template_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'base_templates')
        env = Environment(loader=FileSystemLoader(template_dir))
        template = env.get_template('4_2.html')

        html_content = template.render(**template_data)

        # Write HTML file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"✅ Template 4.2 HTML generated: {output_path}")
        return True

    except Exception as e:
        print(f"❌ Template 4.2 generation error: {str(e)}")
        return False

async def generate_4_2_with_screenshot():
    """Generate Template 4.2 with screenshot"""
    print("📸 Generating Template 4.2 with screenshot...")

    # Generate HTML
    html_success = generate_4_2_output()
    if not html_success:
        return False

    # Generate screenshot
    try:
        output_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'output_html')
        image_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'output_images')
        output_path = os.path.join(output_dir, "07_trading_short_calls_output.html")
        image_path = os.path.join(image_dir, "07_trading_short_calls_output.jpg")

        await generate_image_from_html(output_path, image_path)
        print(f"✅ Template 4.2 screenshot generated: {image_path}")
        return True

    except Exception as e:
        print(f"❌ Template 4.2 screenshot error: {str(e)}")
        return False

if __name__ == "__main__":
    # Run with screenshot generation
    result = asyncio.run(generate_4_2_with_screenshot())

    if result:
        print("🎉 Template 4.2 generation completed successfully!")
    else:
        print("💥 Template 4.2 generation failed!")
        sys.exit(1)