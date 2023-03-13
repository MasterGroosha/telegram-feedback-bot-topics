from pydantic import BaseSettings, SecretStr, RedisDsn


class Settings(BaseSettings):
    bot_token: SecretStr
    forum_supergroup_id: int
    remove_sent_confirmation: bool
    redis_dsn: RedisDsn

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


config = Settings()
