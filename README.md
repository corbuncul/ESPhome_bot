# ESPHome bot
python telegram bot

Бот для получения данных с локальной ESPHome, находящейся по адресу http://esptemppres.local/.
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
- Создать файл .env и внести в него следующие настройки:
```
TELEGRAM_TOKEN=<Токен бота>
TELEGRAM_CHAT_ID=<Ваш chat_id>
```
- При необходимости, измените BASE_NAME (адресс ESPhome) в файле esphomebot.py на адрес Вашей ESPhome.
- Также измените эндпоинты ENDPOINTS сенсоров Вашей ESPhome в файле esphomebot.py.
- Запустить проект:
```
python3 esphomebot.py
```
- Можно пользоваться. Введите команду ```/start``` своему боту.
