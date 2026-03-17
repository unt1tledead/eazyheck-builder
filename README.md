# EazyHeck — Remote PC Control via Telegram

Управление ПК через Telegram бота на aiogram 3.

## Функции
- 📸 Скриншот
- 💻 Инфо о системе (CPU/RAM/Диск)
- ⚙️ Запуск команд в терминале
- 📁 Файловый менеджер (ls, download, upload)
- 🔧 Список процессов + kill
- 🔊 Управление громкостью
- 🔴 Запись экрана (mp4)
- 🔔 Уведомления на рабочий стол
- 📋 Буфер обмена (читать/записать)
- ⏻ Питание (блокировка, сон, перезагрузка, выключение)

## Установка

```bash
pip install -r requirements.txt
```

## Настройка

1. Скопируй `.env.example` → `.env`
2. Вставь токен бота (из @BotFather)
3. Вставь свой Telegram ID (можно узнать у @userinfobot)

```
BOT_TOKEN=ваш_токен
ALLOWED_USER_ID=ваш_id
```

## Запуск

```bash
python bot.py
```

## Структура

```
EazyHeck/
├── bot.py              # Точка входа
├── config.py           # Настройки
├── middleware.py        # Авторизация
├── requirements.txt
├── .env                # Секреты (не пушить в git!)
└── handlers/
    ├── basic.py        # Главное меню
    ├── screenshot.py
    ├── system_info.py
    ├── commands.py
    ├── files.py
    ├── processes.py
    ├── power.py
    ├── volume.py
    ├── screen_record.py
    ├── notifications.py
    └── clipboard.py
```
