import logging

import client 
import watchdog

logging.basicConfig(level=logging.DEBUG)


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
