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


@app.get("/comics/current")
def getCurrentComic(response: Response):
    try:
        comicData = functions.loadJSON('https://xkcd.com/info.0.json')
    except urllib.error.HTTPError as error:
        response.status_code = error.code
        return error
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
            return error
        output.append(functions.processComicData(comicData))
        history.append(comicId)
    return output


@app.get("/comics/download")
def downloadComics(response: Response, comic_ids: List[int] = Query(...)):
    history = []
    urls = []
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
            return error
        urls.append((comicId,comicData['img']))
        history.append(comicId)
    
    for comicId, imageUrl in urls:
        functions.saveImage(imagesPath, str(comicId), imageUrl)


@app.get("/comics/{comicId}")
def getComicByID(comicId: int, response: Response):
    try:
        comicData = functions.loadJSON(f'https://xkcd.com/{comicId}/info.0.json')
    except urllib.error.HTTPError as error:
        response.status_code = error.code
        return error
    return functions.processComicData(comicData)
