import socket
import select
import logging

import utils
import datetime

def run_worker():
    logging.info("Worker started.")
    
    utils.touch('shared_memory.txt')
    
    conn = None
    connected = False
    
    while True:
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
                
                worker_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                worker_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                worker_socket.setblocking(0)
                worker_socket.bind(('localhost', 2223))
                worker_socket.listen(1)
                
                ready, _, _ = select.select([worker_socket], [], [], 1)
                if ready:
    
                    conn, addr = worker_socket.accept()
                    logging.info(f"Etape 5 : Worker connected to client at {addr}")
                    connected = True
                    while True:
                        data = conn.recv(1024)
                        request = data.decode()
                        if not data:
                            break
                        logging.info(f"Etape 5 : Worker received: {request}")
                        
                        now = datetime.datetime.now()
                        message = "no response"
                        if request == "Hello, what time is it ?" : 
                            response = now.strftime("%H:%M:%S")
                            message = "Hello, client! it is " + response
                            message = message.encode('utf-8')
                        elif request == "Hello, what's the date today ?":
                            response = now.strftime("%d/%m/%Y")
                            message = "Hello, client! we are the " + response
                            message = message.encode('utf-8')
                        conn.sendall(message)
                worker_socket.close()
                if conn is not None : 
                    conn.close()
                connected = False
            else : 
                with open('shared_memory.txt', 'w') as f :
                    f.write("No")
                with open('wdtube1', 'w') as fifo_in:
                    fifo_in.write('pong')
                    
        elif question == "Are you done ?":
            if connected == False : 
                logging.info(f"Worker read: {question}")
                with open('shared_memory.txt', 'w') as f :
                    f.write("Yes")
                with open('wdtube1', 'w') as fifo_in:
                    fifo_in.write('pong')
        elif question == "":
            with open('wdtube1', 'w') as fifo_in:
                fifo_in.write('pong')

    
        