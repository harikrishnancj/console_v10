import redis
from dotenv import load_dotenv
import os

load_dotenv()
redis_host = os.getenv("REDIS_HOST", "localhost")
redis_port = int(os.getenv("REDIS_PORT", "6379"))

redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
