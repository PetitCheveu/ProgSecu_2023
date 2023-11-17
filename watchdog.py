import os
import time
import socket
import random
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
                watchdog_socket.settimeout(4.0)
                dispatcher_address = ('localhost', 2224)
                watchdog_socket.connect(dispatcher_address)
                logging.info("Press Ctrl+C to close")

                while True:
                    choice = random.choice([b"Still running ?", b"Tu fonctionnes toujours ?", b"Try a refresh"])
                    watchdog_socket.sendall(choice)
                    try : 
                        response = watchdog_socket.recv(1024)
                        response_dispatcher = response.decode()
                        logging.info(f"Watchdog received from Dispatcher : {response_dispatcher}")
                        if response.decode() != "Yes" and response.decode() != "Oui":
                            close_processes(pid, worker_pid)
                            run_watchdog()
                    except socket.error as e:
                        logging.error(f"Timeout, restarting the serveur {e}")
                        close_processes(pid, worker_pid)
                        run_watchdog()
                        # restart_serveur() #Ecrire la fonction pour pouvoir relancer tout (peut-être qu'un simple run_watchdog suffit ?)
                        break
                    time.sleep(5)

            except KeyboardInterrupt:
                close_processes(pid, worker_pid)
                exit(0)
            except Exception as e:
                logging.error(f"An error occurred during termination: {e}")
            finally:
                watchdog_socket.close()
