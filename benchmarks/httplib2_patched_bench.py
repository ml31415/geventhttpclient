from geventhttpclient import httplib

httplib.patch()

import time
from contextlib import contextmanager

import gevent.pool
import gevent.queue
import httplib2


class ConnectionPool:
    def __init__(self, factory, size=5):
        self.factory = factory
        self.queue = gevent.queue.Queue(size)
        for i in range(size):
            self.queue.put(factory())

    @contextmanager
    def use(self):
        el = self.queue.get()
        yield el
        self.queue.put(el)


def httplib2_factory(*args, **kw):
    def factory():
        return httplib2.Http(*args, **kw)

    return factory


N = 1000
C = 10

url = "http://127.0.0.1/"


def run(pool):
    with pool.use() as http:
        http.request(url)


http_pool = ConnectionPool(httplib2_factory(), size=C)
group = gevent.pool.Pool(size=C)

for i in range(5):
    now = time.time()
    for _ in range(N):
        group.spawn(run, http_pool)
    group.join()

    delta = time.time() - now
    req_per_sec = N / delta

    print(f"request count:{N}, concurrenry:{C}, {req_per_sec} req/s")