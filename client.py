"""
author: Yuval Bahar
date: 27/10/2022
description: hashes strings from "0000000000" to
"9999999999" and compares to the received string
from the server
"""
#  ----------------- IMPORTS -----------------


import socket
import hashlib
from threading import Thread
import os


# ----------------- CONSTANTS - ----------------


SERVER_IP = '127.0.0.1'
SERVER_PORT = 8080
LIBOT = os.cpu_count()
FLAG = [False, None]


# ----------------- FUNCTIONS - ----------------


def hash_func(num, hash_str):
    """
    change the flag if string like the hash string was found in the range of numbers
    :param num: the number to start with in the checking
    :param hash_str: the string from the server to compare
    :return: None
    """
    global FLAG
    num = int(num)
    for i in range(num, num + 10000000):
        if FLAG[0]:
            break
        x = str(i)
        result = hashlib.md5(x.encode()).hexdigest()
        if result == hash_str:
            FLAG = [True, i]
            print(i)


def main():
    """
    connection with the server
    :return: None
    """
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((SERVER_IP, SERVER_PORT))
        while FLAG[0] is False:
            msg = 'start' + str(LIBOT) + 'finish'
            client_socket.send(msg.encode())
            print('sent')
            data = client_socket.recv(5).decode()
            hash_str = ''
            while data == 'start':
                while not data.endswith('finish'):
                    data += client_socket.recv(1).decode()
                hash_str = data[5:-6]
            print(hash_str)
            num = 0
            data = client_socket.recv(5).decode()
            print(data)
            while data == 'start':
                while not data.endswith('finish'):
                    data += client_socket.recv(1).decode()
                data = data[5:-6]
                if data != 'done':
                    num = int(data)
                else:
                    client_socket.close()
                all_threads = []
                for i in range(0, LIBOT):
                    thread = Thread(target=hash_func, args=(num, hash_str))
                    all_threads.append(thread)
                    thread.start()
                    num += 10000000
                for i in all_threads:
                    i.join()
                if True in FLAG:
                    msg = 'startfound' + str(FLAG[1]) + 'finish'
                    print('sent')
                    client_socket.send(msg.encode())
                else:
                    msg = 'startnotfinish'
                    client_socket.send(msg.encode())
                    client_socket.close()
                    main()
    except socket.error as msg:
        print('error in communication with server - ' + str(msg))
    finally:
        client_socket.close()


if __name__ == '__main__':
    main()
