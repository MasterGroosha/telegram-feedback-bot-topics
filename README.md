# Telegram Feedback Bot - II

> 🇷🇺 README на русском доступен [здесь](README.ru.md)

⚠️ **Warning**: project is still under development, use with caution. 
[Issues](https://github.com/MasterGroosha/telegram-feedback-bot-topics/issues) are greatly appreciated!

A simple Telegram bot which uses [Telegram Forums](https://telegram.org/evolution#october-2022) feature to 
separate different users to different topics. This bot is the result of evolution of my 
[simple stateless feedback bot](https://github.com/MasterGroosha/telegram-feedback-bot).

## Used technology

* Python 3.11
* PostgreSQL 17
* aiogram 3.x
* SQLAlchemy 2.x
* psycopg3 (aka psycopg)  
and more...

## Run

* Clone this repo to your server and `cd` into it.
* Clone `settings.example.toml` as `settings.toml` and fill the variables.
* Clone `docker-compose.example.yml` as `docker-compose.yml` and edit PostgreSQL-related values to match those from `settings.toml`.
* Pick an example language `.ftl` file from `bot/locale/examples`, edit to your choice, then place it somewhere and specify its path in `docker-compose.yml` under `bot` service.
* Run the bot with migrations: `docker compose --profile migrate up --build`.