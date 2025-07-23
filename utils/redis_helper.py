from django.conf import settings
from utils.redis_client import RedisClient
from utils.redis_serializers import DjangoModelSerializer


class RedisHelper:

    @classmethod
    def _load_objects_to_cache(cls, key, objects):

        conn = RedisClient.get_connection()

        serialized_list = []
        for obj in objects[:settings.REDIS_LIST_LENGTH_LIMIT]:  # trigger db query
            serialized_data = DjangoModelSerializer.serialize(obj)
            serialized_list.append(serialized_data)

        if serialized_list:
            conn.rpush(key, *serialized_list)
            conn.expire(key, settings.REDIS_KEY_EXPIRE_TIME)

    @classmethod
    def load_objects(cls, key, queryset):
        conn = RedisClient.get_connection()

        if conn.exists(key):
            serialized_list = conn.lrange(key, 0, -1) # cache hit, get all data
            objects = []
            for serialized_data in serialized_list:
                deserialized_obj = DjangoModelSerializer.deserialize(serialized_data)
                objects.append(deserialized_obj)
            return objects
        # cache miss
        cls._load_objects_to_cache(key, queryset)

        return list(queryset)

    @classmethod
    def push_object(cls, key, obj, queryset):
        conn = RedisClient.get_connection()
        if not conn.exists(key):
            
            cls._load_objects_to_cache(key, queryset)
            return
        serialized_data = DjangoModelSerializer.serialize(obj)
        conn.lpush(key, serialized_data)
        conn.ltrim(key, 0, settings.REDIS_LIST_LENGTH_LIMIT - 1)

    @classmethod
    def get_count_key(cls, obj, attr):
        return '{}.{}:{}'.format(obj.__class__.__name__, attr, obj.id)
        
    @classmethod
    def incr_count(cls, obj, attr):
        conn = RedisClient.get_connection()
        key = cls.get_count_key(obj, attr)
        
        if conn.exists(key):
            return conn.incr(key)

        # back fill cache from db
        # 不执行+1 操作keying必须保证调用incr_count 之前 obj.attr已经+1过了
        obj.refresh_from_db()
        conn.set(key, getattr(obj, attr))
        conn.expire(key, settings.REDIS_KEY_EXPIRE_TIME)
        return getattr(obj, attr)
        
        

    @classmethod
    def decr_count(cls, obj, attr):
        conn = RedisClient.get_connection()
        key = cls.get_count_key(obj, attr)
        if conn.exists(key):
            return conn.decr(key)
        # back fill cache from db
        # 不执行-1 操作keying必须保证调用incr_count 之前 obj.attr已经-1过了
        obj.refresh_from_db()
        conn.set(key, getattr(obj, attr))
        conn.expire(key, settings.REDIS_KEY_EXPIRE_TIME)
        return getattr(obj, attr)
        
        
    @classmethod
    def get_count(cls, obj, attr):
        conn = RedisClient.get_connection()
        key = cls.get_count_key(obj, attr)
        count = conn.get(key)
        if count is not None:
            return int(count)

        obj.refresh_from_db() 	# 确保数据是最新的
        count = getattr(obj, attr)
        conn.set(key, count)
        return count