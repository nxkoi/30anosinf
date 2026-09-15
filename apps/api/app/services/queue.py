from __future__ import annotations

from redis import Redis
from rq import Queue

from app.config import get_settings


def get_redis() -> Redis:
    return Redis.from_url(get_settings().redis_url)


def get_queue() -> Queue:
    return Queue("acervo", connection=get_redis())


def enqueue_process_submission(submission_id: str) -> str:
    q = get_queue()
    job = q.enqueue("app.jobs.process_submission", submission_id, job_timeout=600)
    return job.id
