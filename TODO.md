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

TODO : 
Gestion des erreurs : Assurez-vous de gérer les erreurs correctement dans votre code, en utilisant des blocs try/except pour capturer les exceptions qui pourraient survenir lors de l'ouverture de fichiers, de la création de sockets, etc. Cela rendra votre code plus robuste.

Documentation : Ajoutez des commentaires et de la documentation aux parties importantes de votre code pour expliquer ce que fait chaque fonction et chaque section. Cela rendra votre code plus compréhensible pour les autres et pour vous-même à l'avenir.

Gestion de la fermeture des sockets : Assurez-vous de fermer correctement les sockets en utilisant des blocs try/finally pour garantir que les sockets sont fermés même en cas d'erreur.

Utilisation de variables explicites : Utilisez des noms de variables explicites pour améliorer la lisibilité de votre code. Par exemple, au lieu d'utiliser b"requetetype1", utilisez une variable avec un nom explicite comme request_type = b"requetetype1".

Gestion de la communication entre le client et le serveur principal : Assurez-vous que la communication entre le client et le serveur principal est correctement gérée. Actuellement, vous envoyez simplement une requête au serveur principal, mais il semble manquer la logique pour gérer la réponse du serveur principal et établir la connexion avec le serveur secondaire.

Gestion de la communication entre le serveur principal et les serveurs secondaires : De même, assurez-vous de mettre en place une communication appropriée entre le serveur principal et les serveurs secondaires. Cela semble impliquer l'utilisation de tubes nommés, mais assurez-vous que cela fonctionne correctement.

Gestion de la synchronisation : Assurez-vous que la synchronisation entre les différents processus (client, serveur principal, serveurs secondaires et watchdog) est correctement implémentée. Les tubes nommés et les mécanismes de temporisation semblent être une approche, mais cela doit être testé minutieusement pour garantir la synchronisation.

Gestion des exceptions : Assurez-vous que votre code gère correctement les exceptions à tous les niveaux, notamment lors de la création de sockets, de l'écriture/l'ouverture de fichiers, etc.

Nettoyage des ressources : Vous avez commencé à ajouter du code pour nettoyer les ressources (tubes nommés, mémoire partagée) à la fin du watchdog, mais assurez-vous que cela fonctionne correctement.

Test et débogage : Testez votre code étape par étape pour vous assurer que chaque composant fonctionne comme prévu. Utilisez des messages de débogage pour suivre le flux de votre programme et corrigez les erreurs au fur et à mesure.

Réactivité du serveur principal : La question 3.a concerne la réactivité du serveur principal face aux redémarrages initiés par le watchdog. Cela dépendra de la nature de votre application et de vos besoins spécifiques, mais il est important de considérer comment votre système doit réagir en cas de redémarrage.

Utilisation de signaux : La question 3.c suggère d'utiliser des signaux pour la surveillance. Les signaux peuvent être utiles pour détecter si un processus est figé, mais cela nécessite une gestion de signaux appropriée dans votre code.