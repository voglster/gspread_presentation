from dotenv import load_dotenv

load_dotenv()

from os import getenv
from dotmap import DotMap
import json


config = DotMap()

# google creds file
config.google_api_key = getenv("GOOGLE_API_KEY", "")
config.google_credentials_file = getenv("GOOGLE_CREDENTIALS_FILE", "./credentials.json")
with open(config.google_credentials_file) as f:
    config.project_id = json.load(f).get("project_id")

if __name__ == "__main__":
    with open(".env", "w") as f:
        for key, value in config.items():
            f.write(f"{str(key).upper()}={value}\n")
