from flask_caching import Cache

test_cache = Cache(config={"CACHE_TYPE": "SimpleCache"})