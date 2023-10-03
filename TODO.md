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