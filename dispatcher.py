import time
import socket
import select
import logging

def run_dispatcher():
    logging.info("Dispatcher started.")
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
            logging.warning(f"Port 2222 is already in use. Closing the previous socket and retrying.")
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
            logging.info(f"Etape 1 : Dispatcher connected to client at {addr}")
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
                    try:
                        conn.close()
                        server_socket.close()
                    except Exception as e:
                        logging.debug(e)
                    
                    
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