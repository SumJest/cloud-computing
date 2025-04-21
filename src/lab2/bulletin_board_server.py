import socket
import threading
import argparse

parser = argparse.ArgumentParser(description="Сервер доски объявлений")
parser.add_argument("--host", default="127.0.0.1", help="Хост (по умолчанию 127.0.0.1)")
parser.add_argument("--port", type=int, default=7000, help="Порт (по умолчанию 7000)")
args = parser.parse_args()

FILE_PATH = "messages.txt"

def handle_client(conn, addr):
    print(f"[Доска объявлений] Подключено: {addr}")
    with conn:
        while True:
            data = conn.recv(1024).decode().strip()
            if data == "":
                break
            elif data.upper() == "LIST":
                try:
                    with open(FILE_PATH, "r", encoding="utf-8") as f:
                        messages = f.read().replace(";", "\n")
                except FileNotFoundError:
                    messages = "(нет сообщений)"
                conn.sendall(messages.encode())
            else:
                with open(FILE_PATH, "a", encoding="utf-8") as f:
                    f.write(data + ";")
                conn.sendall(f'Message added: "{data}"\n'.encode())

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server.bind((args.host, args.port))
    server.listen()
    print(f"[Доска объявлений] Сервер запущен на {args.host}:{args.port}")
    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr)).start()