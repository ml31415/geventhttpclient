import time

import gevent.pool
import httpx

N = 1000
C = 10

url = "http://127.0.0.1/"


def run(client):
    response = client.get(url)
    assert response.status_code == 200


client = httpx.Client()
group = gevent.pool.Pool(size=C)

for i in range(5):
    now = time.time()
    for _ in range(N):
        group.spawn(run, client)
    group.join()

    delta = time.time() - now
    req_per_sec = N / delta

    print(f"request count:{N}, concurrenry:{C}, {req_per_sec} req/s")