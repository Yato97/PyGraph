from queue import PriorityQueue
from constantes import *
import os
from tkinter import Tk, filedialog
import shutil
import graphviz as gv
from math import inf
import networkx as nx

class Dijkstra:
    """
    class Dijkstra
        
    Parameters:
    -----------
        Graph : Graph
            le graphe sur lequel on applique l'algorithme
        start : int
            le nœud de départ 
        end : int
            le nœud de destination
        solved : bool
            un flag pour savoir si la résolution du plus court chemin est achevé
        selected : node_id
            position du nœud actuelle
        shortest_path : list
            la liste des node_id du chemin le plus court 
        dist : dict
            dictionnaire contenant les clés: valeurs suivantes node_id: distance from start 
        pred : dict
            dictionnaire contenant les clés: valeurs suivantes node_id: son prédécesseur 
        visited : collection set
            collection des nœud visité   
        locked : collection set
            collection des nœuds verrouillés      
    
    Note:
    -----
        Les autres paramètres ne devraient pas être utilisés : ils servent à l'exécution de l'algorithme.
    """
    
    def __init__(self, graph, start=0, end=None, inside=True):
        self.__graph = graph # Graphe 
        self.__start = start # Nœud de départ
        self.__end = end if end is not None else max(graph.node_ids()) # Nœud de destination
        self.__solved = False # Flag
        self.__shortest_path = list() # Path to use
        self.__dist = {} # Distances
        self.__pred = {} # Prédécesseurs
        self.__visited = set() # Nœud visité
        self.__locked = set() # Nœuds verrouillés
        self.__selected = self.__start
        self.__temp = set() # Tool for neighboor
        self.__first_step = True
        self.__priority_queue = PriorityQueue()
        self.__inside = inside
        self.init_dijkstra()
   
    # +++++GET/SET+++++ #
    
    @property
    def graph(self):
        return self.__graph
    
    @property
    def temp(self):
        return self.__temp

    @graph.setter
    def graph(self, graph):
        self.__graph = graph

    @property
    def start(self):
        return self.__start

    @start.setter
    def start(self, start):
        self.__start = start
        
    @property
    def end(self):
        return self.__end

    @end.setter
    def end(self, end):
        self.__end = end

    @property
    def solved(self):
        return self.__solved        
    
    
    # +++++TOOLS+++++ #    
    def view(self):
        return self.graph.view
    
    def show_shortest_path(self):
        # Show the shortest path without other path
        Gtemp = self.graph.copy()
        nodeList = list(self.graph.model.nodes)
        res = list(self.graph.model.nodes)
        for i in range(len(nodeList)):
            for x in range(len(self.__shortest_path)):
                if nodeList[i] == self.__shortest_path[x]:
                    res.remove(self.__shortest_path[x])
        for i in range(len(res)):
            Gtemp.remove_node(res[i])
        return Gtemp.view
    
    def make_section(self, title, img):
        h1 = f"<div id=container_title><h1>{title}</h1></div>"
        img = f"<img src='{img}'>"
        inner_body = f"<div class='slide'>{h1}{img}</div>"
        return inner_body
    
    def diaporama(self, filename="index"):
        header = "<html>\n<head>\n<title>Dijkstra</title>\n<link rel='stylesheet' href='css/css.css'>\n</head>\n<body>\n<div class='diapo'>\n<div class='elements'>"
        footer = "</div><img src=img/left.svg id='nav-gauche'>\n\
                  <img src=img/right.svg id='nav-droite'></div>\n<script src='js/script.js'></script></body>\n</html>"
        html = ""
        
        root = Tk() 
        root.withdraw() 
        root.attributes('-topmost', True) 
        open_file = filedialog.askdirectory() 
        directory = os.getcwd()
        
        filename = open_file+"/exported/"+filename + ".html"
        if not os.path.exists(open_file+"/exported/css"):
            os.makedirs(open_file+"/exported/css")
        if not os.path.exists(open_file+"/exported/js"):
            os.makedirs(open_file+"/exported/js")
        i = 0
            
        while self.__solved != True:
            self.next()
            self.__graph.write(open_file+"/exported/img/"+str(i), view=False)
            if os.path.exists(str(i)):
                os.remove(str(i))
            header += self.make_section("Step : "+str(i), str(open_file+"/exported/img/"+str(i)+".svg"))
            i += 1
        if self.__solved:
            self.dijkstra_path()
            self.color_dijkstra_path()
            self.__graph.write(open_file+"/exported/img/"+str(i), view=False)
            header += self.make_section("Step : "+str(i), str(open_file+"/exported/img/"+str(i)+".svg"))
        shutil.copyfile(directory +'/res/left.svg', open_file+"/exported/img/"+"left.svg")
        shutil.copyfile(directory +'/res/right.svg', open_file+"/exported/img/"+"right.svg")
        shutil.copyfile(directory +'/res/css.css', open_file+"/exported/css/"+"css.css")
        shutil.copyfile(directory +'/res/script.js', open_file+"/exported/js/"+"script.js")
        html = html+header+footer
        page = open(filename,"w")
        page.write(html)                    
        page.close()
        
    # +++++TOOLS+++++ #   
    
    # +++++NETWORKX+++++ #               
    def path(self, src_node_id, dst_node_id):
        # Dijkstra : shortest weighted path, by networkx
        return nx.dijkstra_path(self.graph.model, src_node_id, dst_node_id)

    def path_length(self, src_node_id, dst_node_id):
        # Dijkstra : Distance between 2 entry node : start , end, by networkx
        return nx.dijkstra_path_length(self.graph.model, src_node_id, dst_node_id)
    
    def distance_nx(self, dst_node_id):
        # Dijkstra : Distance between start and an entry node, by networkx
        return nx.dijkstra_path_length(self.graph.model, self.start, dst_node_id)
    
    def distance(self, dst_node_id):
        return self.__dist[dst_node_id]
    
    def shortest_cost(self):
        # Dijkstra : Lenght of the shortest path by networkx
        return nx.dijkstra_path_length(self.graph.model, self.start, self.end)
    # +++++NETWORKX+++++ #    
    
        
    # ------------------------Dijkstra---------------------# 
    
    # +++++INIT+++++ #
    def init_dijkstra(self):
        self.__pred = {}  # Predecessor of the current node pos
        self.__dist = {node_id: inf for node_id in self.graph.node_ids()} # Init all nodes dist to inf except the source_node
        self.__dist[self.start] = 0  # dist from start -> start is zero
        self.__priority_queue.put((self.__dist[self.start], self.start))
        self.__selected = self.__start
        self.graph.color_on(self.start, 3)
        self.graph.resize(0.45)
        # Labelise all node 
        stre = str()
        for i in LETTERS:
            if len(stre) <= self.graph.number_of_nodes():
                stre += i
        self.graph.set_labels(stre)
        self.graph.label_on()
        print(self.__dist)
    # +++++INIT+++++ #
    
    # +++++TOOLS+++++ #
    def dijkstra_path(self):
        pos = self.end
        while pos != self.start:
            self.__shortest_path.append(pos)
            pos = self.__pred[pos]
        self.__shortest_path.append(pos) 
        return self.__shortest_path
    
    def color_dijkstra_path(self):
        self.graph.color_off()
        for i in range(len(self.__shortest_path)):
            if i == 0:
                self.graph.color_on(self.__shortest_path[i], 3)
            elif i >= (len(self.__shortest_path)-1):
                self.graph.color_on(self.__shortest_path[i], 5)
            else :
                self.graph.color_on(self.__shortest_path[i], 2)
    
    def cost_between(self, start, end):
        # Return :Weight between 2 nodes
        return self.graph.edge_view(start, end).weight
    
    def reset_dijkstra(self):
        # Reset dijkstra & view
        self.graph.reset_view()
        self.__step = False
        self.__solved = False
        self.__step_by_step = False
        self.__shortest_path = list() # Path to use
        self.__dist = None
        self.__pred = None
        self.__selected = None
        self.__first_step = True
        self.__visited = set()
        self.__locked = set()
        self.__priority_queue = PriorityQueue() 
        self.init_dijkstra()
    # +++++TOOLS+++++ #
    
    def dijkstra_step(self):
        # Dijkstra :step , Found the best path, save attributes{dist, pred, visited, shortest_path}
            pos_weight, pos = self.__priority_queue.get()
            self.__selected = pos
            for neighbor in self.graph.neighbors(pos):
                if neighbor not in self.__locked:
                    path = pos_weight + self.cost_between(pos, neighbor)
                    if path < self.__dist[neighbor]:
                        self.__dist[neighbor] = path
                        self.__pred[neighbor] = pos
                        if neighbor not in self.__visited:  
                            for i in range(len(self.__priority_queue.queue)):
                                if self.__priority_queue.queue[i][1] == neighbor:
                                    self.__priority_queue.queue.pop(i)
                            self.__priority_queue.put((self.__dist[neighbor], neighbor))
                        else:
                            self.__priority_queue.get((self.__dist[neighbor], neighbor))
                            self.__visited.add(neighbor)
                        string = f"{self.graph.node_view(pos).label}{path}"
                        if self.__inside:
                            string += f'{pos}'
                            self.graph.node_view(neighbor).label_on(string, COLORS[FIREBRICK])
                        else:
                            self.graph.node_view(neighbor).label_on_side(string, COLORS[FIREBRICK])
            self.__locked.add(self.__selected)
            if self.__priority_queue.qsize() == 0 or self.end in self.__locked:
                self.__solved = True
            return self.show_shortest_path()
              
    def solve(self):
        # Dijkstra :main
        while not self.solved:
            self.dijkstra_step()
                        
        if self.solved:
            self.dijkstra_path()
            self.color_dijkstra_path()
        return self.view()
    # ------------------------Dijkstra---------------------#  
    
    def next(self):
        if self.solved:
            print('Dijkstra résolu')
            self.dijkstra_path()
            self.color_dijkstra_path()
            return self.view()
        elif self.__first_step:
            self.__first_step = False
            self.graph.color_on(self.__selected, SELECTED_NODE_COLOR)
            return self.view()
        else:
            for s in self.__temp:
                self.graph.color_on(s, -1)
            self.__temp = set()
            for s in self.__visited:
                self.graph.color_on(s, -1)
            for s in self.__locked:
                self.graph.color_on(s, LOCKED_NODE_COLOR)
            pos_weight, pos = self.__priority_queue.get()
            self.__selected = pos
            self.__visited.add(pos)
            self.graph.color_on(pos, SELECTED_NODE_COLOR)
            for neighbor in self.graph.neighbors(pos):
                if neighbor not in self.__locked:
                    self.graph.color_on(neighbor, NEIGHBOR_COLOR)   
                    self.__temp.add(neighbor)          
                    path = pos_weight + self.cost_between(pos, neighbor)
                    string = f"{self.graph.node_view(pos).label}{path}"
                    if path < self.__dist[neighbor]:
                        self.__dist[neighbor] = path
                        self.__pred[neighbor] = pos
                        if neighbor not in self.__visited:  
                            for i in range(len(self.__priority_queue.queue)):
                                if self.__priority_queue.queue[i][1] == neighbor:
                                    self.__priority_queue.queue.pop(i)
                            self.__priority_queue.put((self.__dist[neighbor], neighbor))
                        else:
                            self.__priority_queue.get((self.__dist[neighbor], neighbor))
                            self.__visited.add(neighbor)
                        if self.__inside:
                            string += f'{LETTERS[neighbor]}'
                            self.graph.node_view(neighbor).label_on(string, COLORS[FIREBRICK])
                        else:
                            self.graph.node_view(neighbor).label_on_side(string, COLORS[FIREBRICK])
            self.__locked.add(self.__selected)
            if self.__priority_queue.qsize() == 0 or self.end in self.__locked:
                self.__solved = True
                
            return self.view()
