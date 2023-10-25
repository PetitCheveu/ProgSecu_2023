# Conseils du prof 1 : 
Ne pas utiliser les signaux car risque d'arrêt de procédure systèmes... -> comportements ératiques

Erreur de buffer dans les tubes présentés dans les aides du TP. Les deux restent en attente car le message est plus court que le buffer. Pour contrer cela, on ouvre et on ferme les tubes dans la boucle. Sinon, il faut générer le flush.
Appel à flush : fifo1.flush() pour éviter les open close en boucle.
Si on veut aller plus loin, on gère des buffer par nous mêmes.

multiprossessing : pourquoi c'est pas ouf : 
- Le segment n'est pas vu de l'extérieur -> client et serveur avec des langages différents avec des systèmes de mémoires partagés système et non python
- Unlink impossible à empêcher dans le gestionnaire de ressources. 
- Erreur acceptée dans le TP

pas de signaux
Tube jusqu'au flush
mémoire partagée : multiprossessing
processus voir
socket voir le moment venu -> existe en python pour du multiclient, pas nécessaire dans notre sujet, mais à voir

# Conseils du prof 2 : 
## Protocole d'échanges (de messages)
### Solution idéale
1) Requête du client au serveur principal (fait)
2) Délégation de traitement du serveur principal au serveur secondaire (?)
3) Acceptation de la requête (début traitement) + transmission d'infos du serveur secondaire au serveur principal à destination du client (N° port ...) (?)
4) Transmission de l'adresse, IP X N° port du client (fait)
5) Client transmet ses données au serveur secondaire (fait)
6) Serveur secondaire envoie résultat de requête au client (fait)
7) Serveurs secondaires informe serveur principal de la fin de traitement de requête.

### Solution autre
1) Requête du client au SP
2) SP-> SS
3) SS -> SP
4) SS -> Client (qui il est)
5) Client -> SS (requête)
6) SS -> Client (réponse)

### Fonctionnement en états : 
0.. -> Etat du client
1.. -> Etat du serveur principal
2.. -> Etat du serveur secondaire

0 -> Envoi d'une requête au serveur principal
1 -> Attente d'une réponse du serveur principal (sollution 1) ou secondaire (solution 2) -> c'est sa position d'attente
10 -> Attente d'une requête client ou watchdog -> c'est sa position d'attente -> Attente de deux évènements différents, les deux par sockets ? utilisation de timeout
20 -> Attente d'authorisation de lecture dans le segment mémoire partagé ou du watchdog -> Pas en attente sur une socket, mais sur un tube -> Position d'attente
21 -> Séparer l'attente du watchdog pour le faire après

# TODO : 
Gestion des erreurs : Assurez-vous de gérer les erreurs correctement dans votre code, en utilisant des blocs try/except pour capturer les exceptions qui pourraient survenir lors de l'ouverture de fichiers, de la création de sockets, etc. Cela rendra votre code plus robuste.

Documentation : Ajoutez des commentaires et de la documentation aux parties importantes de votre code pour expliquer ce que fait chaque fonction et chaque section. Cela rendra votre code plus compréhensible pour les autres et pour vous-même à l'avenir.

Gestion de la fermeture des sockets : Assurez-vous de fermer correctement les sockets en utilisant des blocs try/finally pour garantir que les sockets sont fermés même en cas d'erreur.

Gestion des exceptions : Assurez-vous que votre code gère correctement les exceptions à tous les niveaux, notamment lors de la création de sockets, de l'écriture/l'ouverture de fichiers, etc.

Nettoyage des ressources : Vous avez commencé à ajouter du code pour nettoyer les ressources (tubes nommés, mémoire partagée) à la fin du watchdog, mais assurez-vous que cela fonctionne correctement.

Réactivité du serveur principal : La question 3.a concerne la réactivité du serveur principal face aux redémarrages initiés par le watchdog. Cela dépendra de la nature de votre application et de vos besoins spécifiques, mais il est important de considérer comment votre système doit réagir en cas de redémarrage.