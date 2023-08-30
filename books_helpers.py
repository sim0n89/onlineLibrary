import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os
from urllib import parse
from os.path import splitext
from pathvalidate import sanitize_filename



def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError("it was redirect")


def get_html(url):
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)
    return response.text


def parse_book_page(html, url):
    soup = BeautifulSoup(html, "lxml")
    book_title = soup.select_one("h1").text
    image = soup.select_one(".bookimage img").get("src")
    if "::" in book_title:
        book_title = book_title.split("::")
        book_name = book_title[0].strip()
        book_author = book_title[1].strip()
    else:
        book_name = book_title
        book_author = ''

    comments = soup.select(".texts")

    book_comments = []
    for comment in comments:
        comment_text = comment.select_one("span.black").text
        book_comments.append(comment_text)

    genres = soup.select("span.d_book a")
    book_genres = [genre.get_text() for genre in genres]
    book = {
        "name": book_name,
        "image": urljoin(url, image),
        "comments": book_comments,
        "genres": book_genres,
        "author": book_author
    }

    return book


def download_image(url, name, folder="images/"):
    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, name)
    response = requests.get(url)
    response.raise_for_status()
    with open(file_path, "wb") as file:
        file.write(response.content)


def get_image_extension(url):
    path = parse.urlparse(url)
    return splitext(path.path.rstrip("/").split("/")[-1])[-1]


def download_txt(url, params, name, folder="books/"):
    name = sanitize_filename(name)
    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, f"{name}.txt")
    response = requests.get(url, params=params)
    response.raise_for_status()
    check_for_redirect(response)
    with open(file_path, "wb") as file:
        file.write(response.content)
    return file_path