import requests
from pathlib import Path


def download_book(url, name, params=None):
    path = Path("books")
    path.mkdir(exist_ok=True)
    file_path = path / name
    response = requests.get(url, params=params)
    response.raise_for_status()
    with open(file_path, "wb") as file:
        file.write(response.content)


def main():
    for id in range(1, 11):
        download_book(f"https://tululu.org/txt.php", f"book{id}.txt", {"id":id})


if __name__ == "__main__":
    main()
