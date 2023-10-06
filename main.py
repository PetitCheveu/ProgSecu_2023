import os
import time
import socket
import json
import random
import select
import logging

logging.basicConfig(level=logging.INFO)

# def run_client():
#     print("Client started.")
    
#     # Se connecter au serveur principal sur le port 2222
#     client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     client_socket.connect(('localhost', 2222))
    
#     # Envoyer une requête de type
#     requete = random.randint(1, 2)
    
#     if requete == 1 :
#         client_socket.sendall(b"requetetype1")
#     elif requete == 2 : 
#         client_socket.sendall(b"requetetype2")
    
#     # Recevoir un numéro de port pour le serveur secondaire
#     port_data = client_socket.recv(1024)
#     secondary_port = int(port_data.decode())
    
#     # Se connecter au serveur secondaire
#     secondary_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     secondary_socket.connect(('localhost', secondary_port))
    
#     # Échanger des informations
#     secondary_socket.sendall(b"Hello, secondary server!")
#     data = secondary_socket.recv(1024)
#     print(f"Client received from secondary server: {data.decode()}")
    
#     # Fermer les connexions
#     secondary_socket.close()
#     client_socket.close()

def touch(path):
    with open(path, 'a'):
        os.utime(path, None)

def run_client():
    logging.info("Client started.")

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 2222))
    while True:
        # Se connecter au serveur principal sur le port 2222
        try:
            # Envoyer une requête de type
            requete = random.randint(1, 2)
            if requete == 1:
                requete_type = "requetetype1"
            else:
                requete_type = "requetetype2"

            client_socket.sendall(requete_type.encode())

            # Recevoir un numéro de port pour le serveur secondaire
            port_data = client_socket.recv(1024)
            secondary_port = int(port_data.decode())

            # Se connecter au serveur secondaire
            secondary_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            secondary_socket.connect(('localhost', secondary_port))

            # Échanger des informations
            secondary_socket.sendall(b"Hello, secondary server!")
            data = secondary_socket.recv(1024)
            logging.info(f"Client received from secondary server: {data.decode()}")

        except Exception as e:
            logging.info(f"An error occurred: {str(e)}")

        finally:
            # Fermer la connexion au serveur secondaire
            secondary_socket.close()

        # Demander à l'utilisateur s'il souhaite envoyer une autre requête
        user_input = input("Voulez-vous envoyer une autre requête ? (Oui/Non): ")
        if user_input.lower() != "oui" and user_input.lower() != "o":
            break

    # Fermer la connexion au serveur principal
    client_socket.close()

# Fonctions pour le dispatcher (serveur principal)
def run_dispatcher():
    logging.info("Dispatcher started.")
    
    # Utiliser un fichier comme mémoire partagée
    with open('shared_memory.txt', 'w') as f:
        f.write("ping")
    
    # Tube nommé pour la synchronisation
    fifo_out = os.open('dwtube1', os.O_WRONLY)
    
    for _ in range(3):
        os.write(fifo_out, b'ping')
        with open('wdtube1', 'r') as fifo_in:
            logging.info(f"Dispatcher received: {fifo_in.read().strip()}")
    
    # Créer un socket pour accepter les connexions du client
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Réutiliser le port
    server_socket.bind(('localhost', 2222))
    server_socket.listen(1)
    
    conn, addr = server_socket.accept()
    server_socket.close()
    logging.info(f"Dispatcher connected to client at {addr}")
    
    while True:
        try:
            data = conn.recv(1024)
            if not data:
                break
            logging.info(f"Dispatcher received: {data.decode()}")
            conn.sendall(b"2223")
        except ConnectionResetError:
            logging.info("Client disconnected unexpectedly.")
            break
    
    server_socket.close()
    conn.close()

# Fonctions pour le worker (serveur secondaire)
def run_worker():
    logging.info("Worker started.")
    
    # Lire depuis la mémoire partagée
    touch('shared_memory.txt')
    with open('shared_memory.txt', 'r') as f:
        logging.info(f"Worker received from Shared Memory: {f.read().strip()}")
    
    fifo_in = os.open('dwtube1', os.O_RDONLY)

    # Ouvrir le tube nommé pour la lecture
    stop_fifo_in = os.open('stop_tube', os.O_RDONLY | os.O_NONBLOCK)
    
    for _ in range(3):
        msg = os.read(fifo_in, 4).decode()
        logging.info(f"Worker received from Dispatcher: {msg}")
        with open('wdtube1', 'w') as fifo_out:
            fifo_out.write("pong")
    
    os.close(fifo_in)

    # Créer un socket pour accepter les connexions du client
    worker_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    worker_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Réutiliser le port
    worker_socket.setblocking(0)  # Set the socket to non-blocking
    worker_socket.bind(('localhost', 2223))
    worker_socket.listen(1)
    
    while True:
        # Vérifier si 'stop' a été écrit dans le tube
        try:
            stop_msg = os.read(stop_fifo_in, 4).decode()
            if stop_msg == 'stop':
                logging.info("Worker received stop signal. Exiting.")
                break
        except BlockingIOError:
            pass

        ready, _, _ = select.select([worker_socket], [], [], 1)
        if ready:
            conn, addr = worker_socket.accept()
            logging.info(f"Worker connected to client at {addr}")
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                logging.info(f"Worker received: {data.decode()}")
                
                # Envoyer des données de réponse au client
                conn.sendall(b"Hello, client!")
    
    worker_socket.close()
    conn.close()

# Fonctions pour le watchdog
def run_watchdog():
    logging.info("Watchdog started.")
    
    # Créer des tubes nommés
    if not os.path.exists('dwtube1'):
        os.mkfifo('dwtube1')
    if not os.path.exists('wdtube1'):
        os.mkfifo('wdtube1')

    # Créer un autre tube nommé pour stopper le worker
    if not os.path.exists('stop_tube'):
        os.mkfifo('stop_tube')
    
    # Lancer le dispatcher
    pid = os.fork()
    if pid < 0:
        logging.info("fork() impossible")
        os.abort()
    elif pid == 0:
        run_dispatcher()
        os._exit(0)
    else:
        # Lancer le worker
        worker_pid = os.fork()
        if worker_pid < 0:
            logging.info("fork() impossible")
            os.abort()
        elif worker_pid == 0:
            run_worker()
            os._exit(0)

        else:
            # Watchdog observe les processus (ici, il attend simplement)
            time.sleep(30)
            with open('stop_tube', 'w') as stop_fifo:
                stop_fifo.write('stop')
                logging.info("Watchdog: Checking process health.")
        
                # Nettoyage : supprimer les tubes nommés et la mémoire partagée
                if os.path.exists('dwtube1'):
                    os.remove('dwtube1')
                if os.path.exists('wdtube1'):
                    os.remove('wdtube1')
                if os.path.exists('shared_memory.txt'):
                    os.remove('shared_memory.txt')

if __name__ == '__main__':
    print("1: Run Watchdog (and servers)")
    ("2: Run Client")
    choice = input("Choose an option: ")
    
    if choice == '1':
        run_watchdog()
    elif choice == '2':
        run_client()
    else:
        logging.debug("Invalid option.")