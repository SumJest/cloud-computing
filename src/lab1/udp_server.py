import socket

HOST = '127.0.0.1'
PORT = 54321

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server:
    server.bind((HOST, PORT))
    print(f"UDP сервер запущен на {HOST}:{PORT}")
    
    while True:
        data, addr = server.recvfrom(1024)
        print(f"Получено от {addr}: {data.decode()}")
        server.sendto(data, addr)