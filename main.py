import os
import urllib.request
from typing import List

from dotenv import load_dotenv
from fastapi import FastAPI, Query, Response

from logic import Comic

load_dotenv()
app = FastAPI()

HOST = os.getenv('HOST')


@app.get("/comics/current")
def get_current_comic(response: Response):
    try:
        comic_data = Comic.load_json(f'{HOST}/info.0.json')
    except urllib.error.HTTPError as error:
        response.status_code = error.code
        return error
    return Comic.process_data(comic_data)


@app.get("/comics/many")
def get_many_comics(response: Response, comic_ids: List[int] = Query(...)):
    output = []
    unique_ids = list(dict.fromkeys(comic_ids))
    for comic_id in unique_ids:
        try:
            comic_data = Comic.load_json(f'{HOST}/{comic_id}/info.0.json')
        except urllib.error.HTTPError as error:
            response.status_code = error.code
            return error
        output.append(Comic.process_data(comic_data))
    return output


@app.get("/comics/download")
def download_comics(response: Response, comic_ids: List[int] = Query(...)):
    urls = []
    images_path = os.getenv('IMAGES_PATH')
    local_images = dict.fromkeys(Comic.local_images(images_path), True)
    unique_ids = [ID for ID in dict.fromkeys(comic_ids) if not local_images.get(ID)]

    for comic_id in unique_ids:
        try:
            comic_data = Comic.load_json(f'{HOST}/{comic_id}/info.0.json')
        except urllib.error.HTTPError as error:
            response.status_code = error.code
            return error
        urls.append((comic_id, comic_data.get('img')))

    for comic_id, image_url in urls:
        Comic.save_image(images_path, str(comic_id), image_url)
    return {}


@app.get("/comics/{comic_id}")
def get_comic_by_id(comic_id: int, response: Response):
    try:
        comic_data = Comic.load_json(f'{HOST}/{comic_id}/info.0.json')
    except urllib.error.HTTPError as error:
        response.status_code = error.code
        return error
    return Comic.process_data(comic_data)
