from bs4 import BeautifulSoup

from freezer import Freezer


def main() -> None:
    freezer = Freezer(address='127.0.0.1', port=6379)
    with freezer.stream_connection():
        content = freezer.get_page_content("https://example.com/")
        soup = BeautifulSoup(content, "html.parser")
        title = soup.title.string
        print(title)


if __name__ == "__main__":
    main()
