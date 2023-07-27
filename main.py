import requests
from pathlib import Path
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
import os


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError("it was redirect")


def download_txt(url, name, folder="books/"):
    name = sanitize_filename(name)
    if not os.path.exists(folder):
        os.makedirs(folder)
    file_path = os.path.join(folder, f"{name}.txt")
    print(file_path)
    response = requests.get(url)
    response.raise_for_status()
    try:
        check_for_redirect(response)
        with open(file_path, "wb") as file:
            file.write(response.content)
    except:
        print(f"Вы не скачали {name}, ее нет на сайте")
    return  file_path


def get_html(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text


def get_book_info(html):
    soup = BeautifulSoup(html, "lxml")
    h1 = soup.find("h1").get_text()
    if "::" in h1:
        h1 = h1.split('::')
        book_name = h1[0].strip()
    else:
        book_name = h1
    return book_name


def main():
    for i in range(1, 11):
        url = f"https://tululu.org/b{i}/"
        html = get_html(url)
        book_name = get_book_info(html)
        book_path = download_txt(
            f"https://tululu.org/txt.php?id={i}",
            f"{i}.{book_name}"
        )
        print(book_path)


if __name__ == "__main__":
    main()
