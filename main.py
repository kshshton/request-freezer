from pprint import pprint

from freezer import Freezer


def main() -> None:
    freezer = Freezer(address='127.0.0.1', port=6379)
    freezer.get_content_from_page("https://example.com/")
    pprint(freezer.list_cached_websites())


if __name__ == "__main__":
    main()
