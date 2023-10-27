import os
import time
import socket
import json
import random
import select
import logging
import signal

import worker 
import dispatcher

def close_processes(pid, worker_pid):
    logging.info("Watchdog: Closing process healthly.")
    
    # Terminer les processus
    close_process(pid, "Dispatcher")
    close_process(worker_pid, "Worker")
    
    delete_tube('dwtube1')
    delete_tube('wdtube1')
    
    if os.path.exists('shared_memory.txt'):
        os.remove('shared_memory.txt')
    exit(0)
    
def close_process(pid, type_process):
    os.kill(pid, signal.SIGTERM)
    logging.info(type_process+" process terminated.")

def delete_tube(tube):
    if os.path.exists(tube):
        os.remove(tube)

def run_watchdog():
    logging.info("Watchdog started.")

    if not os.path.exists('dwtube1'):
        os.mkfifo('dwtube1')
    if not os.path.exists('wdtube1'):
        os.mkfifo('wdtube1')

    pid = os.fork()
    if pid < 0:
        logging.info("fork() impossible")
        os.abort()
    elif pid == 0:
        dispatcher.run_dispatcher()
        os._exit(0)
    else:
        worker_pid = os.fork()
        if worker_pid < 0:
            logging.info("fork() impossible")
            os.abort()
        elif worker_pid == 0:
            worker.run_worker()
            os._exit(0)
        else:
            try:
                time.sleep(0.1)
                watchdog_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                dispatcher_address = ('localhost', 2224)
                watchdog_socket.connect(dispatcher_address)
                logging.info("Press Ctrl+C to close")

                while True:
                    logging.info("test")
                    choice = random.choice([b"Still running ?", b"Ca fonctionne toujours ?"])
                    watchdog_socket.sendall(choice)
                    timeout = time.time() + 100000
                    logging.debug(f"timeout : {timeout}")
                    try : 
                        response = watchdog_socket.recv(1024)
                        response_dispatcher = response.decode()
                        logging.info(f"Watchdog received from Dispatcher : {response_dispatcher}")
                        if response.decode() != "Yes" and response.decode() != "Oui":
                            close_processes(pid, worker_pid)
                            break
                    except time.time() > timeout :
                        logging.error("Timeout, restarting the serveur")
                        close_processes(pid, worker_pid)
                        # restart_serveur()
                        break
                    time.sleep(5)

            except KeyboardInterrupt:
                close_processes(pid, worker_pid)
            except Exception as e:
                logging.error(f"An error occurred during termination: {e}")
            finally:
                watchdog_socket.close()
