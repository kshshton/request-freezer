from datetime import datetime, time, timedelta
from typing import Optional

import redis
import requests


class Freezer:
    def __init__(self, address: str, port: int) -> None:
        self.redis_client = redis.Redis(
            host=address,
            port=port,
            decode_responses=True
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
                self.redis_client.set(url, response.text)
                expire_time = self._get_expire_time()
                self.redis_client.expire(url, expire_time)
                print("Saved!")
                return response.text
            else:
                return None

    def get_content_from_page(self, url: str, char_limit: int = 3000) -> str:
        page_content = self.get_page_from_cache(url)

        if page_content:
            return page_content[:char_limit]
