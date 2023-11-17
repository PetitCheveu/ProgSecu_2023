import time
import socket
import select
import logging

import mmap
import os

def run_dispatcher():
    logging.info("Dispatcher started.")

    shared_memory_file = '/tmp/shared_memory'
    SHARED_MEMORY_SIZE = 1024

    if not os.path.exists('/tmp'):
        os.makedirs('/tmp')

    with open(shared_memory_file, 'wb') as f:
        f.truncate(SHARED_MEMORY_SIZE)

    with open(shared_memory_file, 'r+b') as f:
        shared_memory = mmap.mmap(f.fileno(), SHARED_MEMORY_SIZE)

    try : 
        watchdog_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        watchdog_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        watchdog_socket.bind(('localhost', 2224))
        watchdog_socket.listen(1)
        logging.info("Watchdog socket created and listening.")
        connexion_watchdog, addresse = watchdog_socket.accept()
        logging.info(f"Dispatcher connected to watchdog at {addresse}")
    except Exception as e :
        logging.error(f"An error occurred during during the creation of the socket between the dispatcher and the watchdog: {e}")

    while True:
        try : 
            data = connexion_watchdog.recv(1024)
            if not data:
                break
            watchdog_question = data.decode()
            logging.info(f'Dispatcher received: {watchdog_question}')
            if watchdog_question == "Still running ?" : 
                connexion_watchdog.sendall(b"Yes")
            elif watchdog_question == "Tu fonctionnes toujours ?" : 
                connexion_watchdog.sendall(b"Oui")
            else : 
                connexion_watchdog.sendall(b"No")
        except Exception as e : 
            logging.error(f"An error occurred: {e}")
        try:
            # Checking that the connexion is possible and that the port is correctly closed
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind(('localhost', 2222))
            server_socket.listen(1)
        except OSError as e:
            logging.warning(f"Port 2222 is already in use. Closing the previous socket and retrying.\n\n{e}")
            logging.info("Dispatcher process terminated.")
            break
            
        conn, addr = None, None
        start_time = time.time()  # Définir le temps de départ
        while conn is None and (time.time() - start_time) < 1:  # Attendre jusqu'à 4 secondes
            ready_sockets, _, _ = select.select([server_socket], [], [], 4.0)
            if ready_sockets:
                conn, addr = server_socket.accept()
                break  # Sortir de la boucle si une connexion est établie
            else:
                logging.info("Waiting for client request...")

        # if conn is None:
        #     logging.info("No client, still waiting")
        #     continue
        if conn is None:
            logging.info("No client, still waiting")

            # Send a ping to the worker
            with open('dwtube1', 'w') as fifo_out: 
                fifo_out.write('ping')

            # Wait for a response from the worker
            start_time = time.time()
            timeout = 1  # Wait for 1 second for worker response
            while (time.time() - start_time) < timeout:
                with open('wdtube1', 'r') as fifo_in:
                    response = fifo_in.read().strip()
                    if response:
                        if response == "Worker is not answering":
                            logging.info("Worker is not answering. Notifying the watchdog.")
                            connexion_watchdog.sendall(b"Worker is not answering")
                        else:
                            logging.info(f"Worker response: {response}")
                        break
                time.sleep(0.1)
        if conn is not None:
            logging.debug(f"Etape 1 : Dispatcher connected to client at {addr}")
            try:
                data = conn.recv(1024)
                if not data:
                    break
                request_from_client = data.decode()
                logging.debug(f"Etape 1 : Dispatcher received: {request_from_client}")

                shared_memory.seek(0)
                shared_memory.write(b'\x00' * SHARED_MEMORY_SIZE)
                shared_memory.seek(0)
                shared_memory.write(b"Are you free for a connexion ?\x00")
                
                with open('dwtube1', 'w') as fifo_out: 
                    fifo_out.write('ping')
                with open('wdtube1', 'r') as fifo_in:
                    logging.debug(f"Dispatcher received from Worker: {fifo_in.read().strip()}")
                
                shared_memory.seek(0)
                answer = shared_memory.read(SHARED_MEMORY_SIZE).decode().strip('\x00')

                
                if answer == "Yes" : 
                    logging.debug(f"Etape 3 : Worker is free to work")
                    conn.sendall(b"2223")
                    try:
                        conn.close()
                        server_socket.close()
                    except Exception as e:
                        logging.debug(e)
                    

                    shared_memory.seek(0)
                    shared_memory.write(b'\x00' * SHARED_MEMORY_SIZE)                   
                    shared_memory.seek(0)
                    shared_memory.write(b"Are you done ?\x00")
                
                    with open('dwtube1', 'w') as fifo_out: 
                        fifo_out.write('ping')
                        
                    with open('wdtube1', 'r') as fifo_in:
                        logging.info(f"Dispatcher received from Worker: {fifo_in.read().strip()}")
                    
                    shared_memory.seek(0)
                    is_worker_done = shared_memory.read(SHARED_MEMORY_SIZE).decode().strip('\x00')
                    
                    logging.info(f"Dispatcher read: {is_worker_done}")
                    if is_worker_done == "Yes":
                        logging.info(f"Etape 7 : Worker is finished with his job and told the dispatcher")
                        
                if answer == "No" :
                    logging.info(f"Etape 3 : Worker is too busy to work")
                    conn.sendall(b"-1")
                    try:
                        conn.close()
                        server_socket.close()
                    except Exception as e:
                        logging.debug(e)
            
            except ConnectionResetError:
                logging.debug("Client disconnected unexpectedly.")
                break
    try : 
        conn.close()
        server_socket.close()
    except Exception as e : 
        logging.debug(e)