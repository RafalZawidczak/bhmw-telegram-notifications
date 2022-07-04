bhmw-telegram-notifications
=================

This project is dedicated to all those who need to stay up to date with navigational warnings sent by the Hydrographic Office of the Polish Navy (BHMW). Since these warnings are only officially published on the official website (https://bhmw.gov.pl/pl/warnings), it was decided to create a project that would send these alerts to the Telegram channel.

How it works
=================
1. Alerts are being scraped from https://bhmw.gov.pl/pl/warnings every 30 minutes.
2. The list of alerts from the previous run is compared to the current list of alerts. This is made to see if there are any new alerts. If so, they are sent to the Telegram channel.

Channel
=================
[You can find Telegram channel here](https://t.me/bhmw_warnings)

[Preview Channel content.](https://t.me/s/bhmw_warnings)

Tech
=================
- [Dropbox]
- [Github Actions]
- [Python]: 
- [Telegram]

[Python]: <https://python.org>
[Github Actions]: <https://github.com/features/actions>
[Dropbox]: <https://dropbox.com>
[Telegram]: <https://telegram.org>

To do
================
- Automatic translation of all warnings into English language. Currently these warnings, which are published by BHMW only in Polish language, are sent to the telegram channel in Polish language.

