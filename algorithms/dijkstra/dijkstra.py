class Dijkstra(Graph):
    # Dijkstra object take a Graph, source node, destination node as parameters
    def __init__(self, Graph, node_id_src, node_id_dst):
        self.__Graph = Graph
        self.__node_id_src = node_id_src
        self.__node_id_dst = node_id_dst
        self.__step = 0
        self.auto = False
        self.iterable = self.path(node_id_src, node_id_dst) # Path to use
    
    @property
    def Graph(self):
        return self.__Graph

    @Graph.setter
    def Graph(self, Graph):
        self.__Graph = Graph
        
    @property
    def node_id_src(self):
        return self.__node_id_src

    @node_id_src.setter
    def node_id_src(self, node_id_src):
        self.__node_id_src = node_id_src
        
    @property
    def node_id_dst(self):
        return self.__node_id_dst

    @node_id_dst.setter
    def node_id_dst(self, node_id_dst):
        self.__node_id_dst = node_id_dst
        
    @property
    def step(self):
        return self.__step

    @step.setter
    def step(self, step):
        self.__step = step
        
        
    def view(self):
        return self.Graph.view
    
    def show_shortest_path(self):
        # Show the shortest path without other path :  (iterable => shortest path)
        # ATM work only on unweighted Graph because of copy()
        Gtemp = self.Graph.copy()
        nodeList = list(self.Graph.model.nodes)
        res = list(self.Graph.model.nodes)
        for i in range(len(nodeList)):
            for x in range(len(self.iterable)):
                if nodeList[i] == self.iterable[x]:
                    res.remove(self.iterable[x])
        for i in range(len(res)):
            Gtemp.remove_node(res[i])
        
        return Gtemp.view
                
    def path(self, src_node_id, dst_node_id):
        # dijkstra shortest weighted path
        return nx.dijkstra_path(self.Graph.model, src_node_id, dst_node_id)

    def path_length(self, src_node_id, dst_node_id):
        # Dijkstra : Amount of the length(shortest path)
        return nx.dijkstra_path_length(self.Graph.model, src_node_id, dst_node_id)
    
    def colorise_shortest_path(self, auto=True):
        # Colorise the shortest path : (green = srx, dst) (iterable => shortest path)
        # If you want to make it step by step add an arg : (bool : False) on the method
        if auto == True:
            self.auto = True
            for i in range(len(self.iterable)):
                if i == 0:
                    self.Graph.color_on(self.iterable[i], 3)
                elif i >= (len(self.iterable)-1):
                    self.Graph.color_on(self.iterable[i], 3)
                else :
                    self.Graph.color_on(self.iterable[i], 2)
        else:
            self.auto = False
            if self.step == 0:
                self.Graph.color_on(self.iterable[self.step], 3)
            elif self.step >= (len(self.iterable)-1):
                self.Graph.color_on(self.iterable[self.step], 3)
            else :
                self.Graph.color_on(self.iterable[self.step], 2)
        return self.view()
            
    
    def next_step(self):
        if self.auto == False:
            self.step+=1
            self.colorise_shortest_path(auto=False)
        return self.view()
    
    def reset_view(self):
        # Does not work properly because of weight
        self.Graph.reset_view()
        self.step = 0
    