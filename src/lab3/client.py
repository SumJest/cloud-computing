import time
import grpc
import citygame_pb2
import citygame_pb2_grpc

def main():
    name = input("Введите ваше имя: ").strip()
    host = input("Введите адрес сервера (по умолчанию localhost:50051): ").strip() or "localhost:50051"

    # Создаём канал и «заглушку»
    channel = grpc.insecure_channel(host)
    stub = citygame_pb2_grpc.CityGameStub(channel)

    # 1) Присоединяемся
    join_resp = stub.JoinGame(citygame_pb2.JoinRequest(name=name))
    print(join_resp.message)

    # 2) Основной цикл: опрашиваем состояние и ходим, когда очередь до нас
    while True:
        state = stub.GetGameState(citygame_pb2.GameStateRequest())
        if state.finished:
            print(f"Игра завершена. Победитель: {state.winner or '—'}")
            break

        if state.current_turn != name:
            # Не наш ход — ждём 1 секунду и повторяем
            time.sleep(1)
            continue

        # Наш ход
        prev = state.last_city or "(первый ход)"
        city = input(f"Ваш ход (предыдущий: {prev}): ").strip()
        resp = stub.PlayCity(citygame_pb2.CityRequest(name=name, city=city))
        print(resp.message)
        if resp.eliminated:
            print("Вы выбыли из игры.")
            break
        # после хода сразу обновим состояние, чтобы не идти в begin of loop
        time.sleep(0.5)

if __name__ == "__main__":
    main()
