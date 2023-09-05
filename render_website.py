import json
from jinja2 import Environment, FileSystemLoader
from livereload import Server, shell


def on_reload():
    with open("data.json", encoding="utf-8") as json_file:
        books = json.load(json_file)

    env = Environment(loader=FileSystemLoader("."))
    template = env.get_template(
        "templates/index.html",
    )
    rendered_html = template.render(title="Книги по научной фантастике", books=books)
    with open("index.html", "w", encoding="utf-8") as output_file:
        output_file.write(rendered_html)


server = Server()
server.watch("templates/*.html", on_reload)
server.serve(root=".")


if __name__ == "__main__":
    on_reload()
