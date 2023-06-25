"""
FIXME: rename to Cache

"""
from cachetools import LRUCache, TTLCache


class Cache:
    def __init__(self, maxsize: float = 100, ttl: float = None):  # ttl - 1 hr, 128

        if ttl is None:
            self.cache = LRUCache(maxsize=maxsize)
        else:
            self.cache = TTLCache(maxsize=maxsize, ttl=ttl)

    def get(self, key):
        return self.cache.get(key)

    def set(self, key, value):
        self.cache[key] = value

    def delete(self, key):
        self.cache.pop(key, None)

    def clear(self):
        self.cache.clear()

    def __repr__(self):
        return f'Cache({self.cache})'

    def __str__(self):
        return self.cache

    def __call__(self):
        return self.cache
