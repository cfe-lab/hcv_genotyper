import atexit
import functools
import hashlib
import shelve
import typing as ty

CachedType = ty.TypeVar("CachedType")


class HomogeneousCache(ty.Generic[CachedType]):
    def __init__(self, filename: str) -> None:
        self.cache = shelve.open(filename)
        atexit.register(self.save)

    def save(self) -> None:
        self.cache.sync()

    @staticmethod
    def hash_args(args):
        hash_obj = hashlib.md5()
        for arg in args:
            if type(arg) is not str:
                arg = str(arg)
            hash_obj.update(bytes(arg, "utf8"))
        return hash_obj.hexdigest()

    def get(
        self, args: ty.Any, fn: ty.Callable[..., CachedType]
    ) -> CachedType:
        args_hash: str = self.hash_args(args)
        if args_hash not in self.cache:
            obj: CachedType = fn(*args)
            self.cache[args_hash] = obj
        return self.cache[args_hash]


def persistent_cache(filename):
    """Decorator to save a persistent cache (for alignments)"""

    T = ty.TypeVar("T")

    cache: HomogeneousCache[T] = HomogeneousCache(filename)

    def decorator(fn: ty.Callable[..., T]):
        @functools.wraps(fn)
        def wrapped(*args):
            obj = cache.get(args, fn)
            return obj

        return wrapped

    return decorator
