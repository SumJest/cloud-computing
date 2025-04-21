import socket
import argparse

parser = argparse.ArgumentParser(description="Клиент доски объявлений")
parser.add_argument("--host", default="127.0.0.1", help="Хост (по умолчанию 127.0.0.1)")
parser.add_argument("--port", type=int, default=7000, help="Порт (по умолчанию 7000)")
args = parser.parse_args()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
    client.connect((args.host, args.port))
    print("Доска объявлений (LIST — просмотр, сообщение — добавить, пустая строка — выход):")
    while True:
        msg = input("> ")
        client.sendall(msg.encode())
        if not msg:
            break
        data = client.recv(4096).decode()
        print(data)