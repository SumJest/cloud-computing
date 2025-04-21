import socket
import threading
import argparse
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(threadName)s %(levelname)s %(message)s",
    handlers=[logging.StreamHandler()]
)


def sort_words(text):
    words = text.split()
    unique_words = sorted(set(words), key=str.lower)
    return "\n".join(unique_words)

parser = argparse.ArgumentParser(description="Сервер сортировки слов")
parser.add_argument("--host", default="127.0.0.1", help="Хост (по умолчанию 127.0.0.1)")
parser.add_argument("--port", type=int, default=6000, help="Порт (по умолчанию 6000)")
args = parser.parse_args()

def handle_client(conn, addr):
    logging.info(f"[Сортировка] Подключено: {addr}")
    with conn:
        while True:
            data = conn.recv(4096).decode()
            if not data:
                break
            result = sort_words(data)
            conn.sendall(result.encode() + b"\n")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server.bind((args.host, args.port))
    server.listen()
    logging.info(f"[Сортировка] Сервер запущен на {args.host}:{args.port}")
    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr)).start()