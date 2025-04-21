import socket

HOST = '127.0.0.1'
PORT = 12345

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server.bind((HOST, PORT))
    server.listen()
    print(f"TCP сервер запущен на {HOST}:{PORT}")

    conn, addr = server.accept()
    with conn:
        print(f"Подключено: {addr}")
        buffer = ""
        while True:
            data = conn.recv(1).decode()  # читаем по 1 байту
            if not data:
                break
            if data == '\r':
                continue  # игнорируем carriage return
            if data == '\n':
                print(f"Получено сообщение: {buffer}")
                conn.sendall(f"received: {buffer}\r\n".encode())
                buffer = ""
            else:
                buffer += data
