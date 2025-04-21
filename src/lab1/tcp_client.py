import socket

HOST = '127.0.0.1'
PORT = 12345

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
    client.connect((HOST, PORT))
    print("Подключено к серверу.")

    while True:
        msg = input("Введите сообщение (или 'exit' для выхода): ")
        if msg.lower() == 'exit':
            break
        client.sendall((msg + '\n').encode())  # добавляем \n для корректной работы

        # получаем ответ построчно
        data = b""
        while not data.endswith(b'\n'):
            part = client.recv(1024)
            if not part:
                break
            data += part

        print(f"Ответ от сервера: {data.decode().strip()}")
