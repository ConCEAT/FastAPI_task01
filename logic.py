import json
import os
import urllib.request
from datetime import datetime
from typing import Dict

import requests


class Comic:
    @staticmethod
    def local_images(path: str) -> list:
        "Return ids of all images in a directory"
        for (_, _, filenames) in os.walk(path):
            if filenames:
                return list(map(lambda filename: int(filename.split('.')[0]), filenames))
            return []
        raise ValueError("Incorrect path given")

    @staticmethod
    def save_image(path: str, filename: str, url: str) -> None:
        """Save image from URL to /path/filename.ext

        File extension is taken from URL
        """
        file_extension = url.split('.')[-1]
        image = requests.get(url).content
        with open(os.path.join(path, f'{filename}.{file_extension}'), 'wb') as new_image:
            new_image.write(image)

    @staticmethod
    def load_json(url: str) -> dict:
        "Load JSON file from URL to python dictionary"
        with urllib.request.urlopen(url) as source:
            text = source.read().decode('utf8')
        return json.loads(text)

    @staticmethod
    def process_data(comic_data: Dict) -> dict:
        "Format comic data into n"
        return {
            "id": comic_data.get("num"),
            "description": comic_data.get("transcript"),
            "date": datetime(
                int(comic_data.get("year")),
                int(comic_data.get("month")),
                int(comic_data.get("day"))).strftime("%y-%m-%d"),
            "title": comic_data.get("title").lower(),
            "url": comic_data.get("img")
        }
