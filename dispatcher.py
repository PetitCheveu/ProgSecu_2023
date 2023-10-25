import os
import time
import socket
import json
import random
import select
import logging

def run_dispatcher():
    logging.info("Dispatcher started.")
    
    # with open('shared_memory.txt', 'w') as f:
    #     f.write("ping")
    
    # fifo_out = os.open('dwtube1', os.O_WRONLY)
    
    # for _ in range(3):
    #     os.write(fifo_out, b'ping')
    #     with open('wdtube1', 'r') as fifo_in:
    #         logging.info(f"Dispatcher received from Worker: {fifo_in.read().strip()}")
    
    # os.close(fifo_out)
    
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
            request_from_client = data.decode()
            logging.info(f"Etape 1 : Dispatcher received: {request_from_client}")
                            
            with open('shared_memory.txt', 'w') as f :
                f.write("Are you free for a connexion ?")
            
            with open('dwtube1', 'w') as fifo_out: 
                fifo_out.write('ping')
            with open('wdtube1', 'r') as fifo_in:
                logging.info(f"Dispatcher received from Worker: {fifo_in.read().strip()}")
            with open('shared_memory.txt', 'r') as f: 
                answer = f.read()
            
            if answer == "Yes" : 
                logging.info(f"Etape 3 : Worker is free to work")
                conn.sendall(b"2223")
                
                
                with open('shared_memory.txt', 'w') as f :
                    f.write("Are you done ?")
            
                with open('dwtube1', 'w') as fifo_out: 
                    fifo_out.write('ping')
                    
                with open('wdtube1', 'r') as fifo_in:
                    logging.info(f"Dispatcher received from Worker: {fifo_in.read().strip()}")
                
                with open('shared_memory.txt', 'r') as f: 
                    is_worker_done = f.read()
                
                logging.info(f"Dispatcher read: {is_worker_done}")
                if is_worker_done == "Yes":
                    logging.info(f"Etape 7 : Worker is finished with is job and told the dispatcher")
                    
            if answer == "No" :
                logging.info(f"Etape 3 : Worker is too busy to work")
                conn.sendall(b"-1")
            
        except ConnectionResetError:
            logging.debug("Client disconnected unexpectedly.")
            break
    conn.close()