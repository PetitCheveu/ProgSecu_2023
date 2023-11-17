import socket
import random
import logging

def run_client():
    logging.info("Client started.")

    try : 
        while True:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.settimeout(3.0)
            client_socket.connect(('localhost', 2222))
            try:
                abort = False
                requete = random.randint(1, 2)
                if requete == 1:
                    requete_type = "requetetype1"
                else:
                    requete_type = "requetetype2"

                client_socket.sendall(requete_type.encode())
                logging.info(f"Etape 1 : Client sent request: {requete_type}")
                
                port_data = client_socket.recv(1024)
                secondary_port = int(port_data.decode())
                if secondary_port != -1 : 
                    abort = False
                    logging.info(f"Etape 4 : Client received secondary port: {secondary_port}")

                    secondary_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    secondary_socket.settimeout(3.0)
                    secondary_socket.connect(('localhost', secondary_port))
                    logging.info("Etape 5 : Client connected to secondary server.")

                    if requete_type == "requetetype1" :
                        secondary_socket.sendall(b"Hello, what time is it ?")
                    else : 
                        secondary_socket.sendall(b"Hello, what's the date today ?")
                    data = secondary_socket.recv(1024)
                    logging.info(f"Etape 6 : Client received from secondary server: {data.decode()}")
                else : 
                    abort = True
            except socket.error as se:
                logging.error(f"Timeout, closing client: {e}")
                abort = True
            except Exception as e:
                logging.error(f"An error occurred: {str(e)}")

            finally:
                if not abort : 
                    secondary_socket.close()

            if not abort : 
                user_input = input("Voulez-vous envoyer une autre requête ? (Oui/Non): ")
                if user_input.lower() != "oui" and user_input.lower() != "o":
                    client_socket.close()
                    break
            else : 
                logging.info("Aborting connection because the worker is too busy")
                break

        
    except Exception as e : 
        logging.error(f"An error occurred: {str(e)}")