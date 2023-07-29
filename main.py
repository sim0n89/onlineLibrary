import argparse
import os
from os.path import splitext
from pprint import pprint
from time import sleep
from urllib import parse
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError("it was redirect")


def download_txt(url, params, name, folder="books/"):
    name = sanitize_filename(name)
    if not os.path.exists(folder):
        os.makedirs(folder)
    file_path = os.path.join(folder, f"{name}.txt")
    response = requests.get(url, params=params)
    response.raise_for_status()
    check_for_redirect(response)
    with open(file_path, "wb") as file:
        file.write(response.content)
    return file_path


def download_image(url, name):
    folder = "images/"
    if not os.path.exists(folder):
        os.makedirs(folder)
    file_path = os.path.join(folder, name)
    response = requests.get(url)
    response.raise_for_status()
    with open(file_path, "wb") as file:
        file.write(response.content)


def get_html(url):
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)
    return response.text


def parse_book_page(html):
    soup = BeautifulSoup(html, "lxml")
    book_title = soup.find("h1").get_text()
    image = soup.find("div", class_="bookimage").find("img").get("src")
    if "::" in book_title:
        book_title = book_title.split("::")
        book_name = book_title[0].strip()
    else:
        book_name = book_title

    comments = soup.find_all("div", {"class": "texts"})

    book_comments = []
    for comment in comments:
        comment_text = comment.find("span", class_="black").getText()
        book_comments.append(comment_text)

    genres = soup.find("span", class_="d_book").find_all("a")
    book_genres = [genre.get_text() for genre in genres ]

    book = {
        "name": book_name,
        "image": urljoin("https://tululu.org/", image),
        "comments": book_comments,
        "genres": book_genres,
    }

    return book


def get_image_extension(url):
    path = parse.urlparse(url)
    return splitext(path.path.rstrip("/").split("/")[-1])[-1]


def main():
    parser = argparse.ArgumentParser(
        description="Парсим книги с сайта tululu.org. Введите диапазон id книг которые хотите скачать. --start_id - id книги с которой начнется сбор, --end_id - id последней книги."
    )
    parser.add_argument(
        "-start", "--start_id", help="Минимальный id книги", default=1, type=int
    )
    parser.add_argument(
        "-end", "--end_id", help="Максимальный id кники", default=10, type=int
    )
    args = parser.parse_args()
    min_id = args.start_id
    max_id = args.end_id
    if min_id < 0 or max_id < 0 or max_id <= min_id:
        raise Exception("Параметры должны быть больше нуля и end_id>start_id")
    id = min_id
    while id <= max_id:
        url = f"https://tululu.org/b{id}/"
        try:
            html = get_html(url)
        except requests.HTTPError as e:
            print(e)
            id += 1
            continue
        except requests.ConnectionError as e:
            print(f"Ошибка соединения при скачивании книги по id={id}")
            sleep(15)
            continue

        book = parse_book_page(html)
        try:
            params = {
                "id": id
            }
            download_txt(
                f"https://tululu.org/txt.php", params , f"{id}.{book['name']}"
            )
        except requests.HTTPError as e:
            print(f"Вы не скачали {book['name']}, ee нет на сайте")
            id += 1
            continue
        except requests.ConnectionError as e:
            print(f"Ошибка соединения при скачивании книги по id={id}")
            sleep(15)
            continue

        extension = get_image_extension(book["image"])

        try:
            download_image(book["image"], f"{id}{extension}")
        except requests.HTTPError as e:
            print("Картинка не скачалась")
        pprint(book)
        id += 1


if __name__ == "__main__":
    main()
