import argparse
import os
from os.path import splitext
from pprint import pprint
from urllib import parse
from urllib.error import HTTPError
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


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


def parse_book_page(html):
    soup = BeautifulSoup(html, "lxml")
    h1 = soup.find("h1").get_text()
    image = soup.find("div", class_="bookimage").find("img").get("src")
    if "::" in h1:
        h1 = h1.split("::")
        book_name = h1[0].strip()
    else:
        book_name = h1

    comments = soup.find_all("div", {"class":"texts"})
    
    book_comments=[]
    if comments:
        for comment in comments:
            comment_text = comment.find("span", class_="black").getText()
            book_comments.append(comment_text)

    book_genres = []
    genres = soup.find("span", class_="d_book").find_all("a")
    for genre in genres:
        book_genres.append(genre.get_text())

    book_info = {"name": book_name, "image": urljoin("https://tululu.org/", image), "comments": book_comments, "genres": book_genres}
    
    return book_info


def get_image_extension(url):
    path = parse.urlparse(url)
    return splitext(path.path.rstrip("/").split("/")[-1])[-1]


def main():
    parser = argparse.ArgumentParser(
        description="Парсим книги с сайта tululu.org. Введите диапазон id книг которые хотите скачать."
    )
    parser.add_argument("-start", "--start_id", help="Минимальный id книги", default=1, type=int)
    parser.add_argument("-end", "--end_id", help="Максимальный id кники", default=10, type=int)
    args = parser.parse_args()
    min_id = args.start_id
    max_id = args.end_id
    if min_id<0 or max_id<0 or max_id<=min_id:
         raise Exception('Параметры должны быть больше нуля и end_id>start_id')
    i = min_id
    while i <= max_id:
        url = f"https://tululu.org/b{i}/"
        try:
            html = get_html(url)
        except:
            continue

        book_info = parse_book_page(html)
        try:
            download_txt(
                f"https://tululu.org/txt.php?id={i}", f"{i}.{book_info['name']}"
            )
        except:
            print(f"Вы не скачали {book_info['name']}, ee нет на сайте")

        extension = get_image_extension(book_info["image"])
    
        try:
            download_image(book_info["image"], f"{i}{extension}")
        except HTTPError as e:
            print("Картинка не скачалась")
        pprint(book_info)
        i+=1

if __name__ == "__main__":
    main()
