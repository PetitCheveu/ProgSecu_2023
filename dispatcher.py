import os
import time
import socket
import json
import random
import select
import logging

def run_dispatcher():
    logging.info("Dispatcher started.")
    
    with open('shared_memory.txt', 'w') as f:
        f.write("ping")
    
    fifo_out = os.open('dwtube1', os.O_WRONLY)
    
    for _ in range(3):
        os.write(fifo_out, b'ping')
        with open('wdtube1', 'r') as fifo_in:
            logging.info(f"Dispatcher received: {fifo_in.read().strip()}")
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('localhost', 2222))
    server_socket.listen(1)
    
    conn, addr = server_socket.accept()
    server_socket.close()
    logging.info(f"Etape 1 : Dispatcher connected to client at {addr}")
    
    while True:
        try:
            data = conn.recv(1024)
            if not data:
                break
            logging.info(f"Etape 1 : Dispatcher received: {data.decode()}")
            conn.sendall(b"2223")
        except ConnectionResetError:
            logging.debug("Client disconnected unexpectedly.")
            break
    
    conn.close()