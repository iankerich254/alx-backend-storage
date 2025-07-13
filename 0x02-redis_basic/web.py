#!/usr/bin/env python3
"""Module for caching HTML content from URLs with Redis"""

import redis
import requests
from typing import Callable
from functools import wraps

# Initialize Redis client
r = redis.Redis()


def count_url_access(method: Callable) -> Callable:
    """Decorator to count how many times a URL has been accessed."""

    @wraps(method)
    def wrapper(url: str) -> str:
        """Wrapper function that increments access count."""
        r.incr(f"count:{url}")
        return method(url)

    return wrapper


def cache_response(method: Callable) -> Callable:
    """Decorator to cache the response for a given URL for 10 seconds."""

    @wraps(method)
    def wrapper(url: str) -> str:
        """Wrapper that caches the HTML content."""
        cached_data = r.get(f"cache:{url}")
        if cached_data:
            return cached_data.decode("utf-8")

        result = method(url)
        r.setex(f"cache:{url}", 10, result)
        return result

    return wrapper


@cache_response
@count_url_access
def get_page(url: str) -> str:
    """
    Fetch HTML content of the given URL.

    Tracks access count and caches the result for 10 seconds.
    """
    response = requests.get(url)
    return response.text

