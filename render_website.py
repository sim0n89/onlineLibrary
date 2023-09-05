import json
from jinja2 import Environment, FileSystemLoader
from livereload import Server, shell
import os
import more_itertools

def on_reload():
    with open("data.json", encoding="utf-8") as json_file:
        books = json.load(json_file)

    env = Environment(loader=FileSystemLoader("."))
    template = env.get_template(
        "templates/index.html",
    )
    page_number = 1
    book_chunks = more_itertools.chunked(books, 5)
    for book_list in book_chunks:  
        os.makedirs("pages", exist_ok=True)
        file_path = os.path.join("pages", f"index{page_number}.html")
        rendered_html = template.render(title="Книги по научной фантастике", books=books)
        with open(file_path, "w", encoding="utf-8") as output_file:
            output_file.write(rendered_html)
        page_number+=1

server = Server()
server.watch("templates/*.html", on_reload )
server.serve(root=".")


if __name__ == "__main__":
    on_reload()
