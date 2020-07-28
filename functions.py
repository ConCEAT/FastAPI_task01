import os
import json
import requests
import urllib.request
from datetime import datetime

from typing import Dict


def getFilenames(path: str) -> list:
    "Get names of all files in the given directory"
    for (_, _, filenames) in os.walk(path):
        if filenames:
            return filenames
        return []
    raise ValueError("Incorrect path given")

def saveImage(path: str, filename: str, url: str) -> None:
    """Save image from URL to /path/filename.ext
    
    File extension is taken from URL
    """
    fileExtension = url.split('.')[-1]
    image = requests.get(url).content
    with open(f'{path}{filename}.{fileExtension}', 'wb') as newImage:
        newImage.write(image)
    
def loadJSON(url: str) -> dict:
    "Load JSON file from URL to python dictionary"
    with urllib.request.urlopen(url) as source:
        text = source.read().decode('utf8')
    return json.loads(text)

def processComicData(comicData: Dict) -> dict:
    return {
        "id" : comicData["num"],
        "description" : comicData["transcript"],
        "date" : datetime(
            int(comicData["year"]),
            int(comicData["month"]),
            int(comicData["day"])).strftime("%y-%m-%d"),
        "title" : comicData["title"].lower(),
        "url" : comicData["img"]
    }