import argparse
import os
from time import sleep

import requests

from books_helpers import (
    get_html,
    parse_book_page,
    download_image,
    get_image_extension,
    download_txt,
)


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
    book_id = min_id
    while book_id <= max_id:
        url = f"https://tululu.org/b{book_id}/"
        try:
            html = get_html(url)
        except requests.HTTPError as e:
            print(e)
            book_id += 1
            continue
        except requests.ConnectionError as e:
            print(f"Ошибка соединения при скачивании книги по id={book_id}")
            sleep(15)
            continue

        book = parse_book_page(html, url)
        try:
            params = {"id": book_id}
            download_txt(
                f"https://tululu.org/txt.php", params, f"{book_id}.{book['name']}"
            )
        except requests.HTTPError as e:
            print(f"Вы не скачали {book['name']}, ee нет на сайте")
            book_id += 1
            continue
        except requests.ConnectionError as e:
            print(f"Ошибка соединения при скачивании книги по id={book_id}")
            sleep(15)
            continue

        extension = get_image_extension(book["image"])

        try:
            download_image(book["image"], f"{book_id}{extension}")
        except requests.HTTPError as e:
            print("Картинка не скачалась")
        except requests.ConnectionError as e:
            print(f"Ошибка соединения при скачивании книги по id={book_id}")
            sleep(15)
            continue
        book_id += 1


if __name__ == "__main__":
    main()
