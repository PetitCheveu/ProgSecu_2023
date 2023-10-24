import logging

import client 
import dispatcher
import worker
import watchdog

logging.basicConfig(level=logging.INFO)


if __name__ == '__main__':
    print("1: Run Watchdog (and servers)")
    print("2: Run Client")
    choice = input("Choose an option: ")
    
    if choice == '1':
        watchdog.run_watchdog()
    elif choice == '2':
        client.run_client()
    else:
        logging.debug("Invalid option.")
