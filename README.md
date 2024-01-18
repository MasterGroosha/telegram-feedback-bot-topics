# Telegram Feedback Bot - II

> 🇷🇺 README на русском доступен [здесь](README.ru.md)

⚠️ **Warning**: project is still under development, use with caution.
[Issues](https://github.com/MasterGroosha/telegram-feedback-bot-topics/issues) are
greatly appreciated!

A simple Telegram bot which
uses [Telegram Forums](https://telegram.org/evolution#october-2022) feature to
separate different users to different topics. This bot is the result of evolution of my
[simple stateless feedback bot](https://github.com/MasterGroosha/telegram-feedback-bot).

## Used technology

* Python 3.11
* PostgreSQL 15
* Redis
* aiogram 3.x
* SQLAlchemy 2.x
* psycopg3 (aka psycopg)  
  and more...

## Prepare to Run

- install docker.
- place your localization files (see relevant [README](bot/locales/example/README.md))

## Run locally

- create virtual environment `python -m venv venv`
- install dependencies `pip install -r requirements.txt`
- change postgres user and password in `compose.local.yml`
- fill `settings.yml` (copy from [settings.yml.example](settings.yml.example))
- start docker containers with redis and
  postgres `docker compose -f compose.local.yml up -d`
- (first run) apply migrations to DB `alembic upgrade head`
- start application `python -m bot`

## Run application in docker fully

- change postgres user and password in `compose.yml`
- fill `settings.prod.yml` (copy
  from [settings.prod.yml.example](settings.prod.yml.example))
- start docker compose `docker compose up -d`
- (first run) apply migrations to DB `docker compose exec tg_bot alembic upgrade head`

P.S.
If you get error `Could not create new topic     error_type=TelegramBadRequest
message=Bad Request: not enough rights to create a topic method=CreateForumTopic` -
Your bot must be an administrator (has permissions to create topics) in your's telegram
group.