import hashlib

import time
from django.core.cache import cache
from django.db import connection


class CacheResult(object):
    def __init__(self, age=60 * 5):
        self.age = age

    @staticmethod
    def signature(f, f_self, *args, **kwargs):
        class_name = f_self.__class__.__name__
        callback_name = f.__name__
        args = str(args) + str(kwargs)
        hashed_args = hashlib.md5(args.encode('utf8')).hexdigest()
        key = class_name + '_' + callback_name + '_' + hashed_args
        return key

    def __call__(self, f):
        def wrap(f_self, *args, **kwargs):
            cache_key = self.signature(f, f_self, *args, **kwargs)
            result = cache.get(cache_key)
            if result is None:
                result = f(f_self, *args, **kwargs)
                cache.set(cache_key, result, self.age)
            return result

        return wrap


def timeit(method):
    def timed(*args, **kw):
        q_initial = len(connection.queries)
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()

        print('%r %2.2f s' % (method.__name__, te-ts))
        print('queries executed:', len(connection.queries) - q_initial)
        return result

    return timed
