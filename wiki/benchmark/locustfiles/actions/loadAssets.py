import os

# Create dict to store files in binary
data = {
    "images": {},
    "videos": {},
    "gifs": {},
    "audios": {},
    "icons": {},
    "texts": {}
}

# Insert files to respective dicts
for item in data.keys():
    for asset in os.listdir(f"assets/{item}"):
        with open(f"assets/{item}/{asset}", "rb") as f:
            data[item][asset] = f.read()