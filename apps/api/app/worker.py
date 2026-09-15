from __future__ import annotations

import logging
import sys

from redis import Redis
from rq import Worker

from app.config import get_settings

logging.basicConfig(level=logging.INFO, stream=sys.stdout)


def main() -> None:
    settings = get_settings()
    redis_conn = Redis.from_url(settings.redis_url)
    worker = Worker(["acervo"], connection=redis_conn, name="acervo-worker")
    worker.work(with_scheduler=False)


if __name__ == "__main__":
    main()
