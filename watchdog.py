import os
import time
import socket
import json
import random
import select
import logging

import worker 
import dispatcher


def run_watchdog():
    logging.info("Watchdog started.")
    
    if os.path.exists('stop_tube'):
        os.remove('stop_tube')
    
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
        dispatcher.run_dispatcher()
        os._exit(0)
    else:
        worker_pid = os.fork()
        if worker_pid < 0:
            logging.info("fork() impossible")
            os.abort()
        elif worker_pid == 0:
            worker.run_worker()
            stop_fifo_in = os.open('stop_tube', os.O_RDONLY | os.O_NONBLOCK)
            os._exit(0)
        else:
            time.sleep(20)
            with open('stop_tube', 'w') as stop_fifo:
                stop_fifo.write('stop')
                logging.info("Watchdog: Closing process healthly.")
        
                if os.path.exists('dwtube1'):
                    os.remove('dwtube1')
                if os.path.exists('wdtube1'):
                    os.remove('wdtube1')
                if os.path.exists('shared_memory.txt'):
                    os.remove('shared_memory.txt')
            if os.path.exists('stop_tube'):
                os.remove('stop_tube')
                