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
        super().__init__(*args, directory=str(Path.cwd() / "output"), **kwargs)

    def end_headers(self):
        # Add CORS headers for cross-origin access
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

def main():
    """Start the local network server."""
    PORT = 8000

    # Change to project root directory
    os.chdir(Path(__file__).parent)

    # Get local IP address
    local_ip = get_local_ip()

    # Create server
    with socketserver.TCPServer(("0.0.0.0", PORT), CustomHTTPRequestHandler) as httpd:
        print(f"""
🌐 Socials.io Local Network Server Started
═══════════════════════════════════════════

📂 Serving directory: {Path.cwd() / 'output'}
🖥️  Local access:     http://localhost:{PORT}
📱 Network access:    http://{local_ip}:{PORT}

📋 Available endpoints:
   • HTML outputs:    http://{local_ip}:{PORT}/html/
   • Image outputs:   http://{local_ip}:{PORT}/images/

🔗 Quick links:
   • Template 1: http://{local_ip}:{PORT}/html/1_output.html
   • Template 2: http://{local_ip}:{PORT}/html/2_output.html
   • Template 3: http://{local_ip}:{PORT}/html/3_output.html
   • Template 4: http://{local_ip}:{PORT}/html/4_output.html
   • Template 5: http://{local_ip}:{PORT}/html/5_output.html
   • Template 6: http://{local_ip}:{PORT}/html/6_output.html

💡 To test from other devices on your network:
   1. Connect devices to the same Wi-Fi network
   2. Use the network URL: http://{local_ip}:{PORT}
   3. For mobile testing, scan this QR code (if available)

🛑 Press Ctrl+C to stop the server
""")

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n🛑 Server stopped by user")
            httpd.shutdown()

if __name__ == "__main__":
    main()