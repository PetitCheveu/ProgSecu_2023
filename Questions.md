# 1 Mise en place d’un segment mémoire partagé entre un serveur principal et un serveur secondaire.
## a. Quel module utilisez-vous pour manipuler un segment mémoire partagé en Python 3 ?
# 2 Utilisation d’une paire de tubes nommés pour assurer la synchronisation
## a. Prévoyez le code nécessaire pour arrêter proprement les serveurs après un certain nombre d’échanges (ping-pong)
## b. Quel serveur doit s’arrêter en premier pour éviter les zombies ? Qu’est ce qu’un zombie au sens informatique / système d’opération ?
# 3 Mise en place d’un processus (indépendant) de surveillance
## a. Est-ce une bonne idée de lancer le serveur principal depuis le watch-dog puis les serveurs secondaires depuis leserveur principal ? Sachant que le watch-dog peut être amené à stopper et redémarrer [tous] les autres processus ? Doit-il déléguer le redémarrage d’un serveur secondaire au serveur principal, au risque de lui faire perdre en réactivité ?
## b. Est-ce une bonne idée d’utiliser les tubes de communication entre les serveurs pour établir une communication entre le watchdog et les serveurs ? Quelle est la conséquence si un serveur secondaire est figé et que le watch-dog lui donne l’ordre de redémarrer via « son » tube nommé (dwtube1..dwtuben) ?
## c. Comme illustré ci-dessous – sa   ns forcément tout implémenter    – ne serait-il pas judicieux d’utiliser des « signaux » (au sens du système d’exploitation) ? Est-ce que le père d’un processus est informé de l’arrêt d’un processus fils par un signal ?
# 4 Ajout d'un client