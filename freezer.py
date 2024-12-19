import logging
import time
from contextlib import contextmanager
from datetime import datetime, time, timedelta
from typing import Generator

import redis
import requests


class Freezer:
    def __init__(
        self,
        address: str,
        port: int,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ) -> None:
        """
        Definition of connection parameters
        """
        self.redis_client = None
        self.address = address
        self.port = port
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    @contextmanager
    def connection(self) -> Generator:
        """
        Context manager to establish and close Redis connection
        Yields: 
            Redis client instance
        """
        retries = 0
        while retries < self.max_retries:
            try:
                self.redis_client = redis.Redis(
                    host=self.address,
                    port=self.port,
                    db=0,
                    decode_responses=True
                )
                logging.info("Redis connected!")
                yield self.redis_client
                break
            except redis.ConnectionError as e:
                retries += 1
                logging.error(f"Connection failed: {e}")
                if retries < self.max_retries:
                    time.sleep(self.retry_delay)
            finally:
                logging.info("Redis connection has been closed!")

    def _get_expire_time(self) -> int:
        """
        Get time to midnight
        Returns: 
            Milliseconds
        """
        now = datetime.now()
        next_day_midnight = datetime.combine(
            now.date() + timedelta(days=1), time.min
        )
        expire_time = (next_day_midnight - now).total_seconds()
        return int(expire_time)

    def list_cached_websites(self) -> dict:
        return {key: self.redis_client.get(key) for key in self.redis_client.keys()}

    def get_page_content_from_cache(self, url: str) -> str:
        try:
            cached_page = self.redis_client.get(url)
            if not cached_page:
                response = requests.get(url)
                assert response.ok, "Bad response!"
                self.redis_client.set(url, response.text)
                expire_time = self._get_expire_time()
                self.redis_client.expire(url, expire_time)
                logging.info("Saved!")
                return response.text
            logging.info("Loaded from cache!")
            return cached_page
        except Exception as e:
            logging.error(f"get_page_from_cache: {str(e)}")

    def get_page_content(self, url: str, char_limit: int = 3000) -> str:
        try:
            page_content = self.get_page_content_from_cache(url)
            return page_content[:char_limit]
        except Exception as e:
            logging.error(f"get_content_from_page: {str(e)}")
