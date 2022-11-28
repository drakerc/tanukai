import logging

import requests

from config import IMGUR_CLIENT_ID

logger = logging.getLogger("imgur_downloader")


def imgur_downloader(url: str) -> list:
    split_url = url.split('.')
    if split_url[-1] in ['jpg', 'png', 'gif', 'jpeg']:
        return [url.replace('http://', 'https://').replace('https://imgur.com', 'https://i.imgur.com')]
    if "gallery" in url or "/a/" in url:
        pass
    else:
        return [f"{url.replace('http://', 'https://').replace('https://imgur.com', 'https://i.imgur.com')}.jpg"]

    split_url_by_slash = url.split('/')
    album_hash = split_url_by_slash[-1]
    response = requests.get(f"https://api.imgur.com/3/album/{album_hash}",
                           headers={"Authorization": f"Client-ID {IMGUR_CLIENT_ID}"}
                           )
    if response.status_code != 200:
        logger.warning(f"Imgur url {url} returned {response.status_code}, headers: {response.headers}, text: {response.text}")
        return []

    response_json = response.json()
    images = response_json.get("data", {}).get("images", [])
    return [image.get("link") for image in images]
