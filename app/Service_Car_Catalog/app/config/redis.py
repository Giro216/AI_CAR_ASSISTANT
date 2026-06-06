import os

import redis

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

# Создаем пул соединений с автоматическим переподключением
pool = redis.ConnectionPool.from_url(REDIS_URL, decode_responses=True)
redis_client = redis.Redis(connection_pool=pool)


def get_redis() -> redis.Redis:
	return redis_client
