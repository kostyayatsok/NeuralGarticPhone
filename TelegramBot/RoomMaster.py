import random
import traceback
from io import BytesIO
from pathlib import Path
import BotAPI
from GameUtils import PlayerTG
from GameUtils import PendingTimer
from AlbumGenerator import Album
from PIL import Image
import requests
import asyncio
import shutil
from uuid import uuid4


# Собственно класс комнаты
class Room:

    def __init__(self, id_in, chat_id):
        self.room_id = id_in  # ID комнаты
        self.cycle_list = []  # Список ТГ-ИД игроков в порядке их обхода (тот самый "цикл")
        self.player_map = {}  # ТГ-ИД --> Player словарь
        self.cycle_map = {}  # ТГ-ИД --> ind словарь, где ind - индекс чела в массива cycle_list
        self.timer = None  # Текущий таймер
        self.round = -1  # Номер раунда
        self.stage = 0
        self.max_rounds = 1  # Кол-во раундов
        self.time_for_round = 30  # времени на один раунд (сек)
        self.chat_id = chat_id  # ИД чата, в котором бот
        self.albums = {}  # Альбомы!
        self.game_mode = 1
        self.may_send_text = False
        self.may_send_image = False
        self.gif_storage = []
        Path(id_in).mkdir(parents=True, exist_ok=True)

    # отправить сообщение всем игрокам
    async def send_plain_all(self, message, send_to_group=False):
        ok = True
        if send_to_group and self.chat_id != 0:
            if await BotAPI.send_plain_text(self.room_id, self.chat_id, message) == -1:
                ok = False
        else:
            for user_id in self.player_map.copy().keys():
                if await BotAPI.send_plain_text(self.room_id, user_id, message) == -1:
                    ok = False
        return ok

    async def send_photo_all(self, message, image_path, send_to_group=False):
        if send_to_group and self.chat_id != 0:
            await BotAPI.send_gif_with_text('0', self.chat_id, image_path, message)
        else:
            for user_id in self.player_map.copy().keys():
                await BotAPI.send_gif_with_text('0', user_id, image_path, message)

    def build_timer(self, time, pending, label):
        if self.chat_id == 0:
            self.timer = PendingTimer(self.room_id, time, pending, label, self.player_map.copy().keys())
        else:
            self.timer = PendingTimer(self.room_id, time, pending, label, self.player_map.copy().keys())

    # добавить игрока в комнату
    async def add_member(self, user_id, user_name, is_admin=False):
        user_id = user_id
        new_player = PlayerTG(user_id, len(self.cycle_list), user_name, self.room_id)
        new_player.is_admin = is_admin
        self.player_map[user_id] = new_player

        print(user_id, '(admin = {0}) now is in room'.format(is_admin), self.room_id)
        if user_id < 1000000000000:
            await self.send_plain_all('Игрок {0} зашёл в комнату!'.format(user_name), send_to_group=True)

    # вывести список игроков
    async def list_member(self, user_data):
        # объединям всех игроков в строку
        result = 'Игроки: '
        for player in self.player_map.copy().values():
            if player.tg_id >= 1000000000000:
                continue
            result += player.username
            result += ','
        result = result[:-1]

        await BotAPI.send_plain_text(self.room_id, user_data.id, result)

    # изменяем лимит по времени
    async def reset_time(self, new_time):
        self.time_for_round = new_time
        await self.send_plain_all(
            'Ведущий изменил лимит по времени! Новый лимит: {0} секунд'.format(new_time), send_to_group=True)

    async def reset_gamemode(self, new_gamemode):
        new_title = 'нейро-игрок'
        if new_gamemode == 1:
            new_title = 'нейро-художник'
        elif new_gamemode == 2:
            new_title = 'нейро-зритель'
        await self.send_plain_all('Ведущий изменил режим игры! Новый режим: '+new_title)
        self.game_mode = new_gamemode

    # стереть комнату
    async def destroy_room(self):
        for user_id in self.player_map.copy().keys():
            if user_id in self.player_map.keys():
                await self.remove_member(user_id, destroy_on_empty=False)
        print('room {0} has been destroyed'.format(self.room_id))
        rooms.pop(self.room_id)
        if self.chat_id != 0:
            chats.pop(self.chat_id)
        self.timer = None
        shutil.rmtree(self.room_id)
        await BotAPI.delete_messages(self.room_id)

    async def remove_member(self, user_id, destroy_on_empty=True):
        is_admin = self.player_map[user_id].is_admin
        username = self.player_map[user_id].username
        self.player_map.pop(user_id)
        if user_id in players.keys():
            players.pop(user_id)

        print(user_id, 'left the room ', self.room_id)
        if user_id < 1000000000000:
            await self.send_plain_all('Игрок {0} покинул комнату!'.format(username), send_to_group=True)

        # если в комнате пусто
        if len(self.player_map) == 0 and destroy_on_empty:
            await self.destroy_room()
            return

        # если ливнул админ
        if is_admin and self.chat_id != 0 and destroy_on_empty:
            await self.send_plain_all('Админ ливнул из игры!', send_to_group=True)
            await self.destroy_room()
        elif is_admin and destroy_on_empty:
            # ищем нового
            new_admin = None
            for user_id2 in self.player_map.copy().keys():
                new_admin = user_id2
                break

            # деалем его админом и оповещаем
            self.player_map[new_admin].is_admin = True
            await BotAPI.send_plain_text(self.room_id, new_admin, "Вы теперь ведущий!")

    # начало игры
    async def start_game(self):
        for user_id in self.player_map.copy().keys():
            if await BotAPI.send_plain_text(self.room_id, user_id, 'Время на раунд: '+str(self.time_for_round)) == -1:
                await self.send_plain_all('Не все пользователи имеют переписку с ботом!', send_to_group=True)
                return

        if self.game_mode == 1:
            for user_id in self.player_map.copy().keys():
                self.player_map[user_id].neuro_image_asker = True
                self.player_map[user_id].neuro_text_asker = False
        elif self.game_mode == 2:
            for user_id in self.player_map.copy().keys():
                self.player_map[user_id].neuro_image_asker = False
                self.player_map[user_id].neuro_text_asker = True
        elif self.game_mode == 0:
            ai_id = 1000000000000 + random.randint(1, 10000000)
            await self.add_member(ai_id, 'AI bot')
            self.player_map[ai_id].neuro_image_asker = True
            self.player_map[ai_id].neuro_text_asker = True

        members = len(self.player_map.keys())
        self.round = 0
        self.stage = 0
        self.max_rounds = 4
        self.build_timer(6, [5, 2], 'Игра начнется через {0} секунд!')
        self.cycle_list = []
        self.cycle_map = {}
        self.albums = {}
        self.may_send_text = False
        self.may_send_image = False

        for user_id in self.player_map.copy().keys():
            self.cycle_list.append(user_id)
        for iteration in range(members * 2):
            ind1 = random.randint(0, members - 1)
            ind2 = random.randint(0, members - 1)
            if ind1 == ind2:
                continue
            self.cycle_list[ind1], self.cycle_list[ind2] = self.cycle_list[ind2], self.cycle_list[ind1]
        if self.game_mode > 0:
            le = len(self.cycle_list)
            new_cycle = []
            for i in range(le):
                user_id = self.cycle_list[i]
                new_cycle.append(user_id)
                await self.add_member(user_id + 1000000000000,
                                      'AI')
                self.player_map[user_id + 1000000000000].neuro_image_asker = self.player_map[user_id].neuro_image_asker
                self.player_map[user_id + 1000000000000].neuro_text_asker = self.player_map[user_id].neuro_text_asker

                new_cycle.append(user_id + 1000000000000)
            self.cycle_list = new_cycle
        for i in range(len(self.cycle_list)):
            self.cycle_map[self.cycle_list[i]] = i
        for user_id in self.player_map.copy().keys():
            iterator = (self.cycle_map[user_id] + 1) % (len(self.cycle_list))
            self.player_map[user_id].next_id = self.cycle_list[iterator]
        print('The cycle is:', self.cycle_list)

        # чистим историю
        for user_id in self.player_map.copy().keys():
            self.albums[user_id] = Album(self.player_map.copy(), self.room_id)

        all_users = ''
        for user_id in self.player_map.copy().keys():
            if self.player_map[user_id].tg_id >= 1000000000000:
                continue
            all_users += self.player_map[user_id].username
            all_users += ', '
        all_users = all_users[:-2]

        # начинаем!
        await self.send_plain_all('Ведущий запустил игру!', send_to_group=True)
        await self.send_plain_all('Игроки: ' + all_users, send_to_group=True)
        self.timer.start()

    # стоп-игра
    async def stop_game(self):
        self.timer = None
        self.round = -1
        self.stage = 0
        self.gif_storage = []

        for user_id in self.player_map.copy().keys():
            if user_id >= 1000000000000:
                await self.remove_member(user_id, destroy_on_empty=True)

        await self.send_plain_all('Игра окончена, ждём ведущего', send_to_group=True)
        return

    # вывод всех альбомов
    async def print_history(self):
        cnt = 0
        for i in range(len(self.cycle_list)):
            user_id = self.cycle_list[i]
            if user_id >= 1000000000000 and self.game_mode > 0:
                continue
            cnt += 1
        if cnt != len(self.gif_storage):
            await self.send_plain_all('Гифки пока не готовы, попробуйте ещё раз', send_to_group=True)
            return
        await self.send_plain_all('Альбомы: ', send_to_group=True)
        for path in self.gif_storage:
            await self.send_photo_all('', path, send_to_group=True)

    # принять картинку от игрока
    async def apply_image(self, user_data, file_id):
        # мы в картиночном раунде?
        user_id = user_data.id
        if not self.may_send_image:
            await BotAPI.send_plain_text(self.room_id, user_data.id, 'Пока рано/поздно/нельзя отправлять рисунок!')
            return

        image_path = self.room_id + '/user_sent_' + str(uuid4()) + '.jpg'
        await BotAPI.download_image_by_id(file_id, image_path)

        self.player_map[user_id].cur_image = image_path
        await BotAPI.send_plain_text(self.room_id, user_id, 'Принято')

    # принять текст от игрока
    async def apply_text(self, user_data, text_data):
        # мы в текстовом раунде?
        user_id = user_data.id
        if not self.may_send_text:
            await BotAPI.send_plain_text(self.room_id, user_data.id, 'Пока рано/поздно/нельзя отправлять текст!')
            return

        self.player_map[user_id].cur_text = text_data
        await BotAPI.send_plain_text(self.room_id, user_id, 'Принято')

    async def album_image(self):
        if self.round == 0:
            return
        cycle_len = len(self.cycle_list)
        for i in range(cycle_len):
            from_id = self.cycle_list[i]  # первый чел из цепочки
            current_iter = (i + self.round - 1) % cycle_len
            player_id = self.cycle_list[current_iter]
            await self.albums[from_id].add_image_page(self.max_rounds,
                                                      self.player_map[player_id].cur_image, player_id)

    async def album_text(self):
        if self.round == 0:
            return
        cycle_len = len(self.cycle_list)
        for i in range(cycle_len):
            from_id = self.cycle_list[i]  # первый чел из цепочки
            current_iter = (i + self.round - 1) % cycle_len
            player_id = self.cycle_list[current_iter]
            await self.albums[from_id].add_text_page(self.max_rounds,
                                                     self.player_map[player_id].cur_text, player_id)

    async def start_text_round(self):
        await self.album_image()
        await self.send_plain_all('Раунд '+str(self.round+1))

        self.round += 1
        self.stage = 1

        if self.round > self.max_rounds:
            await self.stop_game()
            return

        for user_id in self.player_map.copy().keys():
            print(user_id, self.player_map[user_id].next_id)
            image = self.player_map[user_id].cur_image
            next_id = self.player_map[user_id].next_id
            self.player_map[user_id].cur_image = 'resources/emptyImage.jpg'
            await self.player_map[next_id].request_text(image)

        if self.game_mode != 2:
            time = self.time_for_round
            self.build_timer(time + 1, [time, time // 2, time // 5], 'Осталось {0} секунд!')
            self.timer.start()
            self.may_send_text = True
        else:
            await self.send_plain_all('Ждите, тексты генерируются')

    async def start_image_round(self):
        await self.album_text()
        await self.send_plain_all('Раунд ' + str(self.round + 1))

        self.round += 1
        self.stage = 2

        if self.round > self.max_rounds:
            await self.stop_game()
            return

        for user_id in self.player_map.copy().keys():
            text_data = self.player_map[user_id].cur_text
            next_id = self.player_map[user_id].next_id
            self.player_map[user_id].cur_text = 'a random picture'
            await self.player_map[next_id].request_image(text_data)

        if self.game_mode != 1:
            time = self.time_for_round
            self.build_timer(time + 1, [time, time // 2, time // 5], 'Осталось {0} секунд!')
            self.timer.start()
            self.may_send_image = True
        else:
            await self.send_plain_all('Ждите, картинки генерируются')

    async def update_text_round(self):
        if self.timer is None:
            for user_id in self.player_map.copy().keys():
                obtained = await self.player_map[user_id].obtain_text()
                if obtained is None:
                    return
            await self.start_image_round()
            return
        timer_state = await self.timer.update()
        if timer_state:
            self.may_send_text = False
            self.timer = None
            for user_id in self.player_map.copy().keys():
                obtained = await self.player_map[user_id].obtain_text()
                if obtained is None:
                    await self.send_plain_all('Ждите, тексты генерируются')
                    return

    async def update_image_round(self):
        if self.timer is None:
            for user_id in self.player_map.copy().keys():
                obtained = await self.player_map[user_id].obtain_image()
                if obtained is None:
                    return
            await self.start_text_round()
            return
        timer_state = await self.timer.update()
        if timer_state:
            self.may_send_image = False
            self.timer = None
            for user_id in self.player_map.copy().keys():
                obtained = await self.player_map[user_id].obtain_image()
                if obtained is None:
                    await self.send_plain_all('Ждите, картинки генерируются')
                    return

    def check_gifs(self):
        cnt = 0
        for i in range(len(self.cycle_list)):
            if len(self.gif_storage) > cnt:
                continue
            user_id = self.cycle_list[i]
            if user_id >= 1000000000000 and self.game_mode > 0:
                continue
            cnt += 1
            album = self.albums[user_id]
            gif_path = self.room_id + '/' + 'resultGif' + str(i) + '.gif'
            album.make_gif(gif_path, 2000)
            self.gif_storage.append(gif_path)

    # апдейт комнаты
    async def room_update(self):
        if self.stage == 0:
            # до начала игры
            if self.timer is None:
                self.check_gifs()
                return
            timer_state = await self.timer.update()
            if timer_state:
                if self.game_mode == 2:
                    await self.start_image_round()
                else:
                    await self.start_text_round()
        elif self.stage == 1:
            # текстовый раунд
            await self.update_text_round()
        else:
            # картиночный раунд
            await self.update_image_round()


# апдейт всего и вся
async def global_update():
    while True:
        for room_id in rooms.copy().keys():
            # апдейтим комнату
            bad = False
            try:
                room = rooms[room_id]
                await room.room_update()
            except BaseException as err:
                print('EXCEPTION: ', err)
                traceback.print_stack()
                bad = True
            if bad:
                try:
                    room = rooms[room_id]
                    await room.stop_game()
                    await room.destroy_room()
                except BaseException as err:
                    print('EXCEPTION: ', err)
                    traceback.print_stack()
                    pass
        await asyncio.sleep(0.5)


rooms = {}  # 'ROOM_ID' --> Room, все комнаты
players = {}  # 'TG_ID' --> 'ROOM_ID', какой игрок в какой комнате
chats = {}
