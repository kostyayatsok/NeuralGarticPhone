import time as timelib
import random
import BotAPI
import InternetAPI


# класс игрока
class PlayerTG:

    def __init__(self, tg_id, numId, username, room_id):
        self.tg_id = tg_id          # ТГ-ИД
        self.numId = numId          # Номер (не используется)
        self.username = username    # Имя юзера
        self.room_id = room_id
        self.is_admin = False       # Админ ли?
        self.next_id = 0
        self.cur_image = ''
        self.cur_text = ''
        self.neuro_text_asker = False
        self.neuro_image_asker = False
        self.text_task = ''
        self.image_task = ''
        print('player {0} with id {1} has been created'.format(self.username, self.tg_id))

    async def request_text(self, image_path):
        if self.neuro_text_asker:
            if image_path == '':
                image_path = 'randomPictures/img' + str(random.randint(1, 8)) + '.jpg'
            if self.tg_id >= 100000000000 or (self.neuro_text_asker and self.neuro_image_asker):
                self.cur_text = None
                text_id = InternetAPI.post_image(image_path)
                self.text_task = text_id
        else:
            print('request text for {0} image is {1}'.format(self.tg_id, image_path))
            if image_path is None or image_path == '':
                await BotAPI.send_plain_text(self.room_id, self.tg_id, 'Придумай предложение')
            else:
                await BotAPI.send_photo_with_text(self.room_id, self.tg_id, image_path, 'Что на этой картинке?')

    async def request_image(self, text_data):
        if self.neuro_image_asker:
            if text_data == '':
                text_data = 'picture'
            if self.tg_id >= 100000000000 or (self.neuro_text_asker and self.neuro_image_asker):
                self.cur_image = None
                image_id = InternetAPI.post_text(text_data)
                self.image_task = image_id
        else:
            if text_data is None or text_data == '':
                text_data = 'something'
            await BotAPI.send_photo_with_text(self.room_id, self.tg_id, 'resources/emptyImage.jpg', 'Нарисуй: '+text_data)

    async def obtain_text(self):
        if self.neuro_text_asker:
            if self.tg_id >= 100000000000 or (self.neuro_text_asker and self.neuro_image_asker):
                text_id = self.text_task[1:-1]
                self.cur_text = InternetAPI.get_text(text_id)
                # ar = ['amogus', 'bebra', 'allfucks', 'sliv']
                # self.cur_text = ar[random.randint(0, 3)]
        return self.cur_text

    async def obtain_image(self):
        if self.neuro_image_asker:
            if self.tg_id >= 100000000000 or (self.neuro_text_asker and self.neuro_image_asker):
                image_id = self.image_task[1:-1]
                path = self.room_id + "/imgAI" + str(image_id) + str(self.tg_id) + ".jpg"
                self.cur_image = InternetAPI.get_image(image_id, path)
                # ar = 'randomPictures/img'
                # self.cur_image = ar + str(random.randint(1, 4)) + '.png'
        return self.cur_image


# Таймер с напоминалками
class PendingTimer:

    def __init__(self, room_id, time, pending, label, receivers):
        self.room_id = room_id
        self.time = time             # время на таймере
        self.pending = pending       # времена для напоминания (ОСТАЛОСЬ n секунд!!!)
        self.label = label           # текст напоминания
        self.run = False             # запущен?
        self.last_time = 0           # пред. время
        self.pending_iterator = 0    # итератор в массиве пендингов
        self.receivers = receivers   # получатели ТГ-ИД

    # запуск таймера
    def start(self):
        self.run = True
        self.last_time = timelib.perf_counter()
        self.pending_iterator = 0

    # стоп таймера
    def stop(self):
        self.run = False

    # адейтим True - вермя вышло, False - не вышло
    async def update(self):
        if not self.run:
            return False

        # апдейтим время
        current_time = timelib.perf_counter()
        delta = current_time - self.last_time
        self.last_time = current_time
        self.time -= delta

        # апдейтим пендинги
        iterator = self.pending_iterator
        while iterator < len(self.pending) and self.pending[iterator] >= self.time:
            for player_id in self.receivers:
                value = self.pending[iterator]
                await BotAPI.send_plain_text(self.room_id, player_id, self.label.format(value))
            self.pending_iterator += 1
            iterator = self.pending_iterator

        # чекаем, вышло ли время
        if self.time <= 0:
            self.stop()
            return True
        return False
