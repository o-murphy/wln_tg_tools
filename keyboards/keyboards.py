from aiogram import types


def remove():
    kb = types.ReplyKeyboardRemove()
    return kb


def start(login_url):
    kb = types.InlineKeyboardMarkup(row_width=1)
    keys = [types.InlineKeyboardButton('Wialon Login', url=login_url),
            types.InlineKeyboardButton('Информация', url='https://telegra.ph/123-09-21-35')]
    return kb.add(*keys)


def start_logged():
    kb = types.InlineKeyboardMarkup(row_width=2)
    keys = [
        types.InlineKeyboardButton('Список объектов', callback_data='cicada'),
        types.InlineKeyboardButton('Информация', url='https://telegra.ph/123-09-21-35'),
        # types.InlineKeyboardButton('WiaTag QR', callback_data='wiatag'),
        types.InlineKeyboardButton('🔐 Выйти из аккаунта', callback_data='logout')
    ]
    kb.add(*keys)
    return kb


def charge_to_icon(value):
    if not value:
        return '⚠'
    elif 75 < value <= 100:
        return f'🟩 {value}%'
    elif 50 < value <= 75:
        return f'🟨 {value}%'
    elif 25 < value <= 50:
        return f'🟧 {value}%'
    elif 0 <= value <= 25:
        return f'🟥 {value}%'
    else:
        return '⚠'


def cicadas(cicadas):
    kb = types.InlineKeyboardMarkup(row_width=2)
    # keys = [types.InlineKeyboardButton(i['nm'], callback_data=f'cicada/{i["id"]}') for i in cicadas]

    keys = [types.InlineKeyboardButton(f"{charge_to_icon(i['last_charge'])} | {i['nm']}",
                                       callback_data=f'cicada/{i["id"]}') for i in cicadas]
    kb.add(*keys)
    kb.row(types.InlineKeyboardButton('↩ Назад', callback_data='start_cmd'),
           types.InlineKeyboardButton('Обновить 🔄', callback_data='cicada'))
    return kb


def details(object_id):
    kb = types.InlineKeyboardMarkup(row_width=2)
    keys = [
        types.InlineKeyboardButton('↩ Назад', callback_data='cicada'),
        types.InlineKeyboardButton('Обновить 🔄', callback_data=f'cicada/{object_id}'),
        types.InlineKeyboardButton('🔋 Сбросить заряд', callback_data=f'cicada/{object_id}/reset'),
        types.InlineKeyboardButton('Команды ▶', callback_data=f'cicada/{object_id}/cmd'),
        types.InlineKeyboardButton('Последнее местоположение 📍', callback_data=f'cicada/{object_id}/location'),
    ]
    return kb.add(*keys)


def reset_q(object_id):
    kb = types.InlineKeyboardMarkup(row_width=2)
    keys = [
        types.InlineKeyboardButton('↩ Назад', callback_data=f'cicada/{object_id}'),
        types.InlineKeyboardButton('Да 🆗', callback_data=f'cicada/{object_id}/reset/ok'),
    ]
    return kb.add(*keys)


def location(object_id, pos_y, pos_x, host, token):
    kb = types.InlineKeyboardMarkup(row_width=2)
    keys = [
        types.InlineKeyboardButton('❌ Закрыть', callback_data=f'cicada/{object_id}/location/close'),
        types.InlineKeyboardButton('Обновить 🔄', callback_data=f'cicada/{object_id}/location/update'),
        types.InlineKeyboardButton('🧭 В Google Maps', url=f'http://maps.google.com/maps?q={pos_y},{pos_x}'),
        types.InlineKeyboardButton('Wialon Локатор 📡', url=f'{host}/locator/index.html?t={token}')
    ]
    return kb.add(*keys)


def commands(object_id, cmds):
    kb = types.InlineKeyboardMarkup(row_width=1)
    keys = [
        types.InlineKeyboardButton(f'{cmd["n"]} ▶', callback_data=f'cicada/{object_id}/cmd/{cmd["p"]}')
        for cmd in cmds
    ]
    keys.append(types.InlineKeyboardButton('↩ Назад', callback_data=f'cicada/{object_id}'))
    return kb.add(*keys)


def wiatags(wiatags):
    kb = types.InlineKeyboardMarkup(row_width=2)
    keys = [types.InlineKeyboardButton(i['nm'], callback_data=f'wiatag/{i["id"]}') for i in wiatags]
    kb.add(*keys)
    kb.row(types.InlineKeyboardButton('↩ Назад', callback_data='start_cmd'),
           types.InlineKeyboardButton('Обновить 🔄', callback_data='wiatag'))
    return kb


def wiatags_new_qr(object_id):
    kb = types.InlineKeyboardMarkup(row_width=2)
    keys = [
        types.InlineKeyboardButton('↩ Назад', callback_data=f'wiatag'),
        types.InlineKeyboardButton('Да 🆗', callback_data=f'wiatag/{object_id}/new'),
    ]
    return kb.add(*keys)