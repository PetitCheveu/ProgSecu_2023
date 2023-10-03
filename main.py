from multiprocessing import shared_memory, Process, Pipe
import os
import time
import signal

# Gestionnaire de signaux pour le watchdog
def signal_handler(signum, frame):
    global received_signal
    if signum == signal.SIGUSR1:
        print(f"Watchdog received signal SIGUSR1. Sending back SIGUSR2.")
        os.kill(os.getppid(), signal.SIGUSR2)
    elif signum == signal.SIGUSR2:
        print(f"Watchdog received signal SIGUSR2.")
        received_signal = True

# Worker (Serveur secondaire)
def worker(shm_name, conn):
    try:
        existing_shm = shared_memory.SharedMemory(name=shm_name)
        buffer = existing_shm.buf
        print(f"Worker received from SHM: {buffer[:4].tobytes().decode('utf-8')}")

        for _ in range(3):
            msg = conn.recv()
            print(f"Worker received from Pipe: {msg}. Sending back 'pong'.")
            conn.send("pong")

        existing_shm.close()
    except Exception as e:
        print(f"Worker encountered an error: {e}. Terminating.")
        os._exit(1)

# Dispatcher (Serveur principal)
def dispatcher():
    try:
        # Shared Memory Segment
        shm = shared_memory.SharedMemory(create=True, size=10)
        buffer = shm.buf
        buffer[:4] = b'ping'

        # Named Pipe for synchronization
        parent_conn, child_conn = Pipe()

        p = Process(target=worker, args=(shm.name, child_conn))
        p.start()

        for _ in range(3):
            print(f"Dispatcher sending 'ping' to Worker.")
            parent_conn.send("ping")
            print(f"Dispatcher received: {parent_conn.recv()}")

        p.join()

        shm.unlink()
        shm.close()
    except Exception as e:
        print(f"Dispatcher encountered an error: {e}. Terminating.")
        os._exit(1)

# Watch-dog (Processus de surveillance)
def watch_dog():
    global received_signal
    received_signal = False
    try:
        # Configuration du gestionnaire de signaux
        signal.signal(signal.SIGUSR1, signal_handler)
        signal.signal(signal.SIGUSR2, signal_handler)

        p = Process(target=dispatcher)
        p.start()

        # Envoie d'un signal SIGUSR1 au dispatcher
        print(f"Watchdog sending SIGUSR1 to Dispatcher.")
        os.kill(p.pid, signal.SIGUSR1)
        
        # Vérification de l'état du signal
        time.sleep(1)  # Laisser le temps au gestionnaire de signaux de traiter
        if not received_signal:
            print("Watchdog did not receive SIGUSR2. Something might be wrong. Terminating dispatcher.")
            p.terminate()

        p.join()
    except Exception as e:
        print(f"Watchdog encountered an error: {e}. Terminating.")

if __name__ == '__main__':
    parent_pid = os.getpid()
    watch_dog()
