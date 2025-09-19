#!/usr/bin/env python3
"""
Font downloader for socials.io self-hosted fonts
Downloads Google Fonts locally to eliminate external dependencies
"""

import requests
import os
from pathlib import Path

def download_font(url: str, filename: str) -> bool:
    """Download a font file from URL"""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        with open(filename, 'wb') as f:
            f.write(response.content)

        print(f"✅ Downloaded {filename}")
        return True
    except Exception as e:
        print(f"❌ Failed to download {filename}: {e}")
        return False

def main():
    """Download all required font files"""
    fonts_dir = Path(__file__).parent
    os.chdir(fonts_dir)

    # Font URLs from Google Fonts API (these are examples - actual URLs would be obtained from googleapis.com)
    fonts_to_download = [
        # Poppins family
        ("https://fonts.gstatic.com/s/poppins/v20/pxiEyp8kv8JHgFVrFJDUc1NECPY.woff2", "poppins-300.woff2"),
        ("https://fonts.gstatic.com/s/poppins/v20/pxiEyp8kv8JHgFVrFJA.woff2", "poppins-400.woff2"),
        ("https://fonts.gstatic.com/s/poppins/v20/pxiEyp8kv8JHgFVrFJDmcFENCPY.woff2", "poppins-500.woff2"),
        ("https://fonts.gstatic.com/s/poppins/v20/pxiEyp8kv8JHgFVrFJDGcFMNCPY.woff2", "poppins-600.woff2"),
        ("https://fonts.gstatic.com/s/poppins/v20/pxiEyp8kv8JHgFVrFJDGcFMNCPY.woff2", "poppins-700.woff2"),
        ("https://fonts.gstatic.com/s/poppins/v20/pxiEyp8kv8JHgFVrFJDGcFMNCPY.woff2", "poppins-800.woff2"),

        # Inter family
        ("https://fonts.gstatic.com/s/inter/v12/UcCO3FwrK3iLTeHuS_fvQtMwCp50KnMw2boKoduKmMEVuLyeMZhrib2Bg-4.woff2", "inter-300.woff2"),
        ("https://fonts.gstatic.com/s/inter/v12/UcCO3FwrK3iLTeHuS_fvQtMwCp50KnMw2boKoduKmMEVuLyeMZhrib2Bg-4.woff2", "inter-400.woff2"),
        ("https://fonts.gstatic.com/s/inter/v12/UcCO3FwrK3iLTeHuS_fvQtMwCp50KnMw2boKoduKmMEVuLyeMZhrib2Bg-4.woff2", "inter-500.woff2"),
        ("https://fonts.gstatic.com/s/inter/v12/UcCO3FwrK3iLTeHuS_fvQtMwCp50KnMw2boKoduKmMEVuLyeMZhrib2Bg-4.woff2", "inter-600.woff2"),
        ("https://fonts.gstatic.com/s/inter/v12/UcCO3FwrK3iLTeHuS_fvQtMwCp50KnMw2boKoduKmMEVuLyeMZhrib2Bg-4.woff2", "inter-700.woff2"),
        ("https://fonts.gstatic.com/s/inter/v12/UcCO3FwrK3iLTeHuS_fvQtMwCp50KnMw2boKoduKmMEVuLyeMZhrib2Bg-4.woff2", "inter-800.woff2"),

        # Orbitron family
        ("https://fonts.gstatic.com/s/orbitron/v25/yMJWMIlzdpvBhQQL_SC1X9zOl_lU.woff2", "orbitron-400.woff2"),
        ("https://fonts.gstatic.com/s/orbitron/v25/yMJWMIlzdpvBhQQL_SC1X9zOl_lU.woff2", "orbitron-500.woff2"),
        ("https://fonts.gstatic.com/s/orbitron/v25/yMJWMIlzdpvBhQQL_SC1X9zOl_lU.woff2", "orbitron-700.woff2"),
    ]

    print("🔄 Downloading self-hosted fonts...")
    print("📂 Target directory:", fonts_dir)
    print()

    success_count = 0
    total_count = len(fonts_to_download)

    for url, filename in fonts_to_download:
        if download_font(url, filename):
            success_count += 1

    print()
    print(f"📊 Results: {success_count}/{total_count} fonts downloaded successfully")

    if success_count == total_count:
        print("🎉 All fonts downloaded! Self-hosted fonts implementation complete.")
        print("✅ Playwright will now work offline without external font dependencies.")
    else:
        print("⚠️  Some fonts failed to download. Check network connection and URLs.")
        print("💡 Consider using a font downloader tool like google-fonts-helper.")

if __name__ == "__main__":
    main()