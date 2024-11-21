# Telegram Feedback Bot - II

⚠️ **Внимание**: проект всё ещё в разработке, используйте на свой страх и риск. 
Сообщения о багах и проблемах в секции [Issues](https://github.com/MasterGroosha/telegram-feedback-bot-topics/issues) 
очень желательны!

Перед вами простой Telegram-бот, который использует [форумы в Telegram](https://telegram.org/evolution#october-2022) 
для разделения разговоров с разными юзерами по разным топикам. По сути, это логическое развитие моего 
[stateless фидбек-бота](https://github.com/MasterGroosha/telegram-feedback-bot).

## Технологии

* Python 3.12
* PostgreSQL 16
* Redis 7.x
* aiogram 3.x
* SQLAlchemy 2.x
* psycopg3 (aka psycopg)  
и другие...

## Запуск

Можно ориентироваться на [docker-compose.example.yml](docker-compose.example.yml) для локального запуска PostgreSQL и Redis. 
Заполните данные в [init-user-db.sh](postgres-firstrun/init-user-db.sh) или создайте юзера с базой вручную.

В файле `settings.yml` (основан на [settings.example.yml](settings.example.yml)) укажите настройки, подложите свои файлы 
локализации, согласно [инструкции](bot/locales/example/README.ru.md), и запустите бота. Docker-образы будут позднее.
