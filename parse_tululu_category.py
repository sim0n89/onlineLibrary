from bs4 import BeautifulSoup
from urllib import parse
from urllib.parse import urljoin
import requests
from books_helpers import get_html, parse_book_page, download_image, download_txt
from time import sleep
import os
from pprint import pprint
import json


def get_books_links_from_category(category_url, max_page):
    page_number = 1
    links = []
    while page_number <= max_page:
        category_url = urljoin(category_url, str(page_number))
        try:
            html = get_html(category_url)
        except requests.HTTPError as e:
            print(e)
            page_number += 1
            continue
        except requests.ConnectionError as e:
            print(f"Ошибка соединения при скачивании страницы по url={category_url}")
            sleep(15)
            continue
        soup = BeautifulSoup(html, "lxml")
        category_name = (
            soup.find("div", id="content").find("h2").get_text().split("::")[-1]
        )
        books = soup.find_all("table", class_="d_book")
        for book in books:
            link = book.find("div", class_="bookimage").find("a").get("href")
            url = urljoin(category_url, link)
            links.append(url)
        page_number += 1
        return links, category_name


def main():
    category_url = "https://tululu.org/l55/"

    books_links, category_name = get_books_links_from_category(category_url, 2)
    books = []
    for link in books_links:
        html = get_html(link)
        book = parse_book_page(html, link)
        try:
            image_name = parse.urlparse(book["image"]).path.rstrip("/").split("/")[-1]
            download_image(book["image"], image_name)
            book["img_src"] = os.path.join("images", image_name)
        except requests.HTTPError as e:
            print("Картинка не скачалась")
        except requests.ConnectionError as e:
            print(f"Ошибка соединения при скачивании книги '{book['name']}'")
            sleep(15)
            continue

        book_id = parse.urlparse(link).path.replace("/", "").replace("b", "")

        try:
            params = {"id": book_id}
            book["book_path"] = download_txt(
                f"https://tululu.org/txt.php", params, f"{book_id}.{book['name']}"
            )
        except requests.HTTPError as e:
            print(f"Вы не скачали {book['name']}, ee нет на сайте")
            continue
        except requests.ConnectionError as e:
            print(f"Ошибка соединения при скачивании книги по id={book_id}")
            sleep(15)
            continue
        books.append(book)
    with open(f"{category_name}.json", "w", encoding="utf-8") as file:
        json.dump(books, file, ensure_ascii=False)


if __name__ == "__main__":
    main()
