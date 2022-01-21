class Init(object):
    BOT_TOKEN = ''  # Токен бота
    WLN_HOST = ''  # адрес серва (в конце слэш не ставить!)
    WLN_ADMIN_TOKEN = ''
    WLN_ADMIN_USER = ''  # имя пользователя администратора (не обязательно)

    DB_PATH = 'modules/sqlite3.db'

    # параметры ссылки для авторизации
    START_PARAMETER = 'access_hash'
    REDIRECT_URI = 'https://o-murphy.github.io/telegram_bot_redirect?start='
    REDIRECT_PARAMS = {
        'response_type': 'hash',
        'duration': 3600,
        'access_type': -1,
        'client_id': 'TelegramBot',
        'redirect_uri': REDIRECT_URI
    }

    # настройки для отправки сообщений (оптимальные, трогать не желательно):
    DEFAULTS = {
        'disable_notification': True,  # отключить звук уведомлений
        'disable_web_page_preview': True,  # отключить превью для ссылок
        'parse_mode': "html"  # режим парсинга сообщений
    }
