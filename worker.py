import socket
import select
import logging
import mmap

import datetime

def run_worker():
    logging.info("Worker started.")

    shared_memory_file = '/tmp/shared_memory'
    SHARED_MEMORY_SIZE = 1024

    with open(shared_memory_file, 'rb+') as f:
        f.seek(SHARED_MEMORY_SIZE - 1)
        f.write(b'\x00')
        f.flush()

    with open(shared_memory_file, 'r+b') as f:
        shared_memory = mmap.mmap(f.fileno(), SHARED_MEMORY_SIZE)
    
    conn = None
    connected = False
    
    while True:
        with open('dwtube1', 'r') as fifo_out:
            logging.info(f"Worker received from Dispatcher: {fifo_out.read().strip()}")

        shared_memory.seek(0)
        question = shared_memory.read(SHARED_MEMORY_SIZE).decode().strip('\x00')

        if question == "Are you free for a connexion ?" :
            logging.debug(f"Etape 2 : Worker is asked for disponibility")
        
            if connected == False :
                shared_memory.seek(0)
                shared_memory.write(b'\x00' * SHARED_MEMORY_SIZE)
                
                shared_memory.seek(0)
                shared_memory.write(b"Yes\x00")

                shared_memory.seek(0)
                writen = shared_memory.read(SHARED_MEMORY_SIZE).decode().strip('\x00')
                logging.debug(f"Writen memory {writen}")

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
                    logging.debug(f"Etape 5 : Worker connected to client at {addr}")
                    connected = True
                    while True:
                        data = conn.recv(1024)
                        request = data.decode()
                        if not data:
                            break
                        logging.debug(f"Etape 5 : Worker received: {request}")
                        
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
                shared_memory.seek(0)
                shared_memory.write(b'\x00' * SHARED_MEMORY_SIZE)
                shared_memory.seek(0)
                shared_memory.write(b"No\x00")

                with open('wdtube1', 'w') as fifo_in:
                    fifo_in.write('pong')
                    
        elif question == "Are you done ?":
            if connected == False : 
                logging.info(f"Worker read: {question}")
                shared_memory.seek(0)
                shared_memory.write(b'\x00' * SHARED_MEMORY_SIZE)
                shared_memory.seek(0)
                shared_memory.write(b"Yes\x00")

                with open('wdtube1', 'w') as fifo_in:
                    fifo_in.write('pong')
        elif question == "":
            with open('wdtube1', 'w') as fifo_in:
                fifo_in.write('pong')

    
        