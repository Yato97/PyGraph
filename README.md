# PyGraph

`pygraph` est un petit module Python 3 qui s'appuie sur les modules [`networkx`](https://networkx.org/) et [`graphviz`](https://graphviz.readthedocs.io/) pour modéliser et visualiser des graphes orientés, non orientés et bi-partie.

L'idée de ce module `pygraph` est de créer un objet `Graph` (ou `DiGraph` ou `BiPartite`) qui soit la réunion de deux objets :

- un `model` qui est un graphe au sens de _networkx_
- une `view` qui est un graphe au sens de _graphviz_

_work in progress_