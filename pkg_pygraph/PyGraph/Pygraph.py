"""
pygraph.py

Un petit module pour créer des graphes (non orienté, orienté ou bi-partie)
Avec visualisation via Graphviz et possibilité de modifier quelques propriétés visuelles (couleur, forme, étiquette)

Auteur  : Sébastien Hoarau
Date    : 2021-08
Licence : CC BY-NC-SA 4.0 http://creativecommons.org/licenses/by-nc-sa/4.0/
Site    : gitlab.com/sebhoa/pygraph/

TODO
----
    - Plus de tests. Il reste probablement beaucoup de bugs à corriger
    - Ajouter d'autres algorithmes sur les graphes
    - traiter des graphes valués
"""

import imp
import graphviz as gv
import networkx as nx
import random
import json
import io
from PyGraph.constantes import *

# -----------
# LES CLASSES

class NodeView:
    """
    La classe NodeView modélise les propriétés d'un noeud pour sa visualisation. 
    Cet objet est stocké comme information supplémentaire du modèle networkx
    
    Parameters
    ----------
        gv : graphviz.Graph | graphviz.Digraph
            la vue à laquelle cette vue noeud est rattachée
        node_id : int
            numéro identifiant le sommet
        color_id : int
            un numéro de couleur (valeur par défaut -1)
    """

    def __init__(self, gv, node_id, color_id=WHITE, fontsize=FONTSIZE):        
        self.__gv = gv
        self.__id = node_id 
        self.__color_id = color_id
        self.__pos = None
        self.__label = str(node_id)
        self.__ech = 1
        self.__width = NODE_WIDTH
        self.__fontsize = fontsize
    
    # Public attributes
    
    @property
    def id(self):
        return self.__id
        
    @property
    def color_id(self):
        return self.__color_id
    
    @color_id.setter
    def color_id(self, color_id):
        self.__color_id = min(max(-len(COLORS), color_id), len(COLORS)-1)
    
    @property
    def pos(self):
        return self.__pos
    
    @pos.setter
    def pos(self, pos):
        self.__pos = pos
        
    @property
    def width(self):
        return self.__width
    
    @width.setter
    def width(self, width):
        self.__width = width

    @property
    def ech(self):
        return self.__ech
    
    @ech.setter
    def ech(self, ech):
        self.__ech = ech

    @property
    def label(self):
        return self.__label
    
    @label.setter
    def label(self, label):
        if not isinstance(label, str):
            label = str(self.id)
        self.__label = label
    
    @property
    def gv(self):
        return self.__gv
   
    @property
    def fontsize(self):
        return self.__fontsize

    
    # View modification methods
    
    def create(self):
        self.__gv.node(str(self.id), self.label, shape=CIRCLE, style='filled', fillcolor=self.color(), width=NODE_WIDTH, height=NODE_HEIGHT, fontsize=self.fontsize)
    
    
    # -- about labels
    
    def label_on(self, label = None, color=COLORS[BLACK]):
        if label == None:
            self.__gv.node(str(self.id), self.label, fontcolor=color, fontsize=FONTSIZE)
        else:
            if len(label) <= 2:
                self.__gv.node(str(self.id), label, fontcolor=color, fontsize=FONTSIZE)
            elif len(label) > 2 and len(label) <= 5:
                self.__gv.node(str(self.id), label, fontcolor=color, fontsize=REDUCE_FONTSIZE)
            else:
                self.__gv.node(str(self.id), xlabel=label, fontcolor=color, fontsize=FONTSIZE)
                
                

    def label_off(self):
        self.__gv.node(str(self.id), NOLABEL)
        
    def label_on_side(self, label=None, color=COLORS[BLACK]):
        if label == None:
            self.__gv.node(str(self.id), xlabel=self.label, fontcolor=color)
        else:
            self.__gv.node(str(self.id), xlabel=label, fontcolor=color)

    def label_off_side(self):
        self.__gv.node(str(self.id), xlabel=NOLABEL)
        
    
    # -- about colors
    
    def color(self):
        return COLORS[self.color_id]
    
    def color_on(self, color=None):
        if isinstance(color, str):
            color_str = color
        elif isinstance(color, int):
            try:
                color_str = COLORS[color]
            except:
                color_str = COLORS[WHITE]
        else:
            color_str = self.color()
        self.__gv.node(str(self.id), style='filled', fillcolor=color_str)

    def color_off(self):
        self.__gv.node(str(self.id), style='filled', fillcolor=COLORS[WHITE])
        
        
    # -- about position and size
    
    def _is_positioned(self):
        return self.pos is not None

    def move(self, dx, dy):
        if self._is_positioned():
            self.pos = self.pos[0] + dx, self.pos[1] + dy

    def place(self, ech=None):
        if self._is_positioned():
            ech = self.ech if ech is None else ech
            self.ech = ech
            x, y = self.pos
            pos = f'{x*ech},{y*ech}!'
            self.__gv.node(str(self.id), pos=pos)
            
        
    def size(self, *dim):
        if len(dim) == 0:
            w, h = NODE_WIDTH, NODE_HEIGHT
            self.width = NODE_WIDTH
        elif len(dim) == 1:
            w, h = dim[0], dim[0]
            self.width = dim[0]
        else:
            w, h = dim
            width = dim[0]
        self.__gv.node(str(self.id), width=str(w), height=str(h))


    
class EdgeView:
    """
    La classe EdgeView modélise les propriétés d'une arête ou d'un arc pour sa visualisation. 
    Cet objet est stocké comme information supplémentaire du modèle networkx
    
    Parameters
    ----------
        gv : graphviz.Graph | graphviz.Digraph
            la vue à laquelle cette vue noeud est rattachée
        edge : 
            couple de node_id identifiant l'arc/arête
        color_id : int
            un numéro de couleur (valeur par défaut -1)
        weight : 
            La dimension l'attribut shape circle qui est égale à la hauteur
    """

    def __init__(self, gv, node_src, node_dst, weight=None, color_id=BLACK):        
        self.__gv = gv
        self.__edge = (node_src, node_dst)
        self.__color_id = color_id
        self.__weight = weight
        
    # Public attributes
    
    @property
    def edge(self):
        return self.__edge
        
    @property
    def color_id(self):
        return self.__color_id
    
    @color_id.setter
    def color_id(self, color_id):
        self.__color_id = min(max(-len(COLORS), color_id), len(COLORS)-1)

    @property
    def weight(self):
        return self.__weight
    
    @weight.setter
    def weight(self, weight):
        if not isinstance(weight, str):
            weight = str(self.weight)
        self.__weight = weight
    
    @property
    def gv(self):
        return self.__gv
   
    
    # View modification methods
    
    def create(self):
        if not self.weight:
            self.__gv.edge(str(self.edge[0]), str(self.edge[1]), style='filled', color=self.color())
        else:
            self.__gv.edge(str(self.edge[0]), str(self.edge[1]), str(self.weight), style='filled', color=self.color())
        
    
    # -- about colors
    
    def color(self):
        return COLORS[self.color_id]
    
    def color_on(self, color=None):
        if isinstance(color, str):
            color_str = color
        elif isinstance(color, int):
            try:
                color_str = COLORS[color]
            except:
                color_str = COLORS[BLACK]
        else:
            color_str = self.color()
        self.gv.edge(str(self.edge[0]), str(self.edge[1]), str(self.weight), style='filled', color=color_str)

    def color_off(self):
        self.__gv.edge(str(self.edge[0]), str(self.edge[1]), style='filled', color=COLORS[BLACK])
        
            
class Graph:
    """
    class Graph modélise un graphe non orienté dont le propriétés importantes sont :
    - model : un objet graphe au sens de networkx
    - view : un objet graphe au sens de graphviz
        
    Parameters:
    -----------
        nodes_count : int
            le nombre de sommets du graphe (par défaut 0)
        random : bool
            un flag pour savoir si le graphe généré est aléatoire. Si True alors le modèle sera 
            nx.erdos_renyi_graph(nodes_count, 0.5)
        engine : str
            le moteur de rendu (au sens de graphviz) ; par défaut 'neato'
    
    Note:
    -----
        Les autres paramètres ne devraient pas être utilisés : ils servent pour la création
        des graphes orientés et des graphes bi-partie
    """
        
    def __init__(self, nodes_count=0, random=False, directed=False, bipartite=False, n1=0, n2=0, engine='neato', strict=False):
        if random:
            self.__model = nx.erdos_renyi_graph(nodes_count, 0.5)
        elif directed:
            self.__model = nx.DiGraph()
        elif bipartite:
            self.__model = nx.complete_bipartite_graph(n1, n2)
        else:
            self.__model = nx.Graph()
        if directed:
            self.__view = gv.Digraph(engine=engine, strict=strict, edge_attr={'arrowsize':ARROWSIZE}, node_attr={'fixedsize':'true', 'width':NODE_WIDTH, 'height':NODE_HEIGHT, 'margin':NODE_MARGIN})
        else:
            self.__view = gv.Graph(engine=engine, strict=strict, node_attr={'fixedsize':'true', 'width':NODE_WIDTH, 'height':NODE_HEIGHT, 'margin':NODE_MARGIN})
        self.__engine = engine
        self.__model.add_nodes_from([node_id, {'view': None}] for node_id in range(nodes_count))
        self.init_view()
        
    
    @property
    def model(self):
        return self.__model
    
    @model.setter
    def model(self, model):
        self.__model = model
    
    @property
    def view(self):
        return self.__view
    
    @view.setter
    def view(self, view):
        self.__view = view

    @property
    def engine(self):
        return self.__engine
    
    @engine.setter
    def engine(self, engine):
        self.__engine = engine
    
    # MODEL METHODS
    
    # -- about information
    
    def node_ids(self):
        return self.model.nodes
    
    def edges(self):
        return self.model.edges
    
    def edge_informations(self, s1, s2):
        return self.model.adj[s1][s2]
    
    def number_of_nodes(self):
        return self.model.number_of_nodes()

    def number_of_edges(self):
        return self.model.number_of_edges()
        
    # -- about adding elements
    
    def add_nodes(self, nodes_count=1):
        first = 0 if self.number_of_nodes() == 0 else max(self.node_ids()) + 1
        for new_id in range(first, first+nodes_count):
            self.model.add_nodes_from([(new_id, {'g':self, 'view': NodeView(self.view, new_id)})])
            self.node_view(new_id).create()

    def add_edge(self, s1, s2, weight=None):
        self.model.add_edge(s1, s2, weight=weight, view=EdgeView(self.view, s1, s2, weight))
        self.edge_view(s1, s2).create()
    
    def add_edges_from(self, iterable=None):
        for s in iterable:
            s1, s2, *args = s
            self.add_edge(s1, s2, *args)
    
    # -- about removing elements

    def remove_node(self, node_id):
        if node_id in self.node_ids():
            self.model.remove_node(node_id)
            self.reset_view()
    
    def remove_nodes_from(self, iterable):
        self.model.remove_nodes_from(iterable)
        self.reset_view()

    def remove_edge(self, s1, s2):
        self.model.remove_edge(s1, s2)
        self.reset_view()
    
    def remove_edges_from(self, iterable):
        self.model.remove_edges_from(iterable)
        self.reset_view()
    
    def remove_random_edges(self, edges_count):
        edges_count = min(edges_count, self.number_of_edges())
        list_of_edges = list(self.edges())
        random.shuffle(list_of_edges)
        self.remove_edges_from(list_of_edges[:edges_count])
        
    # -- copy of graph
    
    def copy(self):
        nodes_count = self.number_of_nodes()
        g = Graph(nodes_count, engine=self.engine)
        g.add_edges_from(self.edges())    
        g.same_position_as(self)
        return g

    # -- load a complete json file graph description
    def load_json(self, filename, encoding='utf-8'):
        with open(filename, 'r', encoding=encoding) as jsonfile:
            properties = json.load(jsonfile)
        if 'nodes'  in properties:
            self.add_nodes(properties['nodes'])
        if 'edges' in properties:
            self.add_edges_from(properties['edges'])
        if 'labels' in properties:
            self.set_labels(properties['labels'])
            self.label_on()
        if 'position' in properties:
            self.position(properties['position'])
        if 'scale' in properties:
            self.scale(properties['scale'])

    # -- save a complete json file from graph
    def save_json(self, filename, encoding='utf-8'):
        try:
            to_unicode = unicode
        except NameError:
            to_unicode = str
        nodes, edges, positions, labels, ech = self.export_properties_json()
        data = {
        'nodes': nodes,
        'edges': edges,
        'labels' : labels,
        'position' : positions,
        'scale' : ech 
        }
        with io.open(filename, 'w', encoding='utf8') as outfile:
            str_ = json.dumps(data,
                            indent=4, sort_keys=True, ensure_ascii=False)
            outfile.write(to_unicode(str_))
                
    # -- other informations usefull for a lot of graphs algorithms
    
    def degree(self, node_id):
        return self.model.degree(node_id)
    
    def neighbors(self, node_id):
        return self.model.neighbors(node_id)
    
    
    # VIEW METHODS
    
    def node_view(self, node_id):
        return self.model.nodes[node_id]['view']
    
    def edge_view(self, node_src, node_dst):
        return self.model.edges[node_src, node_dst]['view']
    
    def init_view(self):
        self.init_nodes_view()
        self.init_edges_view()
        self.view_is_up_to_date = True
        
    def reset_view(self, engine=None, strict=False):
        engine = self.engine if engine is None else engine
        d_position = self.export_position()
        self.__view = gv.Graph(engine=engine, format='svg', strict=strict, node_attr={'fixedsize':'true', 'width':NODE_WIDTH, 'height':NODE_HEIGHT, 'margin':NODE_MARGIN})
        self.init_view()
        self.import_position(d_position)
        
    def init_nodes_view(self):
        for node_id in self.node_ids():
            self.model.nodes[node_id]['view'] = NodeView(self.view, node_id)
            self.node_view(node_id).create()

    def init_edges_view(self):
        for s1, s2 in self.edges():
            information = self.edge_informations(s1, s2)
            weight = information.get('weight', None)
            if s2 > s1:
                self.model.edges[s1, s2]['weight'] = weight
                self.model.edges[s1, s2]['view'] = EdgeView(self.view, s1, s2, weight)
                self.edge_view(s1, s2).create()
            
    # -- about nodes positionning and resizing
    
    def position(self, iterable, ech=1):
        for node_id, *pos in iterable:
            self.node_view(node_id).pos = pos
        self.scale(ech)
        
    def scale(self, ech=None):
        for node_id in self.node_ids():
            self.node_view(node_id).place(ech)
        
    def same_position_as(self, g):
        for node_id in g.node_ids():
            if node_id in self.node_ids():
                node_view = self.node_view(node_id) 
                node_view.pos = g.node_view(node_id).pos
                node_view.ech = g.node_view(node_id).ech
                node_view.place()

    def _rec_move(self, node_ids, seen, dx, dy):
        if node_ids:
            node_id = node_ids.pop()
            self.node_view(node_id).move(dx, dy)
            seen.add(node_id)
            for v_id in self.neighbors(node_id):
                if v_id not in seen:
                    node_ids.add(v_id)
                    self._rec_move(node_ids, seen, dx, dy)
                    
    def move(self, node_id, dx, dy, group=False):
        if group:
            self._rec_move({node_id}, set(), dx, dy)
        else:
            self.node_view(node_id).move(dx, dy)
        self.scale()
    
    def resize(self, *dim, node_id=None):
        if node_id is None:
            for node_id in self.node_ids():
                self.node_view(node_id).size(*dim)
                if float(self.node_view(node_id).width) < 0.25:
                    self.node_view(node_id).label_off()
                    self.node_view(node_id).label_on_side(self.node_view(node_id).label)
                else:
                    self.node_view(node_id).label_on(self.node_view(node_id).label)
                    self.node_view(node_id).label_off_side()
        else:
            self.node_view(node_id).size(*dim)
            if float(self.node_view(node_id).width) < 0.25:
                self.node_view(node_id).label_off()
                self.node_view(node_id).label_on_side(self.node_view(node_id).label)
            else:
                self.node_view(node_id).label_on(self.node_view(node_id).label)
                self.node_view(node_id).label_off_side()
            
    def export_position(self):
        lnodes = list(self.node_ids())
        d = {node_id:self.node_view(node_id).pos for node_id in self.node_ids()}
        d['ech'] = self.node_view(lnodes[0]).ech if lnodes else 1
        return d
    
    def export_properties_json(self):
        lnodes = list(self.node_ids())
        # Nodes 
        nodes = len(list(self.node_ids()))
        # Edges
        edges = []
        for i in self.edges():
            edges.append(list((i[0],i[1],self.edge_informations(i[0],i[1]).get('weight'))))
        d = {node_id:self.node_view(node_id).pos for node_id in self.node_ids()}
        # Positions 
        positions = []
        for node_id in self.node_ids():
            temp = []
            temp.append(node_id)
            temp.append(self.node_view(node_id).pos[0])
            temp.append(self.node_view(node_id).pos[1])
            positions.append(temp)
        # Labels
        labels = ""
        for node_id in self.node_ids():
            labels = labels + (self.node_view(node_id).label)
        labels
        # Scale
        ech = self.node_view(lnodes[0]).ech if lnodes else 1
        return nodes, edges, positions, labels, ech

    def import_position(self, d_position):
        ech = d_position['ech']
        for node_id in self.node_ids():
            if node_id in d_position:
                self.node_view(node_id).pos = d_position[node_id]
                self.node_view(node_id).place(ech)

    # -- about labels
    
    def set_labels(self, labels=None):
        """
        Change all nodes label with the str labels parameter
        if labels is None, reset all labels to nodes ids
        """
        if labels is None:
            for node_id in self.node_ids():
                self.node_view(node_id).label = str(node_id)   
        elif isinstance(labels, str):
            nodes_count = self.number_of_nodes()
            labels += NOLABEL * max(0, nodes_count - len(labels))
            for node_id in self.node_ids():
                self.node_view(node_id).label = labels[node_id]
    
    def label_on(self):
        for node_id in self.node_ids():
            self.node_view(node_id).label_on()

    def label_off(self):
        for node_id in self.node_ids():
            self.node_view(node_id).label_off()
    
    # -- about colors

    def color_on(self, *args):
        if len(args) == 2:
            node_id, color = args
            self.node_view(node_id).color_on(color)
        else:
            for node_id in self.node_ids():
                self.node_view(node_id).color_on()

    def color_off(self):
        for node_id in self.node_ids():
            self.node_view(node_id).color_off()
            
    def color_on_edge(self, *args):
        if len(args) == 3:
            node_src, node_dst, color = args
            self.edge_view(node_src, node_dst).color_on(color)
        else:
            for node_src, node_dst in self.edges():
                self.edge_view(node_src, node_dst).color_on()

    def color_off_edge(self):
        for node_src, node_dst in self.edges():
            self.edge_view(node_src, node_dst).color_off()
            
    # -- about attibutes
    
    def is_weighted(self):
        # Return true if the graph is ponderate
        return nx.is_weighted(self.model)
    
    def get_node_attributes(self, node_id):
        return nx.get_node_attributes(self.model, node_id)
    
    def print_graph_info(self):
        for node, info in self.model.adj.items():
            for voisin, info_lien in info.items(): 
                print(f"Lien [{node} et {voisin}] => poid {info_lien['weight']}")
        
    # -- write graph view in file
    
    def write(self, filename='output', format='svg', view = True):
        self.view.render(filename, format=format, view=view)

                    
class DiGraph(Graph):
    """
    class DiGraph modélise un graphe orienté. 
    
    Parameters:
    -----------
        nodes_count : int
            le nombre de sommets du graphe (par défaut 0)
        engine : str
            le moteur de rendu
    
    Note:
    -----
        Appel le constructeur de Graph avec directed=True
    """

    
    def __init__(self, nodes_count=0, engine='neato', strict=False):
        Graph.__init__(self, nodes_count, random=False, directed=True, strict=strict, engine=engine)
        
    def reset_view(self, engine=None, strict=False):
        engine = self.engine if engine is None else engine
        d_position = self.export_position()
        self.view = gv.Digraph(engine=engine, strict=strict, edge_attr={'arrowsize':ARROWSIZE}, node_attr={'fixedsize':'true', 'width':NODE_WIDTH, 'height':NODE_HEIGHT, 'margin':NODE_MARGIN})
        self.init_view()
        self.import_position(d_position)

    def init_edges_view(self):
        for s1, s2 in self.edges():
            informations = self.edge_informations(s1, s2)
            weight = informations.get('weight', None)
            self.model.edges[s1, s2]['weight'] = weight
            self.model.edges[s1, s2]['view'] = EdgeView(self.view, s1, s2, weight)
            self.edge_view(s1, s2).create()

    def copy(self):
        nodes_count = self.number_of_nodes()
        g = DiGraph(nodes_count, engine=self.engine)
        for s1, s2 in self.edges():
            informations = self.edge_informations(s1, s2)
            weight = informations.get('weight', None)
            g.add_edge(s1, s2, weight)    
        g.same_position_as(self)
        return g

    def degree(self, node_id):
        return len(self.neighbors(node_id))
    
    def neighbors(self, node_id):
        if self.is_weighted:
            neigh = self.model.neighbors(node_id)
        else:
            neigh = list(self.model.successors(node_id))
            neigh.extend(self.model.predecessors(node_id))
        return neigh

        
class BiPartite(Graph):
    """
    class BiPartite modélise un graphe bi-partie non orienté. 
    
    Parameters:
    -----------
        n1 : int
            le nombre de sommets d'une partie du graphe
        n2 : int
            le nombre de sommets de l'autre partie du graphe
        engine : str
            le moteur de rendu
    
    Note:
    -----
        Appel le constructeur de Graph avec nodes_count=n1+n2,directed=False, 
        random=False et bipartite=True
    """
    
    def __init__(self, n1, n2, engine='neato'):
        Graph.__init__(self, n1+n2, bipartite=True, n1=n1, n2=n2, engine=engine)
        self.n1 = n1
        self.n2 = n2
        
    def copy(self):
        nodes_count = self.number_of_nodes()
        g = Graph(nodes_count, bipartite=True, n1=self.n1, n2=self.n2, engine=self.engine)
        g.init_view()
        g.add_edges_from(self.edges())
        g.same_position_as(self)
        return g
