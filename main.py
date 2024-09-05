import pprint
from datetime import datetime, time, timedelta
from typing import Optional

import redis
import requests


class Freezer:
    address: str = '127.0.0.1'
    port: int = 6379
    db: int = 0
    char_limit: int = 3000

    def __init__(self) -> None:
        self.redis_client = redis.StrictRedis(
            host=self.address,
            port=self.port,
            db=self.db,
        )

    def _get_expire_time(self) -> int:
        now = datetime.now()
        next_day_midnight = datetime.combine(
            now.date() + timedelta(days=1), time.min)
        expire_time = (next_day_midnight - now).total_seconds()
        return int(expire_time)

    def list_cached_websites(self) -> dict:
        return {key: self.redis_client.get(key) for key in self.redis_client.keys()}

    def get_page_from_cache(self, url: str) -> Optional[str]:
        cached_page = self.redis_client.get(url)

        if cached_page:
            print("Loaded from cache!")
            return cached_page.decode('utf-8')
        else:
            response = requests.get(url)

            if response.ok:
                print("Saving up to cache...")
                self.redis_client.set(url, response.text)
                expire_time = self._get_expire_time()
                self.redis_client.expire(url, expire_time)
                print("Saved!")
                return response.text
            else:
                return None

    def get_content_from_page(self, url: str) -> str:
        page_content = self.get_page_from_cache(url)

        if page_content:
            return page_content[:self.char_limit]


def main() -> None:
    freezer = Freezer()
    freezer.get_content_from_page("https://example.com/")
    pprint.pprint(freezer.list_cached_websites())


if __name__ == "__main__":
    main()
