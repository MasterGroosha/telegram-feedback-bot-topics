from pydantic import BaseSettings, SecretStr


class Settings(BaseSettings):
    bot_token: SecretStr
    forum_supergroup_id: int
    remove_sent_confirmation: bool

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


config = Settings()
