
# Установка библиотек.
pip install python-telegram-bot==12.8 httplib2 oauth2client google-api-python-client google-auth-httplib2 google-auth-oauthlib pandas

# Ставим systemd (запустит бота и будет перезапускать его в случае падения.)
apt-get install systemd  # перемместить bot.service  в /etc/systemd/system

# Запуск бота
- systemctl daemon-reload
- systemctl enable bot
- systemctl start bot
- systemctl status bot
