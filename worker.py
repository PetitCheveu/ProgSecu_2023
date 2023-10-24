import os
import time
import socket
import json
import random
import select
import logging

import utils

def run_worker():
    logging.info("Worker started.")
    
    utils.touch('shared_memory.txt')
    with open('shared_memory.txt', 'r') as f:
        logging.info(f"Worker received from Shared Memory: {f.read().strip()}")
    
    fifo_in = os.open('dwtube1', os.O_RDONLY)
    stop_fifo_in = os.open('stop_tube', os.O_RDONLY | os.O_NONBLOCK)
    
    for _ in range(3):
        msg = os.read(fifo_in, 4).decode()
        logging.info(f"Worker received from Dispatcher: {msg}")
        with open('wdtube1', 'w') as fifo_out:
            fifo_out.write("pong")
    
    os.close(fifo_in)

    worker_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    worker_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    worker_socket.setblocking(0)
    worker_socket.bind(('localhost', 2223))
    worker_socket.listen(1)
    
    conn = None
    connected = False
    
    while True:
        try:
            stop_msg = os.read(stop_fifo_in, 4).decode()
            if stop_msg == 'stop':
                logging.info("Worker received stop signal. Exiting.")
                break
        except BlockingIOError:
            pass

        with open('dwtube1', 'r') as fifo_out:
            logging.info(f"Worker received from Dispatcher: {fifo_out.read().strip()}")

        with open('shared_memory.txt', 'r') as f :
            question = f.read()
        if question == "Are you free for a connexion ?" :
            logging.info(f"Etape 2 : Worker is asked for disponibility")
        
            if connected == False : 
                with open('shared_memory.txt', 'w') as f :
                    f.write("Yes")
                with open('wdtube1', 'w') as fifo_in:
                    fifo_in.write('pong')     
                
                ready, _, _ = select.select([worker_socket], [], [], 1)
                if ready:
                    conn, addr = worker_socket.accept()
                    logging.info(f"Etape 5 : Worker connected to client at {addr}")
                    connected = True
                    while True:
                        data = conn.recv(1024)
                        if not data:
                            break
                        logging.info(f"Etape 5 : Worker received: {data.decode()}")
                        
                        conn.sendall(b"Hello, client!")
                        connected = False
            else : 
                with open('shared_memory.txt', 'w') as f :
                    f.write("No")
                with open('wdtube1', 'w') as fifo_in:
                    fifo_in.write('pong')
    
    worker_socket.close()
    if conn is not None : 
        conn.close()
