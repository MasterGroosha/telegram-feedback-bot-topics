start-text =
    Привет 👋
    С моей помощью ты можешь связаться с моим владельцем. Просто отправь какое-либо сообщение!

no =
    { $capitalization ->
       *[lowercase] нет
        [capitalized] Нет
    }

yes =
    { $capitalization ->
       *[lowercase] да
        [capitalized] Да
    }

new-topic-intro =
    Новый чат!

    { $name }
    ├── Telegram ID: <code>{ NUMBER($id, useGrouping: 0) }</code>
    ├── Юзернейм: { $username }
    ├── Язык: { $language_code }
    └── Telegram Premium: { $has_premium }

error-couldnt-deliver =
    Ошибка: не удалось найти нужный user_id. Сообщение не доставлено.