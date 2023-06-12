import yaml

# Open the file and load the YAML content
with open("config.yml", "r") as file:
    config = yaml.safe_load(file)

PROFILE = f"https://bandcamp.com/{config['username']}"
WISHLIST = PROFILE + "/wishlist"