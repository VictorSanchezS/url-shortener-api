import os
from dotenv import load_dotenv
import redis

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://cache:6379/0")

redis_client = redis.from_url(REDIS_URL, decode_responses=True)


def guardar_en_cache(codigo_corto: str, url_original: str, ttl_segundos: int = 3600):
    redis_client.set(f"url:{codigo_corto}", url_original, ex=ttl_segundos)


def obtener_de_cache(codigo_corto: str) -> str | None:
    return redis_client.get(f"url:{codigo_corto}")


def eliminar_de_cache(codigo_corto: str):
    redis_client.delete(f"url:{codigo_corto}")