"""
Client Module

This module defines a simple client application that connects to a server, sends requests, and receives responses.

The client can send two types of requests ('requetetype1' or 'requetetype2') and communicate with a secondary server
on a dynamically assigned port. It allows the user to send multiple requests and terminates based on user input.

Author: Elena BEYLAT & Robin JOSEPH
"""

import socket
import random
import logging

def run_client():
    """
    Run the client application.

    This function initiates a connection to a server, sends requests of two types, and communicates with a secondary server
    on a dynamically assigned port. It allows the user to send multiple requests and terminates based on user input.

    """
    # Log the start of the client
    logging.info("Client started.")

    try : 
        # Main loop for handling user requests
        while True:
            # Create a new socket for each iteration of the loop
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.settimeout(3.0)
            
            # Connect to the server on port 2222
            client_socket.connect(('localhost', 2222))
            
            try:
                abort = False
                # Generate a random request type
                requete = random.randint(1, 2)
                if requete == 1:
                    requete_type = "requetetype1"
                else:
                    requete_type = "requetetype2"

                # Send the request type to the server
                client_socket.sendall(requete_type.encode())
                logging.info(f"Etape 1 : Client sent request: {requete_type}")
                
                # Receive the secondary port number from the server
                port_data = client_socket.recv(1024)
                secondary_port = int(port_data.decode())
                
                # If a valid secondary port is received, proceed to communicate with the secondary server
                if secondary_port != -1 : 
                    abort = False
                    logging.info(f"Etape 4 : Client received secondary port: {secondary_port}")

                    # Create a new socket for communicating with the secondary server
                    secondary_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    secondary_socket.settimeout(3.0)
                    
                    # Connect to the secondary server on the dynamically assigned port
                    secondary_socket.connect(('localhost', secondary_port))
                    logging.info("Etape 5 : Client connected to secondary server.")

                    # Send a message to the secondary server based on the request type
                    if requete_type == "requetetype1" :
                        secondary_socket.sendall(b"Hello, what time is it ?")
                    else : 
                        secondary_socket.sendall(b"Hello, what's the date today ?")
                    
                    # Receive and log the response from the secondary server
                    data = secondary_socket.recv(1024)
                    logging.info(f"Etape 6 : Client received from secondary server: {data.decode()}")
                else : 
                    # If the secondary port is -1, set abort to True
                    abort = True
            except socket.error as se:
                # Log a timeout error, set abort to True
                logging.error(f"Timeout, closing client: {e}")
                abort = True
            except Exception as e:
                # Log any other exceptions, set abort to True
                logging.error(f"An error occurred: {str(e)}")

            finally:
                # Close the secondary socket in the finally block to ensure proper cleanup
                if not abort : 
                    secondary_socket.close()

            # Prompt the user to send another request
            if not abort : 
                user_input = input("Voulez-vous envoyer une autre requête ? (Oui/Non): ")
                if user_input.lower() != "oui" and user_input.lower() != "o":
                    # Close the client socket and break out of the loop
                    client_socket.close()
                    break
            else : 
                # Log that the connection is aborted due to the worker being too busy
                logging.info("Aborting connection because the worker is too busy")
                break

        
    except Exception as e : 
        # Log any other exceptions that might occur during the execution of the client
        logging.error(f"An error occurred: {str(e)}")