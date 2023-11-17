"""
Watchdog Module

This module implements a Watchdog process that monitors and manages the health of the Dispatcher and Worker processes.

Usage:
- Run the Watchdog module through the main file.

The Watchdog communicates with the Dispatcher using a socket and periodically checks if the Dispatcher and Worker processes are running properly.

Author: Elena BEYLAT & Robin JOSEPH
"""

import os
import time
import socket
import random
import logging
import signal

import worker 
import dispatcher

def close_processes(pid, worker_pid):
    """
    Close the Dispatcher and Worker processes gracefully.

    Args:
    - pid (int): Process ID of the Dispatcher process.
    - worker_pid (int): Process ID of the Worker process.

    """
    logging.info("Watchdog: Closing process healthly.")
    
    # Terminer les processus
    close_process(pid, "Dispatcher")
    close_process(worker_pid, "Worker")
    
    delete_tube('dwtube1')
    delete_tube('wdtube1')
    
    if os.path.exists('shared_memory.txt'):
        os.remove('shared_memory.txt')
    
def close_process(pid, type_process):
    """
    Terminate a process gracefully.

    Args:
    - pid (int): Process ID of the process to be terminated.
    - type_process (str): Type of the process (e.g., "Dispatcher", "Worker").

    """
    os.kill(pid, signal.SIGTERM)
    logging.info(type_process+" process terminated.")

def delete_tube(tube):
    """
    Delete a named pipe.

    Args:
    - tube (str): The name of the named pipe to be deleted.

    """
    if os.path.exists(tube):
        os.remove(tube)



def run_watchdog():
    """
    Run the Watchdog process.

    This function creates named pipes, forks the Dispatcher and Worker processes, and monitors their health using a socket.

    """
    # Log the start of the Watchdog process
    logging.info("Watchdog started.")

    # Check if the named pipes 'dwtube1' and 'wdtube1' exist, create them if not
    if not os.path.exists('dwtube1'):
        os.mkfifo('dwtube1')
    if not os.path.exists('wdtube1'):
        os.mkfifo('wdtube1')

    # Fork a child process to run the Dispatcher
    pid = os.fork()
    if pid < 0:
        # Log an error if forking is not possible
        logging.info("fork() impossible")
        os.abort()
    elif pid == 0:
        # Child process: Run the Dispatcher
        dispatcher.run_dispatcher()
        os._exit(0)
    else:
        # Parent process
        
        # Fork another child process to run the Worker
        worker_pid = os.fork()
        if worker_pid < 0:
            # Log an error if forking is not possible
            logging.info("fork() impossible")
            os.abort()
        elif worker_pid == 0:
            # Child process: Run the Worker
            worker.run_worker()
            os._exit(0)
        else:
            # Parent process
            try:
                # Sleep briefly to allow child processes to start
                time.sleep(0.1)
                
                # Create a socket for communication with the Dispatcher
                watchdog_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                watchdog_socket.settimeout(4.0)
                dispatcher_address = ('localhost', 2224)
                watchdog_socket.connect(dispatcher_address)
                
                # Log a message indicating how to terminate the Watchdog
                logging.info("Press Ctrl+C to close")

                # Main monitoring loop
                while True:
                    # Generate a random message to send to the Dispatcher
                    choice = random.choice([b"Still running ?", b"Tu fonctionnes toujours ?", b"Try a refresh"])
                    watchdog_socket.sendall(choice)
                    try : 
                        # Attempt to receive a response from the Dispatcher
                        response = watchdog_socket.recv(1024)
                        response_dispatcher = response.decode()
                        logging.info(f"Watchdog received from Dispatcher : {response_dispatcher}")
                        
                        # If the response is not "Yes" or "Oui", something is wrong, restart processes
                        if response.decode() != "Yes" and response.decode() != "Oui":
                            close_processes(pid, worker_pid)
                            run_watchdog()
                    except socket.error as e:
                        # Log a timeout error, restart processes, and break out of the loop
                        logging.error(f"Timeout, restarting the serveur {e}")
                        close_processes(pid, worker_pid)
                        run_watchdog()
                        
                    # Sleep for 5 seconds before the next iteration
                    time.sleep(5)

            except KeyboardInterrupt:
                # If Ctrl+C is pressed, close processes and exit
                close_processes(pid, worker_pid)
                exit(0)
            except Exception as e:
                # Log any other exceptions that might occur during termination
                logging.error(f"An error occurred during termination: {e}")
            finally:
                # Close the socket in the finally block to ensure proper cleanup
                watchdog_socket.close()
