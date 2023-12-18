import time as timelib
import BotAPI


# класс игрока
class PlayerTG:

    def __init__(self, tg_id, numId, username):
        self.tg_id = tg_id          # ТГ-ИД
        self.numId = numId          # Номер (не используется)
        self.username = username    # Имя юзера
        self.is_admin = False       # Админ ли?
        print('player {0} with id {1} has been created'.format(self.username, self.tg_id))


# Таймер с напоминалками
class PendingTimer:

    def __init__(self, time, pending, label, receivers):
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
            for player in self.receivers:
                player_id = player.tg_id
                value = self.pending[iterator]
                await BotAPI.send_plain_text(player_id, self.label.format(value))
            self.pending_iterator += 1
            iterator = self.pending_iterator

        # чекаем, вышло ли время
        if self.time <= 0:
            self.stop()
            return True
        return False




