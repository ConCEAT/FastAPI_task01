import os
import json
import requests
import urllib.request
from datetime import datetime

from dotenv import load_dotenv
from typing import Optional, Dict, List
from fastapi import FastAPI, Response, Query

import functions

load_dotenv()
app = FastAPI()

def getFilenames(path: str) -> list:
    for (_, _, filenames) in os.walk(path):
        if filenames:
            return filenames
        return []
    raise ValueError("Incorrect path given")

def saveImage(path, comicId, url):
    fileExtension = url.split('.')[-1]
    image = requests.get(url).content
    with open(f'{path}{comicId}.{fileExtension}', 'wb') as newImage:
        newImage.write(image)
    
def loadJSON(url: str) -> dict:
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


@app.get("/comics/current")
def getCurrentComic(response: Response):
    try:
        comicData = functions.loadJSON('https://xkcd.com/info.0.json')
    except urllib.error.HTTPError as error:
        response.status_code = error.code
        return {"detail": error.msg}
    return functions.processComicData(comicData)


@app.get("/comics/many")
def getManyComics(response: Response, comic_ids: List[int] = Query(...)):
    output = []
    history = []
    for comicId in comic_ids:
        if comicId in history:
            continue
        try:
            comicData = functions.loadJSON(f'https://xkcd.com/{comicId}/info.0.json')
        except urllib.error.HTTPError as error:
            response.status_code = error.code
            return {"detail": error.msg}
        output.append(functions.processComicData(comicData))
        history.append(comicId)
    return output


@app.get("/comics/download")
def downloadComics(response: Response, comic_ids: List[int] = Query(...)):
    
    history = []
    imagesPath = os.getenv('IMAGES_PATH')
    localFiles = list(map(
        lambda filename: int(filename.split('.')[0]),
        functions.getFilenames(imagesPath)
    ))
    
    for comicId in comic_ids:
        if comicId in history or comicId in localFiles:
            continue
        try:
            comicData = functions.loadJSON(f'https://xkcd.com/{comicId}/info.0.json')
        except urllib.error.HTTPError as error:
            response.status_code = error.code
            return {"detail": error.msg}

        imageUrl = comicData['img']
        functions.saveImage(imagesPath, comicId, imageUrl)
        history.append(comicId)


@app.get("/comics/{comicId}")
def getComicByID(comicId: int, response: Response):
    try:
        comicData = functions.loadJSON(f'https://xkcd.com/{comicId}/info.0.json')
    except urllib.error.HTTPError as error:
        response.status_code = error.code
        return {"detail": error.msg}
    return functions.processComicData(comicData)
