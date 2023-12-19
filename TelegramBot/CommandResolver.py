from RoomMaster import players
from RoomMaster import rooms
from RoomMaster import Room
from RoomMaster import chats
import BotAPI
import random
import string


# команда на создание новой комнаты
async def create_command(user_id, chat_id=0, in_chat=False):
    if chat_id in chats.keys() or user_id in players.keys():
        if in_chat:
            room_id = chats[chat_id]
            room = rooms[room_id]
            if room.stage == 0:
                await room.destroy_room()
            else:
                await BotAPI.send_plain_text(user_id, 'Вы уже создали комнату!')
                return ''
        else:
            await BotAPI.send_plain_text(user_id, 'Вы уже создали комнату!')
            return ''

    # генерим рандомный ID комнаты
    letters = string.ascii_letters
    random_string = ''
    while random_string in rooms.keys() or len(random_string) == 0:
        random_string = ''.join(random.choice(letters) for i in range(8))
    print('room {0} has been created'.format(random_string))

    # создаём комнату и добавляем туда админа
    if in_chat:
        new_room = Room(random_string, chat_id)
        rooms[random_string] = new_room
        chats[chat_id] = random_string
        await BotAPI.send_plain_text(chat_id, 'Ваша комната: \"' + random_string + '\"')
    else:
        new_room = Room(random_string, 0)
        rooms[random_string] = new_room
        await BotAPI.send_plain_text(user_id, 'Ваша комната: \"' + random_string + '\"')
    return random_string


# команда на присоединение к комнате
async def join_command(user_data, room_id, in_chat=False, is_admin=False):
    player_id = user_data.id
    print('player {0} is trying to join room {1}'.format(user_data.id, room_id))

    if in_chat and room_id not in chats.keys():
        print('player used invalidated join button for room {0}'.format(room_id))
        return
    if in_chat:
        room_id = chats[room_id]

    # проверяем ID
    if room_id not in rooms.keys():
        await BotAPI.send_plain_text(player_id, 'Такой комнаты не существует!')
        return

    # игнорим /join если чел уже в комнате
    if player_id in rooms[room_id].player_map.keys():
        await BotAPI.send_plain_text(player_id, 'Вы уже находитесь в этой комнате!')
        return

    # если игра в процессе - не пускаем юзера
    room = rooms[room_id]
    if room.stage != 0:
        await BotAPI.send_plain_text(user_data.id, 'Вы не можете войти в комнату во время игры')
        return

    # юзер теперь в комнате
    await rooms[room_id].add_member(user_data, is_admin=is_admin)
    players[player_id] = room_id
    await BotAPI.send_plain_text(user_data.id, 'Добро пожаловать, игра скоро начнется')


# команда на покидание комнаты
async def leave_command(user_data):
    print('player {0} is trying to leave'.format(user_data.id))
    player_id = user_data.id

    # чел не находится в комнате
    if player_id not in players.keys():
        await BotAPI.send_plain_text(player_id, 'Вы ещё не участвуете в играх!')
        return

    # RIP челик
    room_id = players[player_id]
    await rooms[room_id].remove_member(user_data.id)
    await BotAPI.send_plain_text(user_data.id, 'Прощай')


# команда на запуск игры
async def start_command(user_data):
    print('player {0} is trying to start'.format(user_data.id))
    player_id = user_data.id

    # нельзя начать несуществующую игру
    if player_id not in players.keys():
        await BotAPI.send_plain_text(player_id, 'Вы ещё не участвуете в играх!')
        return

    # только админ может начать игру
    room = rooms[players[player_id]]
    if not room.player_map[player_id].is_admin:
        await BotAPI.send_plain_text(player_id, 'Вы не ведущий этой игры!')
        return

    # начинаем
    await room.start_game()


# команда на вывод всей истории текст->картинка (альбомов)
async def history_command(user_data):
    print('player {0} is trying to print history'.format(user_data.id))
    player_id = user_data.id

    # чел не в комнате после 22:15?
    if player_id not in players.keys():
        await BotAPI.send_plain_text(player_id, 'Вы ещё не участвуете в играх!')
        return

    # только админ может вывести альбомы игры
    room = rooms[players[player_id]]
    if not room.player_map[player_id].is_admin:
        await BotAPI.send_plain_text(player_id, 'Вы не ведущий этой игры!')
        return

    # выводим алюбомчики
    await room.print_history()


# команда на вывод списка игроков
async def list_command(user_data):
    print('player {0} is trying to stop'.format(user_data.id))
    player_id = user_data.id

    # челик в комнате?
    if player_id not in players.keys():
        await BotAPI.send_plain_text(player_id, 'Вы ещё не участвуете в играх!')
        return

    # всё ок, выводим
    room = rooms[players[player_id]]
    await room.list_member(user_data)


# команда на установку лимита по времени на раунд
async def time_command(user_data, text_data):
    print('player {0} is trying to re-time to {1}'.format(user_data.id, text_data))
    player_id = user_data.id

    # челик в комнате?
    if player_id not in players.keys():
        await BotAPI.send_plain_text(player_id, 'Вы ещё не участвуете в играх!')
        return

    # только админ может менять настройки
    room = rooms[players[player_id]]
    if not room.player_map[player_id].is_admin:
        await BotAPI.send_plain_text(player_id, 'Вы не ведущий этой игры!')
        return

    # нам отправили какую-то лажу
    if not text_data.isdigit():
        await BotAPI.send_plain_text(player_id, 'Неверное значение параметра')
        return

    # нам отправили какую-то лажу X2
    if int(text_data) > 100000 or int(text_data) == 0:
        await BotAPI.send_plain_text(player_id, 'Это плохая идея :)')
        return

    # всё ок, сетаем
    await room.reset_time(int(text_data))


# команда на изменение качества генерации
async def quality_command(user_data, text_data):
    print('player {0} is trying to re-quality to {1}'.format(user_data.id, text_data))
    player_id = user_data.id

    # челик в комнате?
    if player_id not in players.keys():
        await BotAPI.send_plain_text(player_id, 'Вы ещё не участвуете в играх!')
        return

    # только админ может менять настройки
    room = rooms[players[player_id]]
    if not room.player_map[player_id].is_admin:
        await BotAPI.send_plain_text(player_id, 'Вы не ведущий этой игры!')
        return

    # нам отправили какую-то лажу
    if not text_data.isdigit():
        await BotAPI.send_plain_text(player_id, 'Неверное значение параметра')
        return

    # всё ок, сетаем
    await room.reset_quality(int(text_data))


# команда на остановку игры, ВСЕ ИГРОКИ ОСТАЮТСЯ В КОМНАТАХ
async def stop_command(user_data):
    print('player {0} is trying to stop'.format(user_data.id))
    player_id = user_data.id

    # А мы вообще хоть в комнате??
    if player_id not in players.keys():
        await BotAPI.send_plain_text(player_id, 'Вы ещё не участвуете в играх!')
        return

    # только админ может стопнуть игру
    room = rooms[players[player_id]]
    if not room.player_map[player_id].is_admin:
        await BotAPI.send_plain_text(player_id, 'Вы не ведущий этой игры!')
        return

    # стоп
    await room.stop_game()


# команда на отправку подписи картинки боту
async def apply_command(user_data, text_data):
    print('player {0} is trying to apply {1}'.format(user_data.id, text_data))
    player_id = user_data.id

    # у нас есть комната (x8)?
    if player_id not in players.keys():
        await BotAPI.send_plain_text(player_id, 'Вы ещё не участвуете в играх!')
        return

    # круто, пора apply-ить
    room = rooms[players[player_id]]
    await room.apply_text(user_data, text_data)