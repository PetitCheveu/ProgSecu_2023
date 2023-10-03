import os
import time
import socket
import json

def run_client():
    print("Client started.")
    
    # Se connecter au serveur principal sur le port 2222
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 2222))
    
    # Envoyer une requête de type
    client_socket.sendall(b"requetetype1")
    
    # Recevoir un numéro de port pour le serveur secondaire
    port_data = client_socket.recv(1024)
    secondary_port = int(port_data.decode())
    
    # Se connecter au serveur secondaire
    secondary_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    secondary_socket.connect(('localhost', secondary_port))
    
    # Échanger des informations
    secondary_socket.sendall(b"Hello, secondary server!")
    data = secondary_socket.recv(1024)
    print(f"Client received from secondary server: {data.decode()}")
    
    # Fermer les connexions
    secondary_socket.close()
    client_socket.close()

# Fonctions pour le dispatcher (serveur principal)
def run_dispatcher():
    print("Dispatcher started.")
    
    # Utiliser un fichier comme mémoire partagée
    with open('shared_memory.txt', 'w') as f:
        f.write("ping")
    
    # Tube nommé pour la synchronisation
    fifo_out = os.open('dwtube1', os.O_WRONLY)
    
    for _ in range(3):
        os.write(fifo_out, b'ping')
        with open('wdtube1', 'r') as fifo_in:
            print(f"Dispatcher received: {fifo_in.read().strip()}")
    
    # Créer un socket pour accepter les connexions du client
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 2222))
    server_socket.listen(1)
    
    conn, addr = server_socket.accept()
    print(f"Dispatcher connected to client at {addr}")
    
    while True:
        data = conn.recv(1024)
        if not data:
            break
        print(f"Dispatcher received: {data.decode()}")
        
        # Envoyer le numéro de port du serveur secondaire au client
        conn.sendall(b"2223")
    
    conn.close()

# Fonctions pour le worker (serveur secondaire)
def run_worker():
    print("Worker started.")
    
    # Lire depuis la mémoire partagée
    with open('shared_memory.txt', 'r') as f:
        print(f"Worker received from Shared Memory: {f.read().strip()}")
    
    fifo_in = os.open('dwtube1', os.O_RDONLY)
    
    for _ in range(3):
        msg = os.read(fifo_in, 4).decode()
        print(f"Worker received from Dispatcher: {msg}")
        with open('wdtube1', 'w') as fifo_out:
            fifo_out.write("pong")
    
    os.close(fifo_in)

    # Créer un socket pour accepter les connexions du client
    worker_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    worker_socket.bind(('localhost', 2223))
    worker_socket.listen(1)
    
    conn, addr = worker_socket.accept()
    print(f"Worker connected to client at {addr}")
    
    while True:
        data = conn.recv(1024)
        if not data:
            break
        print(f"Worker received: {data.decode()}")
        
        # Envoyer des données de réponse au client
        conn.sendall(b"Hello, client!")
    
    conn.close()

# Fonctions pour le watchdog
def run_watchdog():
    print("Watchdog started.")
    
    # Créer des tubes nommés
    if not os.path.exists('dwtube1'):
        os.mkfifo('dwtube1')
    if not os.path.exists('wdtube1'):
        os.mkfifo('wdtube1')
    
    # Lancer le dispatcher
    pid = os.fork()
    if pid < 0:
        print("fork() impossible")
        os.abort()
    elif pid == 0:
        run_dispatcher()
        os._exit(0)
    else:
        # Lancer le worker
        worker_pid = os.fork()
        if worker_pid < 0:
            print("fork() impossible")
            os.abort()
        elif worker_pid == 0:
            run_worker()
            os._exit(0)
        
        # Watchdog observe les processus (ici, il attend simplement)
        time.sleep(10)
        print("Watchdog: Checking process health.")
        
        # Nettoyage : supprimer les tubes nommés et la mémoire partagée
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
        print("Invalid option.")

