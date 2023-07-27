from urllib.error import HTTPError
from urllib.parse import urljoin
import requests
from pathlib import Path
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
import os
from os.path import splitext
from urllib import parse


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError("it was redirect")


def download_txt(url, name, folder="books/"):
    name = sanitize_filename(name)
    if not os.path.exists(folder):
        os.makedirs(folder)
    file_path = os.path.join(folder, f"{name}.txt")
    response = requests.get(url)
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


def get_book_info(html):
    soup = BeautifulSoup(html, "lxml")
    h1 = soup.find("h1").get_text()
    image = soup.find("div", class_="bookimage").find("img").get("src")
    if "::" in h1:
        h1 = h1.split("::")
        book_name = h1[0].strip()
    else:
        book_name = h1
    book_info = {"name": book_name, "image": urljoin("https://tululu.org/", image)}
    return book_info


def get_image_extension(url):
    path = parse.urlparse(url)
    return splitext(path.path.rstrip("/").split("/")[-1])[-1]


def main():
    for i in range(1, 11):
        url = f"https://tululu.org/b{i}/"
        try:
            html = get_html(url)
        except:
            continue

        book_info = get_book_info(html)
        try:
            book_path = download_txt(
                f"https://tululu.org/txt.php?id={i}", f"{i}.{book_info['name']}"
            )
        except:
            print(f"Вы не скачали {book_info['name']}, ee нет на сайте")

        extension = get_image_extension(book_info["image"])

        try:
            download_image(book_info["image"], f"{i}.{extension}")
        except HTTPError as e:
            print("Картинка не скачалась")

if __name__ == "__main__":
    main()
