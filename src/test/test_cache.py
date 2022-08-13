from time import sleep

from . import pkg

__package__ = pkg()

import unittest
from ..lib import cache as lib_cache

CacheMissException = lib_cache.CacheMissException
CacheTimeoutException = lib_cache.CacheTimeoutException
Cache = lib_cache.Cache


class CacheTest(unittest.TestCase):
    def test_set_get_string(self):
        cache = Cache()
        cache.set("key1", "get_set_string")
        self.assertEquals(cache.get("key1"), "get_set_string")

    def test_set_get_dict(self):
        cache = Cache()
        cache.set("key1", {"complex": "object", "easy": {"as": [1, 2, 3]}})
        self.assertEqual({"complex": "object", "easy": {"as": [1, 2, 3]}}, cache.get("key1"))

    def test_clear(self):
        cache = Cache(lifetime=10000)
        cache2 = Cache(lifetime=10000)
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")
        cache2.set("key21", "value21")

        self.assertEquals(cache.get("key1"), "value1")
        self.assertEquals(cache.get("key2"), "value2")
        self.assertEquals(cache.get("key3"), "value3")
        self.assertEquals(cache2.get("key21"), "value21")

        cache.clear()

        self.assertIsNone(cache.get("key1"), "value1")
        self.assertIsNone(cache.get("key2"), "value2")
        self.assertIsNone(cache.get("key3"), "value3")
        self.assertEquals(cache2.get("key21"), "value21")

    def test_get_or_raise_success(self):
        cache = Cache()
        cache.set("key1", "value1")
        self.assertEquals(cache.get_or_raise("key1"), "value1")

    def test_get_or_raise_nonexistent_raises(self):
        cache = Cache()
        cache.set("key1", "value1")
        self.assertRaises(CacheMissException, lambda: cache.get_or_raise("notkey1"))

    def test_get_or_raise_expired_raises(self):
        cache = Cache(lifetime=0.2)
        cache.set("key1", "value1")
        sleep(0.5)
        self.assertRaises(CacheTimeoutException, lambda: cache.get_or_raise("key1"))

    def test_get_or_resolve_success(self):
        cache = Cache()
        cache.set("key1", "value1")

        def resolve(key):
            self.fail("Should not have attempted to resolve")

        self.assertEquals(cache.get_or_resolve("key1", resolve), "value1")

    def test_get_or_resolve_nonexistent_resolves(self):
        cache = Cache()
        cache.set("key1", "value1")

        def resolve(key):
            if key != "key2":
                self.fail("Resolved with incorrect key")
            return "newvalue2"

        self.assertEquals(cache.get_or_resolve("key2", resolve), "newvalue2")

    def test_get_or_resolve_expired_resolves(self):
        cache = Cache(lifetime=0.5)
        cache.set("key1", "value1")

        def resolve(key):
            if key != "key1":
                self.fail("Resolved with incorrect key")
            return "newvalue1"

        sleep(1)
        self.assertEquals(cache.get_or_resolve("key1", resolve), "newvalue1")

    def test_custom_key_lifetime_shorter(self):
        cache = Cache(lifetime=30)
        cache.set("longkey", "long")
        cache.set("shortkey", "short", 0.5)
        ttl = 10
        while cache.get("shortkey") and ttl:
            ttl -= 1
            sleep(0.1)
        self.assertIsNone(cache.get("shortkey"))
        self.assertIsNotNone(cache.get("longkey"))

    def test_custom_key_lifetime_longer(self):
        cache = Cache(lifetime=0.2)
        cache.set("longkey", "long", 0.5)
        cache.set("shortkey", "short")
        ttl = 10
        while cache.get("shortkey") and ttl:
            ttl -= 1
            sleep(0.1)
        self.assertIsNone(cache.get("shortkey"))
        self.assertIsNotNone(cache.get("longkey"))

    def test_re_set(self):
        cache = Cache()
        for i in range(3):
            cache.set("key", i)
            sleep(0.1)
            self.assertEquals(cache.get("key"), i)

    def test_re_set_resets_timer(self):
        cache = Cache(lifetime=0.2)
        for i in range(3):
            cache.set("key", i)
            sleep(0.1)
            self.assertEquals(cache.get("key"), i)

    def test_re_set_resets_custom_timer(self):
        cache = Cache(lifetime=0.2)
        for i in range(3):
            cache.set("key", i, 2)
            sleep(0.1)
            self.assertEquals(cache.get("key"), i)

    def test_deleted_raises_miss_exception(self):
        cache = Cache()
        cache.set("key1", "value1")
        cache.delete("key1")
        try:
            cache.get_or_raise("key1")
        except CacheTimeoutException:
            self.fail("CacheTimeoutException raised, CacheMissException expected")
        except CacheMissException:
            pass
        except BaseException:
            self.fail("Some other exception raised, CacheMissException expected")

    def test_set_isolated(self):
        cache = Cache()
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key1", "newvalue1")
        self.assertEquals(cache.get("key1"), "newvalue1")
        self.assertEquals(cache.get("key2"), "value2")

    def test_delete_isolated(self):
        cache = Cache()
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.delete("key1")
        self.assertIsNone(cache.get("key1"))
        self.assertEquals(cache.get("key2"), "value2")
