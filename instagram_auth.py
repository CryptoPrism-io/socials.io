from instagrapi import Client
import os
import shutil

# Define paths - using local Git repository for persistence
SETTINGS_FOLDER = "./settings"  # Path to folder in your local repo
SETTINGS_FILE = os.path.join(SETTINGS_FOLDER, "instagram_settings.json")

# Ensure the settings folder exists
os.makedirs(SETTINGS_FOLDER, exist_ok=True)

try:
    # First, check if settings file exists
    if os.path.exists(SETTINGS_FILE):
        shutil.copy2(SETTINGS_FILE, "instagram_settings.json")
        print("Copied existing settings from repo folder to local")

    # Try to load existing settings and reuse session
    cl = Client()
    cl.load_settings("instagram_settings.json")
    cl.get_timeline_feed()  # Verify session is still valid
    print("Successfully loaded existing session")

except Exception as e:
    print("Creating new session...")
    cl = Client()
    cl.login("cryptoprism.io", "jaimaakamakhya")  # Replace with your credentials
    cl.dump_settings("instagram_settings.json")

    # Save the new settings to the repo folder
    shutil.copy2("instagram_settings.json", SETTINGS_FILE)
    print(f"New session created and saved to {SETTINGS_FILE}")

print("Session is ready to use.")
