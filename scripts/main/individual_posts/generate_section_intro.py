#!/usr/bin/env python3
"""
Generate Section Intro Slides - Reusable section dividers for mega-carousel
Creates 4 section intro slides with different themes and colors
"""

import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

# Load environment variables
load_dotenv()

from scripts.main.content.template_engine import TemplateRenderer
from scripts.main.media.screenshot import generate_image_from_html

# Section Configurations
SECTIONS = {
    'bitcoin': {
        'section_number': '01',
        'section_color': 'orange',
        'section_emoji': '₿',
        'section_title': 'Bitcoin & Market Intelligence',
        'section_description': 'Deep dive into Bitcoin price action, market sentiment, and macro intelligence with Fear & Greed Index tracking.',
        'expect_items': [
            'Fear & Greed Index with dual-axis Bitcoin price chart',
            '30-day historical trend analysis',
            'Market sentiment classification (Extreme Fear to Extreme Greed)',
            'Key price levels and momentum indicators'
        ],
        'stats': None
    },
    'trading': {
        'section_number': '02',
        'section_color': 'purple',
        'section_emoji': '📊',
        'section_title': 'Trading Opportunities',
        'section_description': 'Algorithmic trading signals powered by DMV scoring: Durability, Momentum, and Valuation metrics.',
        'expect_items': [
            'Long Call Positions: High momentum + strong valuation',
            'Short Call Positions: Weak momentum + overvalued assets',
            'DMV composite scores for data-driven decisions',
            'Price targets and 24h performance tracking'
        ],
        'stats': None
    },
    'movers': {
        'section_number': '03',
        'section_color': 'green',
        'section_emoji': '🚀',
        'section_title': 'Market Movers',
        'section_description': 'Track the biggest winners and losers in the crypto market over the last 24 hours.',
        'expect_items': [
            'Top Gainers: Assets up +2% or more',
            'Top Losers: Assets down -2% or more',
            'Real-time price and percentage changes',
            'Market cap rankings for context'
        ],
        'stats': None
    },
    'top_cryptos': {
        'section_number': '04',
        'section_color': 'blue',
        'section_emoji': '💎',
        'section_title': 'Top Cryptocurrencies',
        'section_description': 'Comprehensive market cap rankings from #2 to #48, excluding Bitcoin (covered separately).',
        'expect_items': [
            'Ranks 2-24: Major altcoins and DeFi leaders',
            'Ranks 25-48: Emerging projects and mid-cap gems',
            'DMV scores for quality assessment',
            'Price, market cap, and 24h performance data'
        ],
        'stats': None
    }
}

async def generate_section_intro(section_key):
    """Generate a single section intro slide"""
    if section_key not in SECTIONS:
        print(f"❌ Unknown section: {section_key}")
        return False

    section = SECTIONS[section_key]
    print(f"📸 Generating Section Intro: {section['section_title']}...")

    try:
        # Initialize template renderer
        renderer = TemplateRenderer()

        # Prepare output paths
        output_dir = Path(__file__).parent.parent.parent.parent / 'output_html'
        output_html = output_dir / f'section_intro_{section_key}_output.html'
        output_image = Path(__file__).parent.parent.parent.parent / 'output_images' / f'section_intro_{section_key}_output.jpg'

        # Ensure directories exist
        output_dir.mkdir(parents=True, exist_ok=True)
        output_image.parent.mkdir(parents=True, exist_ok=True)

        # Render template
        html_content = renderer.render_template('section_intro.html', section)

        if not html_content:
            print(f"❌ Failed to render section intro template for {section_key}")
            return False

        # Save HTML
        with open(output_html, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"✅ Section intro HTML generated: {output_html}")

        # Copy CSS files to output_html directory
        import shutil
        base_templates_dir = Path(__file__).parent.parent.parent.parent / 'base_templates'
        css_files = ['style_section_intro.css', 'style_base.css']

        for css_file in css_files:
            css_source = base_templates_dir / css_file
            css_dest = output_dir / css_file
            if css_source.exists() and not css_dest.exists():
                shutil.copy2(css_source, css_dest)
                print(f"📁 Copied {css_file} to output_html directory")

        # Generate screenshot
        await generate_image_from_html(
            output_html_file=str(output_html),
            output_image_path=str(output_image)
        )
        print(f"✅ Section intro screenshot generated: {output_image}")

        return True

    except Exception as e:
        print(f"❌ Error generating section intro for {section_key}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def generate_all_section_intros():
    """Generate all 4 section intro slides"""
    print("🎬 Generating All Section Intro Slides...")
    print("=" * 60)

    results = {}
    for section_key in ['bitcoin', 'trading', 'movers', 'top_cryptos']:
        results[section_key] = await generate_section_intro(section_key)
        print()

    print("=" * 60)
    print("📊 Generation Summary:")
    for section_key, success in results.items():
        status = "✅ Success" if success else "❌ Failed"
        print(f"  {status}: {SECTIONS[section_key]['section_title']}")

    all_success = all(results.values())
    if all_success:
        print("\n🎉 All section intro slides generated successfully!")
    else:
        print("\n⚠️  Some section intros failed to generate")

    return all_success

def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        # Generate specific section
        section_key = sys.argv[1]
        result = asyncio.run(generate_section_intro(section_key))
    else:
        # Generate all sections
        result = asyncio.run(generate_all_section_intros())

    return 0 if result else 1

if __name__ == "__main__":
    sys.exit(main())
