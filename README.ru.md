# Telegram Feedback Bot - II

⚠️ **Внимание**: проект всё ещё в разработке, используйте на свой страх и риск. 
Сообщения о багах и проблемах в секции [Issues](https://github.com/MasterGroosha/telegram-feedback-bot-topics/issues) 
очень желательны!

Перед вами простой Telegram-бот, который использует [форумы в Telegram](https://telegram.org/evolution#october-2022) 
для разделения разговоров с разными юзерами по разным топикам. По сути, это логическое развитие моего 
[stateless фидбек-бота](https://github.com/MasterGroosha/telegram-feedback-bot).

## Технологии

* Python 3.11
* PostgreSQL 17
* aiogram 3.x
* SQLAlchemy 2.x
* psycopg3 (он же – psycopg)  
и другие...

## Запуск

* Клонируйте репозиторий и зайдите в получившийся каталог командой `cd`.
* Скопируйте файл `settings.example.toml` под именем `settings.toml` и заполните своими значениями.
* Скопируйте файл `docker-compose.example.yml` под именем `docker-compose.yml` и заполните своими значениями. Данные для PostgreSQL должны совпадать с теми, что указаны в `settings.toml`.
* Возьмите любой `.ftl`-файл из `bot/locale/examples`, отредактируйте, если надо, положите где-нибудь и укажите путь к файлу в `docker-compose.yml` в секции `bot`.
* Запустите бота с миграциями: `docker compose --profile migrate up --build`.