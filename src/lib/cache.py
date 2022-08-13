from time import time

_DEFAULT_LIFETIME = 60


class CacheMissException(Exception):
    pass


class CacheTimeoutException(CacheMissException):
    pass


class CacheItem:
    def __init__(self, value: any, lifetime: float = None):
        self.born: float = time()
        self.lifetime = lifetime if lifetime is not None else _DEFAULT_LIFETIME
        self.value = value

    def is_valid(self, lifetime: float = None) -> bool:
        return (time() - self.born) < (lifetime if lifetime is not None else self.lifetime)

    def get(self) -> any:
        return self.value


class Cache:
    def __init__(self, lifetime: float = 60, debug_id: str = None):
        self.lifetime = lifetime
        self.items = {}
        self.debug_id = debug_id
        if debug_id:
            print("Debug on for cache", debug_id, "Default cache lifetime set to ", lifetime)

    def set(self, key: str, value: any, lifetime: float = None) -> None:
        lifetime: float = lifetime if lifetime is not None else self.lifetime
        self.items[key] = CacheItem(value, lifetime)
        if self.debug_id: print(f"{self.debug_id}: Set cache item {key} for {lifetime} seconds to value", value)

    def delete(self, key) -> None:
        del self.items[key]
        if self.debug_id: print(f"{self.debug_id}: Delete cache item {key}")

    def get_or_raise(self, key, lifetime: float = None) -> any:
        lifetime = lifetime if lifetime is not None else self.lifetime
        if key not in self.items:
            if self.debug_id: print(f"{self.debug_id}: Cache miss looking for key {key}")
            raise CacheMissException()
        if not self.items[key].is_valid():
            if self.debug_id: print(f"{self.debug_id}: Cache timeout for key {key}, deleting value")
            self.delete(key)
            raise CacheTimeoutException()
        value = self.items[key].get()
        if self.debug_id: print(f"{self.debug_id}: Cache hit, found key {key} with value", value)
        return self.items[key].get()

    def get_or_resolve(self, key: str, add_fn: callable, lifetime: float = None, item_lifetime: float = None) -> any:
        try:
            return self.get_or_raise(key, lifetime)
        except CacheMissException:
            pass

        if self.debug_id: print(f"{self.debug_id}: Cache miss finding item {key}, resolving with callable")
        value = add_fn(key)
        self.set(key, value, item_lifetime if item_lifetime is not None else self.lifetime)
        return value

    def get(self, key, lifetime: float = None) -> any:
        try:
            return self.get_or_raise(key, lifetime)
        except CacheMissException:
            return None

