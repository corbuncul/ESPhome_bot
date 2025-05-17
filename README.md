# ESPHome bot
python telegram bot

Бот для получения данных с локальной ESPHome
## Для запуска api проекта необходимо:
- Клонировать репозиторий и перейти в него в командной строке:
```
git clone https://github.com/corbuncul/ESPhome_bot.git
cd ESPhome_bot
```
- Cоздать и активировать виртуальное окружение:
```
python3 -m venv env
source env/bin/activate
```
- Установить зависимости из файла requirements.txt:
```
python3 -m pip install --upgrade pip
pip install -r requirements.txt
```
- создать файл .env и внести в него следующие настройки:
```
TELEGRAM_TOKEN=<Токен бота>
TELEGRAM_CHAT_ID=<Ваш chat_id>
```
- Запустить проект:
```
python3 esphomebot.py
```

## Для запуска проекта в docker необходимо:
- создать файл .env и внести в него следующие настройки:
```
TELEGRAM_TOKEN=<Токен бота>
TELEGRAM_CHAT_ID=<Ваш chat_id>
```
- запустить проект командой:
```
docker compose up -d
```
- Можно пользоваться. Введите команду ```/start``` своему боту.
