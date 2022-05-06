import pandas as pd
import json
from moodle_sync import MoodleSync

if __name__ == "__main__":
    with open("data/credentials.json", "r") as f:
        credentials = json.load(f)
    url = credentials["url"]
    token = credentials["token"]

    ms = MoodleSync(url, token)
    r = ms.add_students_to_group(6090, 5500)
    print(r)
