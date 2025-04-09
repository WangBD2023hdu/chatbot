import redis
import json
from datetime import timedelta
import os
from typing import Optional, Dict, List, Any

class RedisManager:
    def __init__(self):
        self.redis_client = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            db=int(os.getenv('REDIS_DB', 0)),
            decode_responses=True
        )
        self.message_ttl = timedelta(minutes=30)  # 消息过期时间
        self.session_ttl = timedelta(hours=24)    # 会话过期时间
        self.global_ttl = timedelta(days=7)       # 全局状态过期时间

    def _get_session_key(self, token: str) -> str:
        return f"session:{token}"

    def _get_message_key(self, token: str) -> str:
        return f"messages:{token}"

    def _get_dependency_key(self, token: str, operation: str) -> str:
        return f"dependency:{token}:{operation}"

    def _get_global_key(self, key: str) -> str:
        return f"global:{key}"

    # 用户特定状态管理
    def store_message(self, token: str, message: Dict[str, Any]) -> None:
        """存储消息到 Redis"""
        key = self._get_message_key(token)
        self.redis_client.rpush(key, json.dumps(message))
        self.redis_client.expire(key, self.message_ttl)

    def get_recent_messages(self, token: str, count: int = 5) -> List[Dict[str, Any]]:
        """获取最近的消息"""
        key = self._get_message_key(token)
        messages = self.redis_client.lrange(key, -count, -1)
        return [json.loads(msg) for msg in messages]

    def set_dependency(self, token: str, operation: str, dependency_data: Dict[str, Any]) -> None:
        """设置操作依赖"""
        key = self._get_dependency_key(token, operation)
        self.redis_client.set(key, json.dumps(dependency_data))
        self.redis_client.expire(key, self.session_ttl)

    def get_dependency(self, token: str, operation: str) -> Optional[Dict[str, Any]]:
        """获取操作依赖"""
        key = self._get_dependency_key(token, operation)
        data = self.redis_client.get(key)
        return json.loads(data) if data else None

    def check_dependency(self, token: str, operation: str, required_dependencies: List[str]) -> bool:
        """检查依赖是否满足"""
        for dep in required_dependencies:
            if not self.get_dependency(token, dep):
                return False
        return True

    def clear_session(self, token: str) -> None:
        """清除会话数据"""
        # 清除消息
        self.redis_client.delete(self._get_message_key(token))
        # 清除依赖
        pattern = self._get_dependency_key(token, "*")
        for key in self.redis_client.keys(pattern):
            self.redis_client.delete(key)

    # 全局状态管理
    def set_global_state(self, key: str, value: Any) -> None:
        """设置全局状态"""
        redis_key = self._get_global_key(key)
        self.redis_client.set(redis_key, json.dumps(value))
        self.redis_client.expire(redis_key, self.global_ttl)

    def get_global_state(self, key: str) -> Optional[Any]:
        """获取全局状态"""
        redis_key = self._get_global_key(key)
        data = self.redis_client.get(redis_key)
        return json.loads(data) if data else None

    def increment_global_counter(self, key: str) -> int:
        """增加全局计数器"""
        redis_key = self._get_global_key(key)
        return self.redis_client.incr(redis_key)

    def get_global_counter(self, key: str) -> int:
        """获取全局计数器"""
        redis_key = self._get_global_key(key)
        return int(self.redis_client.get(redis_key) or 0)

# 创建全局 Redis 管理器实例
redis_manager = RedisManager() 