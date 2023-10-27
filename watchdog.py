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
    
    # Terminer le processus du dispatcher
    os.kill(pid, signal.SIGTERM)
    logging.info("Dispatcher process terminated.")
    
    # Terminer le processus du worker
    os.kill(worker_pid, signal.SIGTERM)
    logging.info("Worker process terminated.")

    if os.path.exists('dwtube1'):
        os.remove('dwtube1')
    if os.path.exists('wdtube1'):
        os.remove('wdtube1')
    if os.path.exists('shared_memory.txt'):
        os.remove('shared_memory.txt')
    exit(0)


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
                logging.info("Press Ctrl+C to close")
                signal.pause()  # Attendre jusqu'à ce que Ctrl+C soit pressé
            except KeyboardInterrupt:
                close_processes(pid, worker_pid)
            except Exception as e:
                logging.error(f"An error occurred during termination: {e}")
            # try:
            #     time.sleep(5)
            #     logging.info("Ctrl+C to close")

            #     close_processes(pid, worker_pid)
            # except Exception as e:
            #     logging.error(f"An error occurred during termination: {e}")
                
