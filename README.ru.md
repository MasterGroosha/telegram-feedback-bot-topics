# Telegram Feedback Bot - II

⚠️ **Внимание**: проект всё ещё в разработке, используйте на свой страх и риск.
Сообщения о багах и проблемах в
секции [Issues](https://github.com/MasterGroosha/telegram-feedback-bot-topics/issues)
очень желательны!

Перед вами простой Telegram-бот, который
использует [форумы в Telegram](https://telegram.org/evolution#october-2022)
для разделения разговоров с разными юзерами по разным топикам. По сути, это логическое
развитие моего
[stateless фидбек-бота](https://github.com/MasterGroosha/telegram-feedback-bot).

## Технологии

* Python 3.11
* PostgreSQL 15
* Redis
* aiogram 3.x
* SQLAlchemy 2.x
* psycopg3 (aka psycopg)  
  и другие...

## Подготовка к запуску

- установите docker
- подложите свои файлы локализации,
  согласно [инструкции](bot/locales/example/README.ru.md)

## Локальный запуск

- создайте виртуальное окружение `python -m venv venv`
- установите зависимости `pip install -r requirements.txt`
- в файле `compose.local.yml` укажите пользователя и пароль для postgres
- в файле `settings.yml` (основан на [settings.example.yml](settings.example.yml))
  укажите настройки (обязательно 'token' и 'forum_supergroup_id')
- запустите docker контейнеры `docker compose -f compose.local.yml up -d`
- (при первом запуске) выполните миграции `alembic upgrade head`
- и запустите бота `python -m bot`

## Запуск бота в контейнере

- в файле `compose.yml` укажите пользователя и пароль для postgres
- в файле `settings.prod.yml` (основан
  на [settings.prod.example.yml](settings.prod.example.yml))
  укажите настройки (обязательно 'token' и 'forum_supergroup_id')
- запустите docker контейнеры `docker compose up -d`
- (при первом запуске) выполните
  миграции `docker compose exec tg_bot alembic upgrade head`

Чтобы не ловить
ошибку `Could not create new topic     error_type=TelegramBadRequest
message=Bad Request: not enough rights to create a topic method=CreateForumTopic`
В вашей супергруппе с топиками бот должен иметь права на создание топиков (быть
администратором)