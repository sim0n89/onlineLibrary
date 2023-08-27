from bs4 import BeautifulSoup
from urllib import parse
from urllib.parse import urljoin
import requests
from books_helpers import get_html, parse_book_page, download_image, download_txt
from time import sleep
import os
from pprint import pprint
import json
import argparse


def get_books_links_from_category(category_url, end_page=9999, start_page=1):
    links = []
    for page in range(start_page, end_page, 1):
        category_url = urljoin(category_url, str(page))
        try:
            html = get_html(category_url)
        except requests.HTTPError as e:
            print(e)
            return links, category_name
        except requests.ConnectionError as e:
            print(f"Ошибка соединения при скачивании страницы по url={category_url}")
            sleep(15)
            continue
        soup = BeautifulSoup(html, "lxml")
        category_name = soup.select_one("#content h2").text.split("::")[-1].strip()
        books = soup.select("table.d_book")
        for book in books:
            link = book.select_one(".bookimage a").get("href")
            url = urljoin(category_url, link)
            links.append(url)

    return links, category_name


def main():
    parser = argparse.ArgumentParser(
        description="Парсим книги с сайта tululu.org. Введите диапазон страниц категорий. --start_page - стартовая страница, --end_page - последняя страница категории. --skip_txt - не сохранять текст книг, skip_imgs - не сохранять картинки, dest_folder - путь к каталогу с результатами парсинга"
    )
    parser.add_argument(
        "-start", "--start_page", help="Номер стартовой страницы", default=1, type=int
    )
    parser.add_argument(
        "-end", "--end_page", help="Номер максимальной страницы", default=9999, type=int
    )
    parser.add_argument(
        "-s_img", "--skip_imgs", help="Не скачивать картинки", action="store_true"
    )
    parser.add_argument(
        "-s_txt", "--skip_txt", help="Не скачивать текст", action="store_true"
    )
    # parser.add_argument(
    #     "-f", "--dest_folder", help="Не скачивать текст", default=False, type=bool
    # )
    # dest_folder
    args = parser.parse_args()
    start_page = args.start_page
    end_page = args.end_page
    skip_img = args.skip_imgs
    skip_txt = args.skip_txt
    category_url = "https://tululu.org/l55/"
    books_links, category_name = get_books_links_from_category(
        category_url, end_page, start_page
    )
    books = []
    for link in books_links:
        html = get_html(link)
        book = parse_book_page(html, link)
        if (not skip_img):
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
        if (not skip_txt):
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
