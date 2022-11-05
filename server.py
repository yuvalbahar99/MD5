"""
author: Yuval Bahar
date: 27/10/2022
description: The server connects to X clients. Sends to each of them
a hash string that needs to be decrypted. Divides the work according
the clients and their cores.
"""
# ----------------- IMPORTS -----------------


import socket
from threading import Thread, Lock


# ----------------- CONSTANTS -----------------


IP = "127.0.0.1"
PORT = 8080
QUEUE_SIZE = 10
HASH_STR = 'EC9C0F7EDCC18A98B1F31853B1813301'
CLIENT_DICT = {}
FLAG = False
NUM = 0
lock = Lock()


# ----------------- FUNCTIONS -----------------


def handle_connection(client_socket, client_address):
    """
    handle a connection
    :param client_socket: the connection socket
    :param client_address: the remote address
    :return: None
    """
    global NUM
    global lock
    global FLAG
    try:
        print('New connection received from ' + client_address[0] + ':' + str(client_address[1]))
        # handle the communication
        data = client_socket.recv(5).decode()
        while data == 'start':
            while not data.endswith('finish'):
                data += client_socket.recv(1).decode()
        libot = data[5:-6]
        libot = int(libot)
        print(libot)
        CLIENT_DICT[client_socket] = libot
        msg = 'start'
        msg += HASH_STR
        msg += 'finish'
        client_socket.send(msg.encode())
        if not FLAG:
            lock.acquire()
            msg = 'start'
            msg += str(NUM)
            msg += 'finish'
            NUM += 10000000 * libot
            lock.release()
            client_socket.send(msg.encode())
            data = client_socket.recv(5).decode()
            while data == 'start':
                while not data.endswith('finish'):
                    data += client_socket.recv(1).decode()
            if 'found' in data:
                for i in CLIENT_DICT.keys():
                    try:
                        i.send('startdonefinish'.encode())
                    except socket.error:
                        pass
                FLAG = True
                print(data[10:-6])
    except socket.error as err:
        print('received socket exception - ' + str(err))
    finally:
        client_socket.close()


def main():
    """
    main loop- waiting for clients to connect
    :return: None
    """
    global FLAG
    # Open a socket and loop forever while waiting for clients
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_socket.bind((IP, PORT))
        server_socket.listen(QUEUE_SIZE)
        print("Listening for connections on port %d" % PORT)

        while not FLAG:
            client_socket, client_address = server_socket.accept()
            thread = Thread(target=handle_connection,
                            args=(client_socket, client_address))
            thread.start()

    except socket.error as err:
        print('received socket exception - ' + str(err))
    finally:
        server_socket.close()


if __name__ == "__main__":
    # Call the main handler function
    main()
