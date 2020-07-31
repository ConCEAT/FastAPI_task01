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
def get_current_comic(response: Response):
    try:
        comic_data = functions.load_json('https://xkcd.com/info.0.json')
    except urllib.error.HTTPError as error:
        response.status_code = error.code
        return error
    return functions.process_comic_data(comic_data)


@app.get("/comics/many")
def get_many_comics(response: Response, comic_ids: List[int] = Query(...)):
    output = []
    history = []
    for comic_id in comic_ids:
        if comic_id in history:
            continue
        try:
            comic_data = functions.load_json(f'https://xkcd.com/{comic_id}/info.0.json')
        except urllib.error.HTTPError as error:
            response.status_code = error.code
            return error
        output.append(functions.process_comic_data(comic_data))
        history.append(comic_id)
    return output


@app.get("/comics/download")
def download_comics(response: Response, comic_ids: List[int] = Query(...)):
    history = []
    urls = []
    images_path = os.getenv('IMAGES_PATH')
    local_files = list(map(
        lambda filename: int(filename.split('.')[0]),
        functions.get_filenames(images_path)
    ))
    
    for comic_id in comic_ids:
        if comic_id in history or comic_id in local_files:
            continue
        try:
            comic_data = functions.load_json(f'https://xkcd.com/{comic_id}/info.0.json')
        except urllib.error.HTTPError as error:
            response.status_code = error.code
            return error
        urls.append((comic_id,comic_data['img']))
        history.append(comic_id)
    
    for comic_id, image_url in urls:
        functions.save_image(images_path, str(comic_id), image_url)
    return {}


@app.get("/comics/{comic_id}")
def get_comic_by_id(comic_id: int, response: Response):
    try:
        comic_data = functions.load_json(f'https://xkcd.com/{comic_id}/info.0.json')
    except urllib.error.HTTPError as error:
        response.status_code = error.code
        return error
    return functions.process_comic_data(comic_data)
