#!/usr/bin/env python3
"""
Simple HTTP server for local network access to socials.io output files.
Serves HTML and image outputs for testing on local network devices.
"""
import http.server
import socketserver
import os
import socket
from pathlib import Path

def get_local_ip():
    """Get the local IP address of this machine."""
    try:
        # Connect to a remote address to get local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "127.0.0.1"

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler with better MIME types and directory listing."""

    def __init__(self, *args, **kwargs):
        # Set the directory to serve from
        super().__init__(*args, directory=str(Path.cwd()), **kwargs)

    def end_headers(self):
        # Add CORS headers for cross-origin access
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

def main():
    """Start the local network server."""
    PORT = 8080

    # Change to project root directory to serve both output_html and input_images
    project_root = Path(__file__).parent.parent.parent
    os.chdir(project_root)

    # Get local IP address
    local_ip = get_local_ip()

    # Create server
    with socketserver.TCPServer(("0.0.0.0", PORT), CustomHTTPRequestHandler) as httpd:
        print(f"""
🌐 Socials.io HTML Output Server Started
═══════════════════════════════════════════

📂 Serving from: {Path.cwd()}
🖥️  Local access:     http://localhost:{PORT}
📱 Network access:    http://{local_ip}:{PORT}

🔗 Story HTML links:
   • Story Teaser:    http://localhost:{PORT}/output_html/story_teaser_output.html
   • Bitcoin Story:   http://localhost:{PORT}/output_html/04_bitcoin_intelligence_output.html
   • Long Calls:      http://localhost:{PORT}/output_html/long_calls_story_output.html
   • Short Calls:     http://localhost:{PORT}/output_html/short_calls_story_output.html

🔗 Carousel templates:
   • Cover:           http://localhost:{PORT}/output_html/01_cover_output.html
   • Top Cryptos:     http://localhost:{PORT}/output_html/12_top_cryptos_2_24_output.html
   • Gainers/Losers:  http://localhost:{PORT}/output_html/09_top_gainers_output.html

💡 To test from other devices on your network:
   1. Connect devices to the same Wi-Fi network
   2. Use the network URL: http://{local_ip}:{PORT}

🛑 Press Ctrl+C to stop the server
""")

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n🛑 Server stopped by user")
            httpd.shutdown()

if __name__ == "__main__":
    main()