import redis
import json

# Kết nối Redis
redis_client = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)

# Hàm để cache dữ liệu
def cache_content_file(file_id:int, answer:str,question : str):
    redis_client.set(f"FileID:{file_id} - question : {question}", json.dumps(answer), ex=3600)  # Cache trong 1 giờ

# Hàm để lấy dữ liệu từ cache
def get_cached_content_file(file_id : int,question : str):
    result = redis_client.get(f"FileID:{file_id} - question : {question}")
    if result:
        return json.loads(result)
    return None
