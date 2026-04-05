from upstash_redis import Redis
import os

redis = Redis(
    url=os.environ.get('UPSTASH_REDIS_REST_URL', 'http://127.0.0.1:6379'), 
    token=os.environ.get('UPSTASH_REDIS_REST_TOKEN', None)
)