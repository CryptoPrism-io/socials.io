from instagrapi import Client
from pathlib import Path

# Initialize Instagram Client
cl = Client()

# Login to Instagram
USERNAME = "cryptoprism.io"
PASSWORD = "jaimaakamakhya"


cl.login(USERNAME, PASSWORD)

# Define the list of media files
media_files = [
    Path("1_output.jpg"),
    Path("2_output.jpg"),
    Path("3_output.jpg"),
    Path("4_output.jpg"),
    Path("5_output.jpg")
]

# Define the caption for the carousel post
caption = "Your carousel post caption here!"


# Upload the carousel post
media = cl.album_upload(media_files, caption)

print("Carousel Post Uploaded Successfully")

