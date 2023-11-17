"""
Dispatcher Module

This module defines a Dispatcher that communicates with a Watchdog, listens for client requests, and coordinates with a Worker.

The Dispatcher manages communication with the Watchdog and Worker to handle client requests, check the Worker's availability, and signal the Worker to start or finish its tasks.

Author: Elena BEYLAT & Robin JOSEPH
"""

import time
import socket
import select
import logging

import mmap
import os

def run_dispatcher():
    """
    Run the Dispatcher process.

    This function initializes the Dispatcher, communicates with the Watchdog, listens for client requests, and coordinates with the Worker.

    """
    # Log the start of the Dispatcher process
    logging.info("Dispatcher started.")

    # Shared memory configuration
    shared_memory_file = '/tmp/shared_memory'
    SHARED_MEMORY_SIZE = 1024

    # Ensure the '/tmp' directory exists
    if not os.path.exists('/tmp'):
        os.makedirs('/tmp')

    # Create and truncate the shared memory file
    with open(shared_memory_file, 'wb') as f:
        f.truncate(SHARED_MEMORY_SIZE)

    # Initialize shared memory
    with open(shared_memory_file, 'r+b') as f:
        shared_memory = mmap.mmap(f.fileno(), SHARED_MEMORY_SIZE)

    try : 
        # Set up the socket connection with the Watchdog
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
            # Receive data from the Watchdog
            data = connexion_watchdog.recv(1024)
            if not data:
                break
            watchdog_question = data.decode()
            logging.info(f'Dispatcher received: {watchdog_question}')
            
            # Respond to the Watchdog based on the received question
            if watchdog_question == "Still running ?" : 
                connexion_watchdog.sendall(b"Yes")
            elif watchdog_question == "Tu fonctionnes toujours ?" : 
                connexion_watchdog.sendall(b"Oui")
            else : 
                connexion_watchdog.sendall(b"No")
        except Exception as e : 
            logging.error(f"An error occurred: {e}")
        try:
            # Set up the server socket to listen for client requests
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind(('localhost', 2222))
            server_socket.listen(1)
        except OSError as e:
            # Handle the case where port 2222 is already in use
            logging.warning(f"Port 2222 is already in use. Closing the previous socket and retrying.\n\n{e}")
            logging.info("Dispatcher process terminated.")
            break
            
        conn, addr = None, None
        start_time = time.time()  # Set the start time
        while conn is None and (time.time() - start_time) < 1:  # Wait for up to 1 second
            ready_sockets, _, _ = select.select([server_socket], [], [], 4.0)
            if ready_sockets:
                conn, addr = server_socket.accept()
                break  # Exit the loop if a connection is established
            else:
                logging.info("Waiting for client request...")

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
                # Receive data from the client
                data = conn.recv(1024)
                if not data:
                    break
                request_from_client = data.decode()
                logging.debug(f"Etape 1 : Dispatcher received: {request_from_client}")

                # Set shared memory to indicate that the worker is needed
                shared_memory.seek(0)
                shared_memory.write(b'\x00' * SHARED_MEMORY_SIZE)
                shared_memory.seek(0)
                shared_memory.write(b"Are you free for a connexion ?\x00")
                
                # Notify the worker via named pipe
                with open('dwtube1', 'w') as fifo_out: 
                    fifo_out.write('ping')
                    
                # Receive response from the worker via named pipe
                with open('wdtube1', 'r') as fifo_in:
                    logging.debug(f"Dispatcher received from Worker: {fifo_in.read().strip()}")
                
                # Read the worker's answer from shared memory
                shared_memory.seek(0)
                answer = shared_memory.read(SHARED_MEMORY_SIZE).decode().strip('\x00')

                
                if answer == "Yes" : 
                    logging.debug(f"Etape 3 : Worker is free to work")
                    # Send the worker's listening port to the client
                    conn.sendall(b"2223")
                    
                    # Close the client connection and server socket
                    try:
                        conn.close()
                        server_socket.close()
                    except Exception as e:
                        logging.debug(e)
                    

                    # Set shared memory to indicate that the worker's task is done
                    shared_memory.seek(0)
                    shared_memory.write(b'\x00' * SHARED_MEMORY_SIZE)                   
                    shared_memory.seek(0)
                    shared_memory.write(b"Are you done ?\x00")
                
                    # Notify the worker via named pipe
                    with open('dwtube1', 'w') as fifo_out: 
                        fifo_out.write('ping')
                        
                    # Receive response from the worker via named pipe
                    with open('wdtube1', 'r') as fifo_in:
                        logging.info(f"Dispatcher received from Worker: {fifo_in.read().strip()}")
                    
                    # Read the worker's completion status from shared memory
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