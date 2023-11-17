import os
import time
import socket
import random
import select
import logging

logging.basicConfig(level=logging.INFO)

def touch(path):
    with open(path, 'a'):
        os.utime(path, None)

def run_client():
    logging.info("Client started.")

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 2222))
    while True:
        try:
            requete = random.randint(1, 2)
            if requete == 1:
                requete_type = "requetetype1"
            else:
                requete_type = "requetetype2"

            client_socket.sendall(requete_type.encode())
            logging.info(f"Etape 1 : Client sent request: {requete_type}")

            port_data = client_socket.recv(1024)
            secondary_port = int(port_data.decode())
            logging.info(f"Etape 4 : Client received secondary port: {secondary_port}")

            secondary_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            secondary_socket.connect(('localhost', secondary_port))
            logging.info("Etape 5 : Client connected to secondary server.")

            if requete_type == "requetetype1" :
                secondary_socket.sendall(b"Hello, secondary server!")
            else : 
                secondary_socket.sendall(b"Salut, serveur secondaire!")
            data = secondary_socket.recv(1024)
            logging.info(f"Etape 6 : Client received from secondary server: {data.decode()}")

        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")

        finally:
            secondary_socket.close()

        user_input = input("Voulez-vous envoyer une autre requête ? (Oui/Non): ")
        if user_input.lower() != "oui" and user_input.lower() != "o":
            break

    client_socket.close()

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
            
            # Faire un message via le pipe au serveur secondaire pour savoir s'il peut répondre à la requête
            with open('dwtube1', 'w') as fifo_out : 
                os.write(b'Can you handle the file ?')
                
            
            # Lire le message reçu par le serveur secondaire pour renvoyer l'information au client
            
            conn.sendall(b"2223")
        except ConnectionResetError:
            logging.debug("Client disconnected unexpectedly.")
            break
    
    conn.close()

def run_worker():
    logging.info("Worker started.")
    
    touch('shared_memory.txt')
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
    
    while True:
        try:
            stop_msg = os.read(stop_fifo_in, 4).decode()
            if stop_msg == 'stop':
                logging.info("Worker received stop signal. Exiting.")
                break
        except BlockingIOError:
            pass
        
        # Lire un message dans le pipe, si un message de demande de traitement de requête est présent, il écrit dans l'autre pipe 
        with open('dwtube1', os.O_RDONLY) as fifo_out :
            msg = os.read(fifo_out, 4).decode()
        logging.info(f"Etape 2 : Worker received from Dispatcher: {msg}")

        ready, _, _ = select.select([worker_socket], [], [], 1)
        if ready:
            conn, addr = worker_socket.accept()
            logging.info(f"Etape 5 : Worker connected to client at {addr}")
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                logging.info(f"Etape 5 : Worker received: {data.decode()}")
                
                conn.sendall(b"Hello, client!")
    
    worker_socket.close()
    conn.close()

def run_watchdog():
    logging.info("Watchdog started.")
    
    if not os.path.exists('dwtube1'):
        os.mkfifo('dwtube1')
    if not os.path.exists('wdtube1'):
        os.mkfifo('wdtube1')

    if not os.path.exists('stop_tube'):
        os.mkfifo('stop_tube')
    
    pid = os.fork()
    if pid < 0:
        logging.info("fork() impossible")
        os.abort()
    elif pid == 0:
        run_dispatcher()
        os._exit(0)
    else:
        worker_pid = os.fork()
        if worker_pid < 0:
            logging.info("fork() impossible")
            os.abort()
        elif worker_pid == 0:
            run_worker()
            os._exit(0)
        else:
            time.sleep(30)
            with open('stop_tube', 'w') as stop_fifo:
                stop_fifo.write('stop')
                logging.info("Watchdog: Checking process health.")
        
                if os.path.exists('dwtube1'):
                    os.remove('dwtube1')
                if os.path.exists('wdtube1'):
                    os.remove('wdtube1')
                if os.path.exists('shared_memory.txt'):
                    os.remove('shared_memory.txt')

if __name__ == '__main__':
    print("1: Run Watchdog (and servers)")
    print("2: Run Client")
    choice = input("Choose an option: ")
    
    if choice == '1':
        run_watchdog()
    elif choice == '2':
        run_client()
    else:
        logging.debug("Invalid option.")
