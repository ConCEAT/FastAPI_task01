import os
import json
import requests
import urllib.request
from datetime import datetime

from typing import Dict


def get_filenames(path: str) -> list:
    "Get names of all files in the given directory"
    for (_, _, filenames) in os.walk(path):
        if filenames:
            return list(map(lambda filename: int(filename.split('.')[0]), filenames))
        return []
    raise ValueError("Incorrect path given")

def save_image(path: str, filename: str, url: str) -> None:
    """Save image from URL to /path/filename.ext
    
    File extension is taken from URL
    """
    file_extension = url.split('.')[-1]
    image = requests.get(url).content
    with open(os.path.join(path,f'{filename}.{file_extension}'), 'wb') as new_image:
        new_image.write(image)
    
def load_json(url: str) -> dict:
    "Load JSON file from URL to python dictionary"
    with urllib.request.urlopen(url) as source:
        text = source.read().decode('utf8')
    return json.loads(text)

def process_comic_data(comic_data: Dict) -> dict:
    return {
        "id" : comic_data["num"],
        "description" : comic_data["transcript"],
        "date" : datetime(
            int(comic_data["year"]),
            int(comic_data["month"]),
            int(comic_data["day"])).strftime("%y-%m-%d"),
        "title" : comic_data["title"].lower(),
        "url" : comic_data["img"]
    }