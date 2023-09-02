start-text =
    Hello 👋
    You can use me to talk to my owner and receive messages from them. Just send any message here!

no =
    { $capitalization ->
       *[lowercase] no
        [capitalized] No
    }

yes =
    { $capitalization ->
       *[lowercase] yes
        [capitalized] Yes
    }

new-topic-intro =
    New user chat!

    { $name }
    ├── Telegram ID: <code>{ NUMBER($id, useGrouping: 0) }</code>
    ├── Username: { $username }
    ├── Language: { $language_code }
    └── Premium: { $has_premium }

error-couldnt-deliver =
    Error: couldn't find corresponding user_id. Message cannot be delivered.