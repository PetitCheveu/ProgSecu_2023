*French below*

# Systems and secure programming

## Description

This project, carried out as part of the Systems and Secure Programming teaching unit at INSA Hauts-de-France, involves the development of a client-server architecture in Python 3. The architecture comprises a main server (dispatcher), secondary servers (workers), a watch-dog process and a client-server.

## Components

- **Client** : The client sends a request to the dispatcher, and receives a response from the worker.

- **Dispatcher** : The dispatcher receives requests from the client, verify the availability of the worker, and forwards the request to the worker.

- **Worker** : The worker receives requests from the dispatcher, processes them and sends the response to the client.

- **Watch-dog** : The watch-dog supervises the dispatcher and the worker. It restarts them if they are no longer functional.

## Installation and Execution

1. **Requirements** : Python 3
2. **Watch-dog execution** : The monitoring process have to be launched first.
```bash
python3 main.py
1. Run Watchdog (and servers)
2. Run Client
Choose an option : 1
```
3. **Client execution** : The client can be launched after the watch-dog.
```bash
python3 main.py
1. Run Watchdog (and servers)
2. Run Client
Choose an option : 2
```

## Architecture and Communication Flow

- The client initiates a TCP connection on port 2222 with the main server.
- The dispatcher directs requests to the worker.
The worker processes requests and sends responses back to the client.
- The watchdog monitors the status of all servers and restarts components if necessary.

## Authors

[](https://www.linkedin.com/in/elena-beylat-166333234/) **Elena Beylat**

[](https://www.linkedin.com/in/robinjoseph-8259/) **Robin Joseph**

---
---
---

*Français*

# Systèmes et programmation sécurisée

## Description

Ce projet, réalisé dans le cadre de l'unité d'enseignement Systèmes et Programmation Sécurisée à l'INSA Hauts-de-France, consiste en le développement d'une architecture client-serveur en Python 3. L'architecture comprend un serveur principal (dispatcher), des serveurs secondaires (workers), un processus de surveillance (watch-dog) et un client.

## Composants

- **Client** : Le client envoie une requête au dispatcher, et attend la réponse du worker.

- **Dispatcher** : Le dispatcher reçoit les requêtes du client, vérifie la disponibilité du worker, et lui transmet la requête.

- **Worker** : Le worker reçoit les requêtes du dispatcher, les traite et envoie la réponse au client.

- **Watch-dog** : Le watch-dog supervise le dispatcher et le worker. Il les redémarre s'ils ne sont plus fonctionnels.

## Installation et Exécution

1. **Prérequis** : Python 3
2. **Exécution du watch-dog** : Le processus de surveillance doit être lancé en premier.
```bash
python3 main.py
1. Run Watchdog (and servers)
2. Run Client
Choose an option : 1
```

3. **Exécution du client** : Le client peut être lancé après le watch-dog.
```bash
python3 main.py
1. Run Watchdog (and servers)
2. Run Client
Choose an option : 2
```

## Architecture et Flux de Communication

- Le client initie une connexion TCP sur le port 2222 avec le serveur principal.
- Le dispatcher dirige les requêtes vers le worker.
- Le worker traite les requêtes et envoie les réponses au client.
- Le watch-dog surveille l'état de tous les serveurs et redémarre les composants si nécessaire.

## Auteurs

[](https://www.linkedin.com/in/elena-beylat-166333234/) **Elena Beylat**

[](https://www.linkedin.com/in/robinjoseph-8259/) **Robin Joseph**
