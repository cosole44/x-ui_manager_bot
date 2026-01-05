#!/bin/bash
set -e

# Настройки
PROJECT_DIR="/opt/x-ui_manager_bot"
REPO_URL="https://github.com/cosole44/x-ui_manager_bot.git"
SERVICE_NAME="x-ui_manager_bot"

# Проверка прав root
if [[ $EUID -ne 0 ]]; then
   echo "Пожалуйста, запустите скрипт с правами root: sudo ./install_bot.sh"
   exit 1
fi

# Создаём папку проекта
if [ -d "$PROJECT_DIR" ]; then
    echo "Папка $PROJECT_DIR уже существует. Пропускаем создание."
else
    mkdir -p "$PROJECT_DIR"
    echo "Создана папка $PROJECT_DIR"
fi

cd "$PROJECT_DIR"

# Клонируем репозиторий
if [ -d ".git" ]; then
    echo "Репозиторий уже клонирован. Пропускаем git clone."
else
    git clone "$REPO_URL" .
fi

# Запрос переменных для .env
echo "Введите токен бота (API_TOKEN):"
read -r API_TOKEN
echo "Введите PANEL_URL:"
read -r PANEL_URL
echo "Введите SUB_URL:"
read -r SUB_URL
echo "Введите USERNAME:"
read -r USERNAME
echo "Введите PASSWORD:"
read -r PASSWORD
echo "Введите INBOUND_ID:"
read -r INBOUND_ID

# Создаём .env
cat > .env <<EOL
API_TOKEN=$API_TOKEN
PANEL_URL=$PANEL_URL
SUB_URL=$SUB_URL
USERNAME=$USERNAME
PASSWORD=$PASSWORD
INBOUND_ID=$INBOUND_ID
EOL
chmod 600 .env
echo ".env создан"

# Создаём виртуальное окружение
if [ -d ".venv" ]; then
    echo "Виртуальное окружение уже существует. Пропускаем создание."
else
    python3 -m venv .venv
    echo "Виртуальное окружение создано"
fi

# Устанавливаем зависимости
source .venv/bin/activate
pip install --upgrade pip
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "requirements.txt не найден. Устанавливаем минимальные зависимости."
    pip install aiogram requests python-dotenv
fi
deactivate

# Создаём systemd-сервис
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME.service"

cat > "$SERVICE_FILE" <<EOL
[Unit]
Description=Telegram bot x-ui manager
After=network.target

[Service]
Type=simple
WorkingDirectory=$PROJECT_DIR
ExecStart=$PROJECT_DIR/.venv/bin/python $PROJECT_DIR/bot.py
Restart=always
User=root
EnvironmentFile=$PROJECT_DIR/.env

[Install]
WantedBy=multi-user.target
EOL

# Перезагружаем systemd и запускаем сервис
systemctl daemon-reload
systemctl enable $SERVICE_NAME
systemctl start $SERVICE_NAME

echo "✅ Установка завершена. Сервис $SERVICE_NAME запущен."
echo "Для просмотра логов используйте: journalctl -u $SERVICE_NAME -f"
