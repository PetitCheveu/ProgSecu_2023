"""
Worker Module

This module defines a Worker that interacts with a Dispatcher and communicates with a Client using sockets and shared memory.

The Worker receives requests from the Dispatcher, checks its availability, and responds to the Client with the current time or date.

Author: Elena BEYLAT & Robin JOSEPH
"""

import socket
import select
import logging
import mmap

import datetime

def run_worker():
    """
    Run the Worker process.

    This function initializes the Worker, communicates with the Dispatcher, and responds to Client requests with the current time or date.

    """
    # Log the start of the Worker process
    logging.info("Worker started.")

    # Shared memory configuration
    shared_memory_file = '/tmp/shared_memory'
    SHARED_MEMORY_SIZE = 1024

    # Initialize shared memory
    with open(shared_memory_file, 'rb+') as f:
        f.seek(SHARED_MEMORY_SIZE - 1)
        f.write(b'\x00')
        f.flush()

    with open(shared_memory_file, 'r+b') as f:
        shared_memory = mmap.mmap(f.fileno(), SHARED_MEMORY_SIZE)
    
    # Initialize socket-related variables
    conn = None
    connected = False
    
    while True:
        # Read from the Dispatcher's named pipe
        with open('dwtube1', 'r') as fifo_out:
            logging.info(f"Worker received from Dispatcher: {fifo_out.read().strip()}")

        # Read the question from shared memory
        shared_memory.seek(0)
        question = shared_memory.read(SHARED_MEMORY_SIZE).decode().strip('\x00')

        # Handle different types of questions
        if question == "Are you free for a connexion ?" :
            logging.debug(f"Etape 2 : Worker is asked for disponibility")
        
            if connected == False :
                # Set shared memory to 'Yes' and notify the Dispatcher
                shared_memory.seek(0)
                shared_memory.write(b'\x00' * SHARED_MEMORY_SIZE)
                
                shared_memory.seek(0)
                shared_memory.write(b"Yes\x00")

                shared_memory.seek(0)
                writen = shared_memory.read(SHARED_MEMORY_SIZE).decode().strip('\x00')
                logging.debug(f"Writen memory {writen}")

                # Notify the Dispatcher via named pipe
                with open('wdtube1', 'w') as fifo_in:
                    fifo_in.write('pong')     
                
                # Set up a socket to listen for connections
                worker_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                worker_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                worker_socket.setblocking(0)
                worker_socket.bind(('localhost', 2223))
                worker_socket.listen(1)
                
                # Check for incoming connection within a timeout
                ready, _, _ = select.select([worker_socket], [], [], 1)
                if ready:
                    conn, addr = worker_socket.accept()
                    logging.debug(f"Etape 5 : Worker connected to client at {addr}")
                    connected = True
                    
                    # Handle data received from the Client
                    while True:
                        data = conn.recv(1024)
                        request = data.decode()
                        if not data:
                            break
                        logging.debug(f"Etape 5 : Worker received: {request}")
                        
                        # Generate a response based on the request
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
                
                # Close the worker socket and the connection
                worker_socket.close()
                if conn is not None : 
                    conn.close()
                connected = False
            else :
                # Set shared memory to 'No' and notify the Dispatcher
                shared_memory.seek(0)
                shared_memory.write(b'\x00' * SHARED_MEMORY_SIZE)
                shared_memory.seek(0)
                shared_memory.write(b"No\x00")

                with open('wdtube1', 'w') as fifo_in:
                    fifo_in.write('pong')
                    
        elif question == "Are you done ?":
            if connected == False : 
                logging.info(f"Worker read: {question}")
                
                # Set shared memory to 'Yes' and notify the Dispatcher
                shared_memory.seek(0)
                shared_memory.write(b'\x00' * SHARED_MEMORY_SIZE)
                shared_memory.seek(0)
                shared_memory.write(b"Yes\x00")

                # Notify the Dispatcher via named pipe
                with open('wdtube1', 'w') as fifo_in:
                    fifo_in.write('pong')
        elif question == "":
            # Notify the Dispatcher via named pipe
            with open('wdtube1', 'w') as fifo_in:
                fifo_in.write('pong')

    
        