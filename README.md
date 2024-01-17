# Telegram Feedback Bot - II

> 🇷🇺 README на русском доступен [здесь](README.ru.md)

⚠️ **Warning**: project is still under development, use with caution. 
[Issues](https://github.com/MasterGroosha/telegram-feedback-bot-topics/issues) are greatly appreciated!

A simple Telegram bot which uses [Telegram Forums](https://telegram.org/evolution#october-2022) feature to 
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

## Run

You can use [docker-compose.example.yml](docker-compose.example.yml) file to deploy PostgreSQL and Redis locally. 
Fill new user and database data in [init-user-db.sh](postgres-firstrun/init-user-db.sh) file or do it manually.

Use `settings.yml` (based on [settings.example.yml](settings.example.yml)) to fill the necessary options, place your localization 
files (see relevant [README](bot/locales/example/README.md)), then run this bot. Docker images will follow soon.

```ini
cp settings.example.yml settings.yml
docker compose up -d --build
docker exec -it support-bot-topic bash
alembic upgrade head
mkdir bot/locales/en && cp bot/locales/example/strings_example_en.ftl bot/locales/en/strings_example_en.ftl
python -m bot
```

