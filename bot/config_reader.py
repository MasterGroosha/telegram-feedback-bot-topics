from enum import Enum
from os import getenv
from pathlib import Path
from typing import Optional

from pydantic import SecretStr, BaseModel, RedisDsn, model_validator, PostgresDsn, Field
from yaml import load as yaml_load

try:
    from yaml import CSafeLoader as Loader
except ImportError:
    from yaml import Loader


class FSMModeEnum(str, Enum):
    MEMORY = "memory"
    REDIS = "redis"


class RedisSettings(BaseModel):
    dsn: RedisDsn


class PostgresSettings(BaseModel):
    dsn: PostgresDsn


class BotSettings(BaseModel):
    token: SecretStr
    forum_supergroup_id: int
    ignored_topics_ids: set[int] = Field(default_factory=set)
    fsm_mode: FSMModeEnum
    language: str
    albums_preserve_enabled: bool = False
    albums_wait_time_seconds: int = 3.0


class Settings(BaseModel):
    redis: Optional[RedisSettings] = None
    postgres: PostgresSettings
    bot: BotSettings  # Must be the last one, since it checks for fsm_mode

    @model_validator(mode="after")
    def validate_fsm_mode(self) -> 'Settings':
        if self.bot.fsm_mode == FSMModeEnum.REDIS:
            if self.redis is None or self.redis.dsn is None:
                raise ValueError('"Redis" FSM mode selected, but no Redis DSN provided')
        return self


def parse_settings(local_file_name: str = "settings.yml") -> Settings:
    file_path = getenv("FEEDBACK_BOT_CONFIG_PATH")
    if file_path is not None:
        # Check if path exists
        if not Path(file_path).is_file():
            raise ValueError("Path %s is not a file or doesn't exist", file_path)
    else:
        parent_dir = Path(__file__).parent.parent
        settings_file = Path(Path.joinpath(parent_dir, local_file_name))
        if not Path(settings_file).is_file():
            raise ValueError("Path %s is not a file or doesn't exist", settings_file)
        file_path = settings_file.absolute()
    with open(file_path, "rt") as file:
        config_data = yaml_load(file, Loader)
    return Settings.model_validate(config_data)
