import json

files = []

with open("assets.json", "r") as file:
    assets = json.load(file)

for asset in assets:
    with open(asset, "rb") as file:
        files.append(file.read())