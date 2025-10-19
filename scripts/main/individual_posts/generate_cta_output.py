#!/usr/bin/env python3
"""
Generate CTA Slide - Call to Action
Final slide of the mega-carousel with follow/save/share prompts
"""

import os
import sys
import asyncio
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

# Load environment variables
load_dotenv()

from scripts.main.content.template_engine import TemplateRenderer
from scripts.main.media.screenshot import generate_image_from_html

async def generate_cta_output():
    """Generate CTA slide with call to action"""
    print("📸 Generating CTA Slide...")
    print("🎬 Creating final call-to-action card...")

    try:
        # Get current date
        now = datetime.now()
        current_date = now.strftime("%d %b, %Y")

        # Prepare template context
        context = {
            'current_date': current_date
        }

        # Initialize template renderer
        renderer = TemplateRenderer()

        # Prepare output paths
        output_dir = Path(__file__).parent.parent.parent.parent / 'output_html'
        output_html = output_dir / '14_cta_output.html'
        output_image = Path(__file__).parent.parent.parent.parent / 'output_images' / '14_cta_output.jpg'

        # Ensure directories exist
        output_dir.mkdir(parents=True, exist_ok=True)
        output_image.parent.mkdir(parents=True, exist_ok=True)

        # Render template
        html_content = renderer.render_template('cta.html', context)

        if not html_content:
            print("❌ Failed to render CTA template")
            return False

        # Save HTML
        with open(output_html, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"✅ CTA HTML generated: {output_html}")

        # Copy CSS files to output_html directory
        import shutil
        base_templates_dir = Path(__file__).parent.parent.parent.parent / 'base_templates'
        css_files = ['style_cta.css', 'style_base.css']

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
        print(f"✅ CTA screenshot generated: {output_image}")
        print("🎉 CTA slide generation completed successfully!")

        return True

    except Exception as e:
        print(f"❌ Error generating CTA slide: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main entry point"""
    result = asyncio.run(generate_cta_output())
    return 0 if result else 1

if __name__ == "__main__":
    sys.exit(main())
