# 1 Mise en place d’un segment mémoire partagé entre un serveur principal et un serveur secondaire.
## a. Quel module utilisez-vous pour manipuler un segment mémoire partagé en Python 3 ?
Nous avons utilisé le module mmap de Python 3 pour créer et gérer un segment de mémoire partagée.

**Création du Segment de Mémoire Partagée** : Nous avons commencé par créer un fichier qui sert de support au segment de mémoire partagée. Ensuite, nous avons utilisé mmap.mmap() pour mapper ce fichier dans l'espace d'adressage de nos processus. Cela nous a permis de traiter ce segment comme un tableau de bytes directement accessible dans la mémoire.

**Lecture et Écriture dans la Mémoire Partagée** : Nous avons pu lire et écrire dans la mémoire partagée comme si nous manipulions un tableau de bytes classique grâce aux méthodes read(), write() et seek() de l'objet mmap.

# 2 Utilisation d’une paire de tubes nommés pour assurer la synchronisation

## a. Prévoyez le code nécessaire pour arrêter proprement les serveurs après un certain nombre d’échanges (ping-pong)
Nous n'avons pas compté le nombre de ping, pour redémarrer les serveurs proprement, nous avons cependant mis un système pour les redémarer de façon aléatoire. Dans ces conditions, nous fermons les sockets, les tubes puis les serveurs et nous les relançons.

## b. Quel serveur doit s’arrêter en premier pour éviter les zombies ? Qu’est ce qu’un zombie au sens informatique / système d’opération ?
Pour éviter les zombies, il faut arrêter le processus fils en premier, dans notre cas, cela représente les serveurs dispatcher et worker. 

Nous les fermons dans l'ordre suivant : Worker -> Dispatcher -> Watchdog. Nous les créons dans l'ordre inverse.

En informatique, le terme "zombie" se réfère généralement à un processus zombie, qui est un processus fils qui a terminé son exécution, mais dont l'entrée n'a pas encore été lue par le processus parent.

# 3 Mise en place d’un processus (indépendant) de surveillance

## a. Est-ce une bonne idée de lancer le serveur principal depuis le watch-dog puis les serveurs secondaires depuis le serveur principal ? Sachant que le watch-dog peut être amené à stopper et redémarrer [tous] les autres processus ? Doit-il déléguer le redémarrage d’un serveur secondaire au serveur principal, au risque de lui faire perdre en réactivité ?

Nous considérons qu'il est plus judicieux de confier au watch-dog la supervision directe de tous les processus, y compris les serveurs secondaires. Cela assure une meilleure réactivité et une gestion centralisée, surtout en cas de défaillance du serveur principal.

Dans notre implémentation, le watch-dog lance et surveille à la fois le serveur principal et le serveur secondaire. Ainsi, en cas de problème, le watch-dog peut intervenir directement pour redémarrer n'importe quel serveur, sans dépendre du serveur principal. Cette approche augmente la fiabilité de notre système et évite les dépendances qui pourraient conduire à des points de défaillance uniques.

## b. Est-ce une bonne idée d’utiliser les tubes de communication entre les serveurs pour établir une communication entre le watchdog et les serveurs ? Quelle est la conséquence si un serveur secondaire est figé et que le watch-dog lui donne l’ordre de redémarrer via « son » tube nommé (dwtube1..dwtuben) ?
Ce n'est pas forcément une bonne idée d'utiliser les tubes de communication entre les serveurs pour établir une communication entre le watchdog et les serveurs. En effet, si le serveur worker est figé, celui-ci ne lira plus le tube et de se fait ne sera pas correctement fermé par le watchdog.
Dans notre cas, nos sommes passé par une socket qui lie le watchdog au dispatcher, de ce fait, si le dispatcher n'intéragit plus avec le worker, il indiquera qu'il est toujours fonctionnel et que le worker lui répond bien.

## c. Comme illustré ci-dessous – sans forcément tout implémenter – ne serait-il pas judicieux d’utiliser des « signaux » (au sens du système d’exploitation) ? Est-ce que le père d’un processus est informé de l’arrêt d’un processus fils par un signal ?

Non, dans le contexte de notre projet, l'utilisation des signaux (au sens du système d'exploitation) pour la communication entre le watch-dog et les autres processus n'est pas optimale pour plusieurs raisons :

**Manque de Précision et de Contrôle** : Les signaux sont des mécanismes de communication bas-niveau qui ne fournissent pas beaucoup de détails. Ils ne permettent pas de transmettre des informations complexes ou des données spécifiques sur l'état du processus.

**Risques de Perte de Signal** : Les signaux peuvent parfois être perdus ou ne pas être traités instantanément, ce qui peut entraîner des délais ou des réponses incohérentes dans la surveillance des processus.

**Complexité de Gestion des Signaux** : La gestion des signaux nécessite un traitement asynchrone et peut compliquer la logique du programme, surtout lorsqu'il s'agit de gérer plusieurs sources de signaux.

# 4 Ajout d'un client
Nous avons implémenté une communication avec le client comme suit :
- **Etape 1** : Le client se connect au dispatcher.
- **Etape 2** : Le dispatcheur demande au worker s'il est disponible.
- **Etape 3** : Si le worker est disponible il répond que oui. Sinon : il répond que non et ferme les connexions ouvertes et ne fait pas les étapes suivantes.
- **Etape 4** : Le dispatcher renvoit l'adresse de connexion du worker au client.
Fermeture de la connexion entre le dispatcher et le client.
- **Etape 5** : Le client envoit sa requete au worker.
- **Etape 6** : Le worker répond à la requête.
Fermeture de la connexion entre le worker et le client.
- **Etape 7** : Le dispatcher demande au worker s'il a fini et celui-ci répond que oui.