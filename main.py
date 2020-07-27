import os
import json
import urllib.request
from datetime import datetime

from dotenv import load_dotenv
from typing import Optional, Dict, List
from fastapi import FastAPI, Response, Query

load_dotenv()
app = FastAPI()

#<VARIABLE> = os.getenv("<VARIABLE>")

def loadJSON(url: str):
    with urllib.request.urlopen(url) as source:
        text = source.read().decode('utf8')
    return json.loads(text)

def processComicData(comicData: Dict):
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
        comicData = loadJSON('https://xkcd.com/info.0.json')
    except urllib.error.HTTPError as error:
        response.status_code = error.code
        return {"detail": error.msg}
    return processComicData(comicData)

@app.get("/comics/many")
def getManyComics(response: Response, comic_ids: List[int] = Query(...)):
    output = []
    history = []
    for comicID in comic_ids:
        if comicID in history:
            continue
        try:
            comicData = loadJSON(f'https://xkcd.com/{comicID}/info.0.json')
        except urllib.error.HTTPError as error:
            response.status_code = error.code
            return {"detail": error.msg}
        output.append(processComicData(comicData))
        history.append(comicID)
    return output

@app.get("/comics/{comicID}")
def getComicByID(comicID: int, response: Response):
    try:
        comicData = loadJSON(f'https://xkcd.com/{comicID}/info.0.json')
    except urllib.error.HTTPError as error:
        response.status_code = error.code
        return {"detail": error.msg}
    return processComicData(comicData)
