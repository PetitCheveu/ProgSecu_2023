# 1 Mise en place d’un segment mémoire partagé entre un serveur principal et un serveur secondaire.
## a. Quel module utilisez-vous pour manipuler un segment mémoire partagé en Python 3 ?
Pour manipuler la mémoire partagée, nous utilisons mmap [compléter]
# 2 Utilisation d’une paire de tubes nommés pour assurer la synchronisation
## a. Prévoyez le code nécessaire pour arrêter proprement les serveurs après un certain nombre d’échanges (ping-pong)
Nous n'avons pas compté le nombre de ping, pour redémarrer les serveurs proprement, nous avons cependant mis un système pour les redémarer de façon aléatoire. Dans ces conditions, nous fermons les sockets, les tubes puis les serveurs et nous les relançons.
## b. Quel serveur doit s’arrêter en premier pour éviter les zombies ? Qu’est ce qu’un zombie au sens informatique / système d’opération ?
[compléter]
# 3 Mise en place d’un processus (indépendant) de surveillance
## a. Est-ce une bonne idée de lancer le serveur principal depuis le watch-dog puis les serveurs secondaires depuis leserveur principal ? Sachant que le watch-dog peut être amené à stopper et redémarrer [tous] les autres processus ? Doit-il déléguer le redémarrage d’un serveur secondaire au serveur principal, au risque de lui faire perdre en réactivité ?
[compléter]
Ce n'est pas une solution que nous utilisons, dans notre cas, le watchdog démarre le serveur dispatcher, puis il démarre le serveur worker. C'est également lui qui s'occupe de tout fermer en cas de soucis.
## b. Est-ce une bonne idée d’utiliser les tubes de communication entre les serveurs pour établir une communication entre le watchdog et les serveurs ? Quelle est la conséquence si un serveur secondaire est figé et que le watch-dog lui donne l’ordre de redémarrer via « son » tube nommé (dwtube1..dwtuben) ?
Ce n'est pas forcément une bonne idée d'utiliser les tubes de communication entre les serveurs pour établir une communication entre le watchdog et les serveurs. En effet, si le serveur worker est figé, celui-ci ne lira plus le tube et de se fait ne sera pas correctement fermé par le watchdog.
Dans notre cas, nos sommes passé par une socket qui lie le watchdog au dispatcher, de ce fait, si le dispatcher n'intéragit plus avec le worker, il indiquera qu'il est toujours fonctionnel et que le worker lui répond bien.
## c. Comme illustré ci-dessous – sans forcément tout implémenter    – ne serait-il pas judicieux d’utiliser des « signaux » (au sens du système d’exploitation) ? Est-ce que le père d’un processus est informé de l’arrêt d’un processus fils par un signal ?
Non, l'utilisation de signaux pour le watchdog n'est pas optimale. Cela peut causer des comportements ératiques en cas de fermeture de processus
[compléter]
# 4 Ajout d'un client
Nous avons implémenté une communication avec le client comme suit :
Etape 1 : Le client se connect au dispatcher.
Etape 2 : Le dispatcheur demande au worker s'il est disponible.
Etape 3 : Si le worker est disponible il répond que oui. Sinon : il répond que non et ferme les connexions ouvertes et ne fait pas les étapes suivantes.
Etape 4 : Le dispatcher renvoit l'adresse de connexion du worker au client.
Fermeture de la connexion entre le dispatcher et le client.
Etape 5 : Le client envoit sa requete au worker.
Etape 6 : Le worker répond à la requête.
Fermeture de la connexion entre le worker et le client.
Etape 7 : Le dispatcher demande au worker s'il a fini et celui-ci répond que oui.