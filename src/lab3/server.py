import logging
import grpc
from concurrent import futures
import argparse
import random
import time
import threading

import citygame_pb2
import citygame_pb2_grpc
from load_cities import load_russian_cities

# Инициализация логгера
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

MAX_TURN_TIME = 30  # секунд
CITY_LIST = []  # будет загружен из файла

class GameSession:
    def __init__(self):
        self._reset()
        self.lock = threading.Lock()
        logging.info("GameSession создана.")

    def _reset(self):
        self.players = []
        self.current_index = 0
        self.used_cities = set()
        self.last_city = ''
        self.finished = False
        self.winner = None
        self.turn_deadline = None
        self.turn_thread = None
        logging.info("Сессия игры сброшена.")

    def add_player(self, name: str) -> str:
        with self.lock:
            if self.finished:
                logging.info("Добавление игрока после завершения: перезапуск игры.")
                self._reset()

            if name in self.players:
                logging.info(f"Игрок '{name}' уже в игре.")
                return f'{name}, вы уже в игре.'

            self.players.append(name)
            logging.info(f"Игрок '{name}' добавлен. Всего игроков: {len(self.players)}.")

            if len(self.players) == 2:
                random.shuffle(self.players)
                logging.info(f"Игроки перемешаны: {self.players}. Начало игры.")
                self.start_turn_timer()
                return f'{name}, вы присоединились к игре. Игра начинается!'
            elif len(self.players) > 2:
                return f'{name}, вы присоединились к игре.'
            else:
                return f'{name}, вы присоединились к игре. Ждем второго игрока.'

    def start_turn_timer(self):
        self.turn_deadline = time.time() + MAX_TURN_TIME
        self.turn_thread = threading.Thread(target=self._turn_watchdog, daemon=True)
        self.turn_thread.start()
        logging.info(f"Таймер хода запущен. Время до дедлайна: {MAX_TURN_TIME} секунд.")

    def _turn_watchdog(self):
        while True:
            time.sleep(1)
            with self.lock:
                if self.turn_deadline is None or self.finished:
                    return
                if time.time() > self.turn_deadline:
                    player = self.players[self.current_index]
                    logging.info(f"[Watchdog] Игрок '{player}' не успел в срок. Выбывает.")
                    self.players.pop(self.current_index)
                    if len(self.players) == 1:
                        self.finished = True
                        self.winner = self.players[0]
                        logging.info(f"Игра завершена. Победитель: {self.winner}.")
                        return
                    self.current_index %= len(self.players)
                    self.turn_deadline = time.time() + MAX_TURN_TIME
                    logging.info(f"Следующий игрок: {self.players[self.current_index]}. Таймер перезапущен.")

    def play_turn(self, name: str, city: str):
        with self.lock:
            city_clean = city.lower().strip()
            logging.info(f"Ход игрока '{name}': город='{city_clean}'.")

            if self.finished:
                logging.info("Ход после завершения игры.")
                return 'Игра уже завершена.', False, '', True

            if not self.players or self.players[self.current_index] != name:
                logging.info(f"Сейчас не ход игрока '{name}'.")
                return 'Сейчас не ваш ход.', False, '', False

            if city_clean in self.used_cities:
                logging.info(f"Город '{city_clean}' уже использован.")
                self._eliminate(name)
                return 'Город уже был использован. Вы выбываете.', False, '', True

            if city_clean not in CITY_LIST:
                logging.info(f"Город '{city_clean}' отсутствует в списке.")
                self._eliminate(name)
                return 'Города нет в списке. Вы выбываете.', False, '', True

            if self.last_city:
                last = self.last_city[-1]
                if last in 'ьъы' and len(self.last_city) > 1:
                    last = self.last_city[-2]
                if not city_clean.startswith(last):
                    logging.info(f"Неправильная буква: ожидалась '{last}'.")
                    self._eliminate(name)
                    return f'Нужно назвать город на "{last.upper()}". Вы выбываете.', False, '', True

            # Успешный ход
            self.used_cities.add(city_clean)
            self.last_city = city_clean
            logging.info(f"Принят город '{city_clean}'. Использованные: {self.used_cities}.")

            if len(self.players) == 1:
                self.finished = True
                self.winner = name
                logging.info(f"Игра завершена. Победитель: {self.winner}.")
                return 'Вы победили!', True, '', False

            # Переход хода
            self.current_index = (self.current_index + 1) % len(self.players)
            nxt = self.last_city[-1]
            if nxt in 'ьъы' and len(self.last_city) > 1:
                nxt = self.last_city[-2]
            self.turn_deadline = time.time() + MAX_TURN_TIME
            logging.info(f"Передан ход игроку '{self.players[self.current_index]}'. Следующая буква: '{nxt}'.")
            return f'Принято: {city_clean}', True, nxt, False

    def _eliminate(self, name: str):
        logging.info(f"Элиминируем игрока '{name}'.")
        self.players.remove(name)
        if len(self.players) == 1:
            self.finished = True
            self.winner = self.players[0]
            logging.info(f"Игра завершена. Победитель: {self.winner}.")
        else:
            self.current_index %= len(self.players)
            logging.info(f"Оставшиеся игроки: {self.players}. Следующий индекс: {self.current_index}.")

    def get_state(self):
        with self.lock:
            state = {
                'players': list(self.players),
                'last_city': self.last_city,
                'current_turn': self.players[self.current_index] if self.players else '',
                'finished': self.finished,
                'winner': self.winner or ''
            }
            logging.info(f"Запрошено состояние: {state}.")
            return state

class CityGameServicer(citygame_pb2_grpc.CityGameServicer):
    def __init__(self):
        self.session = GameSession()

    def JoinGame(self, request, context):
        logging.info(f"RPC JoinGame: имя='{request.name}'.")
        msg = self.session.add_player(request.name)
        return citygame_pb2.JoinReply(message=msg)

    def PlayCity(self, request, context):
        logging.info(f"RPC PlayCity: имя='{request.name}', город='{request.city}'.")
        msg, valid, nxt, elim = self.session.play_turn(request.name, request.city)
        return citygame_pb2.CityReply(
            message=msg,
            valid=valid,
            next_letter=nxt,
            eliminated=elim
        )

    def GetGameState(self, request, context):
        logging.info("RPC GetGameState");
        st = self.session.get_state()
        return citygame_pb2.GameStateReply(
            players=st['players'],
            last_city=st['last_city'],
            current_turn=st['current_turn'],
            finished=st['finished'],
            winner=st['winner']
        )


def serve(host: str, port: int):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    citygame_pb2_grpc.add_CityGameServicer_to_server(CityGameServicer(), server)
    addr = f"{host}:{port}"
    server.add_insecure_port(addr)
    logging.info(f"gRPC сервер запущен на {addr}")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=50051)
    args = parser.parse_args()
    CITY_LIST = load_russian_cities()
    logging.info(f"Загружено городов: {len(CITY_LIST)}.")
    serve(args.host, args.port)