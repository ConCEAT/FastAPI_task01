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

HOST = os.getenv('HOST')


@app.get("/comics/current")
def get_current_comic(response: Response):
    try:
        comic_data = functions.load_json(f'{HOST}/info.0.json')
    except urllib.error.HTTPError as error:
        response.status_code = error.code
        return error
    return functions.process_comic_data(comic_data)


@app.get("/comics/many")
def get_many_comics(response: Response, comic_ids: List[int] = Query(...)):
    output = []
    unique_ids = list(dict.fromkeys(comic_ids))
    for comic_id in unique_ids:
        try:
            comic_data = functions.load_json(f'{HOST}/{comic_id}/info.0.json')
        except urllib.error.HTTPError as error:
            response.status_code = error.code
            return error
        output.append(functions.process_comic_data(comic_data))
    return output


@app.get("/comics/download")
def download_comics(response: Response, comic_ids: List[int] = Query(...)):
    urls = []
    images_path = os.getenv('IMAGES_PATH')
    local_files = dict.fromkeys(functions.get_filenames(images_path), True)
    unique_ids = [ID for ID in dict.fromkeys(comic_ids) if not local_files.get(ID)]

    for comic_id in unique_ids:
        try:
            comic_data = functions.load_json(f'{HOST}/{comic_id}/info.0.json')
        except urllib.error.HTTPError as error:
            response.status_code = error.code
            return error
        urls.append((comic_id,comic_data['img']))
    
    for comic_id, image_url in urls:
        functions.save_image(images_path, str(comic_id), image_url)
    return {}


@app.get("/comics/{comic_id}")
def get_comic_by_id(comic_id: int, response: Response):
    try:
        comic_data = functions.load_json(f'{HOST}/{comic_id}/info.0.json')
    except urllib.error.HTTPError as error:
        response.status_code = error.code
        return error
    return functions.process_comic_data(comic_data)
