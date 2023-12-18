import random
import BotAPI
from GameUtils import PlayerTG
from GameUtils import PendingTimer
import asyncio


# Собственно класс комнаты
class Room:

    def __init__(self, id_in):
        self.room_id = id_in      # ID комнаты
        self.cycle_list = []      # Список ТГ-ИД игроков в порядке их обхода (тот самый "цикл")
        self.player_map = {}      # ТГ-ИД --> Player словарь
        self.cycle_map = {}       # ТГ-ИД --> ind словарь, где ind - индекс чела в массива cycle_list
        self.timer = None         # Текущий таймер
        self.stage = 0            # Стадия/режим работы: 0 == игра не начата, # 1 == игроки описывают картинку,
                                  # 2 == нейронка генерит картинки
        self.round = -1           # Номер раунда (только текстовые!)
        self.max_rounds = -1      # Кол-во раундов (только текстовые!)
        self.tasks = []           # Пока что не используется
        self.image_history = {}   # ТГ-ИД --> [картинка], хранит цепочки картинок для альбома
        self.text_history = {}    # ТГ-ИД --> [текст], хранит цепочки подписей к картинкам для альбома

    # отправить сообщение всем игрокам
    async def send_plain_all(self, message):
        for user_id in self.player_map.copy().keys():
            await BotAPI.send_plain_text(user_id, message)

    # добавить игрока в комнату
    async def add_member(self, user_data, is_admin=False):
        user_id = user_data.id
        new_player = PlayerTG(user_id, len(self.cycle_list), user_data.username)
        new_player.is_admin = is_admin
        self.player_map[user_id] = new_player

        print(user_id, '(admin = {0}) now is in room'.format(is_admin), self.room_id)
        await self.send_plain_all('Игрок {0} зашёл в комнату!'.format(user_data.username))

    # вывести список игроков
    async def list_member(self, user_data):
        # объединям всех игроков в строку
        result = 'Игроки: '
        for player in self.player_map.copy().values():
            result += player.username
            result += ','
        result = result[:-1]

        await BotAPI.send_plain_text(user_data.id, result)

    # стереть комнату
    def destroy_room(self):
        print('room {0} has been destroyed'.format(self.room_id))
        rooms.pop(self.room_id)
        self.timer = None

    # выкинуть игрока
    async def remove_member(self, user_data):
        user_id = user_data.id
        is_admin = self.player_map[user_id].is_admin
        self.player_map.pop(user_id)
        players.pop(user_id)

        print(user_id, 'left the room ', self.room_id)
        await self.send_plain_all('Игрок {0} покинул комнату!'.format(user_data.username))

        # если в комнате пусто
        if len(self.player_map) == 0:
            self.destroy_room()
            return

        # если ливнул админ
        if is_admin:
            # ищем нового
            new_admin = None
            for user_id2 in self.player_map.copy().keys():
                new_admin = user_id2
                break

            # деалем его админом и оповещаем
            self.player_map[new_admin].is_admin = True
            await BotAPI.send_plain_text(new_admin, "Вы теперь ведущий!")

    # начало игры
    async def start_game(self):
        # инитаем всякое
        members = len(self.player_map.keys())
        self.round = -1
        self.max_rounds = members
        self.tasks = []
        self.timer = PendingTimer(11, [10, 5], 'Игра начнется через {0} секунд!', self.player_map.values())
        self.cycle_list = []
        self.cycle_map = {}

        # чистим историю
        for user_id in self.player_map.copy().keys():
            self.image_history[user_id] = []
            self.text_history[user_id] = []

        # генерим цикл
        # TODO: проверить этот недокод :)
        for user_id in self.player_map.copy().keys():
            self.cycle_list.append(user_id)
        for iteration in range(members * 2):
            ind1 = random.randint(0, members - 1)
            ind2 = random.randint(0, members - 1)
            if ind1 == ind2:
                continue
            self.cycle_list[ind1], self.cycle_list[ind2] = self.cycle_list[ind2], self.cycle_list[ind1]
        for i in range(len(self.cycle_list)):
            self.cycle_map[self.cycle_list[i]] = i
        print('The cycle is:', self.cycle_list)

        # выводим всех игроков
        all_users = ''
        for user_id in self.player_map.copy().keys():
            all_users += self.player_map[user_id].username
            all_users += ', '
        all_users = all_users[:-2]

        # начинаем!
        await self.send_plain_all('Ведущий запустил игру!')
        await self.send_plain_all('Игроки: ' + all_users)
        self.timer.start()

    # стоп-игра
    async def stop_game(self):
        self.stage = 0
        self.timer = None
        await self.send_plain_all('Игра окончена, ждём ведущего')
        return

    # принять текст от игрока
    async def apply_text(self, user_data, text_data):
        # мы в текстовом раунде?
        if self.stage != 1:
            await BotAPI.send_plain_text(user_data.id, 'Пока рано/поздно отправлять текст!')
            return

        user_id = user_data.id
        members = len(self.cycle_list)
        # ищем ИД первого челика из цепочки картинка-текст
        source_id = self.cycle_list[(self.cycle_map[user_id] - self.round + members) % members]
        self.text_history[source_id][-1] = text_data  # изменяем последний текст в истории (текст текущего раунда)
        await BotAPI.send_plain_text(user_data.id, 'Принято')

    # начало текстового раунда (дана картинка - введи подпись/предложение)
    async def text_round_start(self):
        self.round += 1
        self.timer = PendingTimer(30, [20, 10, 5], 'Осталось {0} секунд!', self.player_map.values())
        self.timer.start()
        self.stage = 1

        # добавляем пустую запись в историю (если чел вылетел - у него будет '' в качестве текста)
        members = len(self.text_history)
        for user_id in self.player_map.copy().keys():
            self.text_history[user_id].append('')

    # начало кариночного раунда (нейросеть генерит картинки)
    async def picture_round_start(self):
        self.timer = None
        self.stage = 2

        # добавляем пустую запись в историю (когда нейронка сгенерит - тут будет путь к картинке/сама картинка)
        members = len(self.image_history)
        for user_id in self.player_map.copy().keys():
            self.image_history[user_id].append('')
        #TODO: Отправляем тексты нейронке. Лучше всего нейронку пихать в отдельный поток
        #TODO: т.к. иначе весь бот для ВСЕХ уйдёт в АФК при ожидании генерации

    # апдейт кариночного раунда (нейросеть генерит картинки)
    async def picture_round_update(self):
        if len(self.tasks) == 0:
            # нейронка всё сгенерила!
            cycle_len = len(self.cycle_list)
            for i in range(cycle_len):
                from_id = self.cycle_list[i]  # первый чел из цепочки
                to_id = self.cycle_list[(i + self.round) % cycle_len]  # текущий игрок цепочки

                # пока что берём рандомную картинку и отправляем её
                img_name = 'randomPictures/img' + str(random.randint(1, 8)) + '.png'
                self.image_history[from_id][-1] = img_name
                await BotAPI.send_photo_with_text(to_id, img_name, 'Что на этой картинке?')

            # следующий раунд!
            await self.text_round_start()
            return
        # TODO: Ждём нейронку. Лучше всего нейронку пихать в отдельный поток
        # TODO: т.к. иначе весь бот для ВСЕХ уйдёт в АФК при ожидании генерации

    # вывод всех альбомов
    async def print_history(self):
        await self.send_plain_all('Альбомы: ')
        for i in range(len(self.cycle_list)):
            # для каждой цепочки...
            user_id = self.cycle_list[i]
            result = str(i + 1) + ': '
            for j in range((len(self.image_history[user_id])) + len(self.text_history[user_id])):
                # проходимся по её участникам
                if j % 2 == 0:
                    # это текст!
                    result += self.text_history[user_id][j // 2]
                else:
                    # а это картинка!
                    result += self.image_history[user_id][j // 2]
                current_id = self.cycle_list[(i + j) % len(self.cycle_list)]  # текущий чел из цепочки
                result += ' ({0}) ---> '.format(self.player_map[current_id].username)
            result = result[:-6]  # удаляем '--->'
            await self.send_plain_all(result)

    # апдейт комнаты
    async def room_update(self):
        if self.stage == 0:
            # до начала игры
            if self.timer is None:
                return
            timer_state = await self.timer.update()
            if timer_state:
                await self.send_plain_all('Придумайте предложение')
                await self.text_round_start()
        elif self.stage == 1:
            # текстовый раунд
            if self.timer is None:
                return
            timer_state = await self.timer.update()
            if timer_state:
                if self.round == self.max_rounds - 1:
                    # конец игры?
                    await self.stop_game()
                    return
                await self.picture_round_start()
        else:
            # картиночный раунд
            await self.picture_round_update()


# апдейт всего и вся
async def global_update():
    while True:
        for room_id in rooms.copy().keys():
            # апдейтим комнату
            room = rooms[room_id]
            await room.room_update()
        await asyncio.sleep(0.2)


rooms = {}     # 'ROOM_ID' --> Room, все комнаты
players = {}   # 'TG_ID' --> 'ROOM_ID', какой игрок в какой комнате
