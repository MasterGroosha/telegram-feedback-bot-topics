from enum import Enum
from typing import Optional

from pydantic import BaseSettings, SecretStr, RedisDsn, PostgresDsn, BaseModel


class FSMModeEnum(str, Enum):
    MEMORY = "memory"
    REDIS = "redis"


class Redis(BaseModel):
    dsn: RedisDsn  # Without database id!
    fsm_db_id: int
    data_db_id: int


class Settings(BaseSettings):
    bot_token: SecretStr
    forum_supergroup_id: int
    redis: Optional[Redis]
    postgres_dsn: PostgresDsn
    fsm_mode: FSMModeEnum

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        env_nested_delimiter = '__'


config = Settings()
