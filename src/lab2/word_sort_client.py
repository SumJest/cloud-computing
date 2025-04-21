import socket
import argparse

parser = argparse.ArgumentParser(description="Клиент сортировки слов")
parser.add_argument("--host", default="127.0.0.1", help="Хост (по умолчанию 127.0.0.1)")
parser.add_argument("--port", type=int, default=6000, help="Порт (по умолчанию 6000)")
args = parser.parse_args()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
    client.connect((args.host, args.port))
    print("Введите текст для сортировки слов (или пустую строку для выхода):")
    while True:
        text = input("> ")
        if not text:
            break
        client.sendall(text.encode())
        data = client.recv(4096).decode()
        print("Отсортированные слова:")
        print(data)