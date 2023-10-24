import os
import time
import socket
import json
import random
import select
import logging

def run_client():
    logging.info("Client started.")

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 2222))
    while True:
        try:
            requete = random.randint(1, 2)
            if requete == 1:
                requete_type = "requetetype1"
            else:
                requete_type = "requetetype2"

            client_socket.sendall(requete_type.encode())
            logging.info(f"Etape 1 : Client sent request: {requete_type}")

            port_data = client_socket.recv(1024)
            secondary_port = int(port_data.decode())
            logging.info(f"Etape 4 : Client received secondary port: {secondary_port}")

            secondary_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            secondary_socket.connect(('localhost', secondary_port))
            logging.info("Etape 5 : Client connected to secondary server.")

            if requete_type == "requetetype1" :
                secondary_socket.sendall(b"Hello, secondary server!")
            else : 
                secondary_socket.sendall(b"Salut, serveur secondaire!")
            data = secondary_socket.recv(1024)
            logging.info(f"Etape 6 : Client received from secondary server: {data.decode()}")

        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")

        finally:
            secondary_socket.close()

        user_input = input("Voulez-vous envoyer une autre requête ? (Oui/Non): ")
        if user_input.lower() != "oui" and user_input.lower() != "o":
            break

    client_socket.close()