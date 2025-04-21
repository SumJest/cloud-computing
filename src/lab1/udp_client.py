import socket

HOST = '127.0.0.1'
PORT = 54321

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client:
    while True:
        msg = input("Введите сообщение (или 'exit' для выхода): ")
        if msg.lower() == 'exit':
            break
        client.sendto(msg.encode(), (HOST, PORT))
        data, _ = client.recvfrom(1024)
        print(f"Ответ от сервера: {data.decode()}")