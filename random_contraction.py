'''
A file contains the adjacency list representation of a simple undirected graph. There are
200 vertices labeled 1 to 200. The first column in the file represents the vertex label, and
the particular row (other entries except the first column) tells all the vertices that the
vertex is adjacent to. So for example, the 6th row looks like : "6  155 56  52  120 ......".
This just means that the vertex with label 6 is adjacent to (i.e., shares an edge with)
the vertices with labels 155,56,52,120,......,etc

Your task is to code up and run the randomized contraction algorithm for the min cut problem
and use it on the above graph to compute the min cut (e.g. 5) (HINT: Note that you'll have
to figure out an implementation of edge contractions. Initially, you might want to do this
naively, creating a new graph from the old every time there's an edge contraction. But you should
also think about more efficient implementations.) (WARNING: As per the video lectures, please
make sure to run the algorithm many times with different random seeds, and remember the
smallest cut that you ever find.) Write your numeric answer in the space provided. So e.g.,
if your answer is 5, just type 5 in the space provided.

'''
import pprint
import random
import math
import time


# input: file name
# output: object with vertex keys as keys and their neighbors as values
def preprocess_adj_list(filename):
    f = open(filename, 'r')
    vtxStrs = f.read().splitlines()
    f.close()

    result = []
    for idx, val in enumerate(vtxStrs):
        result.append(val.split())

    return graph_obj(result)


# input: vertex arrays, each w/ a vertex followed by its neighbors
# output: object with vertex keys as keys and their neighbors as values
def graph_obj(arr_vertices):
    graph = {}
    for idx, val in enumerate(arr_vertices):
        graph[val[0]] = val[1:]
    return graph


# input: object with vertex keys as keys and their neighbors as values
# output: Graph object instantiated with input graph object
def create_graph(graph_obj):
    graph = Graph()
    for vertex_key in graph_obj:
        vertex = Vertex(vertex_key)
        for neighbor_key in graph_obj[vertex_key]:
            vertex.add_neighbor(neighbor_key)
        graph.add_vertex(vertex)
    return graph


# Vertex class (vertices are objects with 'key' and 'neighbors' keys)
# Modifying these Vertex objects can make the graph more robust
class Vertex(object):
    def __init__(self, key):
        self.key = key
        self.neighbors = {}

    def __str__(self):
        return '{' + "'key': '{}', 'neighbors': {}".format(
            self.key,
            self.neighbors
        ) + '}'

    def add_neighbor(self, neighbor_key, weight=1):
        if (neighbor_key):
            self.neighbors[neighbor_key] = weight

    def has_neighbor(self, neighbor_key):
        return neighbor_key in self.neighbors

    def get_neighbor_keys(self):
        return list(self.neighbors.keys())

    def remove_neighbor(self, neighbor_key):
        if neighbor_key in self.neighbors:
            del self.neighbors[neighbor_key]

    def get_weight(self, neighbor_key):
        if neighbor_key in self.neighbors:
            return self.neighbors[neighbor_key]


# Graph class
# Note: to maximize applications, add_edge, increase_edge, and remove_edge only add or remove an
# edge for the 'from' vertex, and 'has_edge' only checks the 'from' vertex.
class Graph(object):
    def __init__(self):
        self.vertices = {}

    # 'x in graph' will use this containment logic
    def __contains__(self, key):
        return key in self.vertices

    # 'for x in graph' will use this iter() definition, where x is a vertex in an array
    def __iter__(self):
        return iter(self.vertices.values())

    def __str__(self):
        output = '\n{\n'
        vertices = self.vertices.values()
        for vertex in vertices:
            graph_key = "'{}'".format(vertex.key)
            vertex_str = "\n   'key': '{}', \n   'neighbors': {}".format(
                vertex.key,
                vertex.neighbors
            )
            output += ' ' + graph_key + ': {' + vertex_str + '\n },\n'
        return output + '}'

    def add_vertex(self, vertex):
        if vertex:
            self.vertices[vertex.key] = vertex
        # temporary logic
        return self

    def get_vertex(self, key):
        try:
            return self.vertices[key]
        except KeyError:
            return None

    def get_vertices_keys(self):
        return list(self.vertices.keys())

    # removes vertex as neighbor from all its neighbors, then deletes vertex
    def remove_vertex(self, key):
        if key in self.vertices:
            neighbor_keys = self.vertices[key].get_neighbor_keys()
            for neighbor_key in neighbor_keys:
                self.remove_edge(neighbor_key, key)
            del self.vertices[key]
        # temporary logic
        return self

    # overwrites the weight for an edge if it exists already, with a default of 1
    def add_edge(self, from_key, to_key, weight=1):
        if from_key not in self.vertices:
            self.add_vertex(Vertex(from_key))
        if to_key not in self.vertices:
            self.add_vertex(Vertex(to_key))

        self.vertices[from_key].add_neighbor(to_key, weight)

    # adds the weight for an edge if it exists already, with a default of 1
    def increase_edge(self, from_key, to_key, weight=1):
        if from_key not in self.vertices:
            self.add_vertex(Vertex(from_key))
        if to_key not in self.vertices:
            self.add_vertex(Vertex(to_key))

        weight_v1_v2 = self.get_vertex(from_key).get_weight(to_key)
        new_weight_v1_v2 = weight_v1_v2 + weight if weight_v1_v2 else weight

        self.vertices[from_key].add_neighbor(to_key, new_weight_v1_v2)
        # temporary logic
        return self

    def has_edge(self, from_key, to_key):
        if from_key in self.vertices:
            return self.vertices[from_key].has_neighbor(to_key)

    def remove_edge(self, from_key, to_key):
        if from_key in self.vertices:
            self.vertices[from_key].remove_neighbor(to_key)

    def for_each_vertex(self, cb):
        for vertex in self.vertices:
            cb(vertex)


# input: Graph object
# output: array of all its edges
def compile_edges(graph):
    edges = []
    vertex_keys = graph.get_vertices_keys()
    for vertex_key in vertex_keys:
        neighbor_keys = graph.get_vertex(vertex_key).get_neighbor_keys()
        for neighbor_key in neighbor_keys:
            edges.append([vertex_key, neighbor_key])
    return edges


# input: Graph object, array of all its edges
# output: a random edge [v1,v2] that still exists in the graph
def choose_edge(graph, edges):
    random_edge = random.choice(edges)
    v1_key = random_edge[0]
    v2_key = random_edge[1]
    while(not graph.has_edge(v1_key, v2_key)):
        random_edge = random.choice(edges)
        v1_key = random_edge[0]
        v2_key = random_edge[1]
    return random_edge


# input: array of all edges, vertex_key to be removed
# output: array of all edges none of which contain vertex_key
def remove_vertex_from_edges(edges, vertex_key):
    for edge in edges:
        # can exit iteration early if edges are sorted by edge[0], because vertex_key
        # will not be found again at edge[0] if larger. note it could be found at edge[1],
        # but exiting the for loop here has massive time benefits. and if we happen to choose
        # a random edge at some point that includes this vertex_key which no longer exists,
        # (because we exited this for loop without deleting the edges in which it was at
        # edge[1]), choose_edge will discard this edge from the edges list and continue until
        # it finds a random edge that exists
        if int(vertex_key) > int(edge[0]):
            break
        if vertex_key in edge:
            edges.remove(edge)
    return edges


# input: Graph object of 2 vertices with an equal number of edges to each other
# output: number of edges between 2 vertices
def count_edges(graph):
    edges = 0
    vertex = graph.get_vertex(graph.get_vertices_keys()[0])
    neighbor_keys = vertex.get_neighbor_keys()
    for neighbor_key in neighbor_keys:
        edges += vertex.get_weight(neighbor_key)
    return edges


# input: object with vertex keys as keys and their neighbors as values
# output: minimum cut overall
def record_min_cut(graph_object):
    num_vertices = len(list(graph_object.keys()))
    # n(n-1)/2 is maximum possible number of edges, and hence the inverse is the success
    # probability of picking the correct edge for the min cut on the 1st iteration
    best_min_cut = num_vertices * (num_vertices - 1) / 2
    print('best_min_cut to start:', best_min_cut)
    # iterations = n^2 (rough reciprocal of success probability on 1st iteration) * ln(n)
    # iterations = int(num_vertices**2 * math.log(num_vertices))
    iterations = 1000
    for i in range(iterations):
        graph = create_graph(graph_object)
        min_cut = random_contraction(graph)
        print('min_cut:', min_cut)
        if min_cut < best_min_cut:
            best_min_cut = min_cut
            print('best_min_cut:', best_min_cut)
    return best_min_cut


# input: Graph object
# output: minimum cut of graph
def random_contraction(graph):
    edges = compile_edges(graph)
    while len(graph.get_vertices_keys()) > 2:
        random_edge = choose_edge(graph, edges)
        v1_key = random_edge[0]
        v2_key = random_edge[1]
        v1 = graph.get_vertex(v1_key)
        v2 = graph.get_vertex(v2_key)

        # Merge or contract v1 and v2 into a single vertex v1 (3 steps)
        # To prepare to delete v2:
        # 1) for each v2_nbr, a) add it to the neighbors of v1, and b) add v1 to its neighbors
        v2_nbr_keys = v2.get_neighbor_keys()
        for v2_nbr_key in v2_nbr_keys:
            # a) add v2_nbr to neighbors of v1, with an edge weight = [v2,v2_nbr] edge weight
            # (Note: self-loop created here when we eventually add v1 (also a v2_nbr) as a
            # neighbor to itself, but it is removed in step 3)
            weight_v2_v2_nbr = v2.get_weight(v2_nbr_key)
            graph.increase_edge(v1_key, v2_nbr_key, weight_v2_v2_nbr)
            # b) add v1 to neighbors of v2_nbr, with a [v2_nbr,v1] edge weight = same
            # [v1,v2_nbr] edge weight just added
            graph.increase_edge(v2_nbr_key, v1_key, weight_v2_v2_nbr)
            # append the new edges formed to list of edges
            edges.append([v1_key, v2_nbr_key])
            edges.append([v2_nbr_key, v1_key])
            graph.add_vertex(graph.get_vertex(v2_nbr_key))

        graph.add_vertex(v1)
        # 2) remove v2 from graph, which removes it as anyones neighbor and deletes it
        # (remove from edges the edges v2 shared with neighbors and vice-versa)
        graph.remove_vertex(v2_key)
        edges = remove_vertex_from_edges(edges, v2_key)
        # 3) remove self-loop added in step 1a. v1 should not have itself listed in its neighbors
        graph.remove_edge(v1_key, v1_key)

    # return edges between final 2 vertices (will be equal for each vertex)
    return count_edges(graph)


# graph_object = {
#     'a': {'b': 0, 'c': 0},
#     'b': {'a': 0, 'c': 0, 'd': 0},
#     'c': {'a': 0, 'b': 0, 'd': 0},
#     'd': {'b': 0, 'c': 0}
# }
graph_object = preprocess_adj_list('random_contraction.txt')
pprint.pprint(graph_object, width=260)

start = time.time()
best_min_cut = record_min_cut(graph_object)
print('final best min cut:', best_min_cut)
end = time.time()
print('seconds:', end - start)

# Play area:
# p_graph = Graph()
# p_graph.add_vertex(Vertex('apples'))
# p_graph.add_vertex(Vertex('kittens'))
# p_graph.add_edge('apples', 'kittens')
# dogs = Vertex('dogs')
# dogs.add_neighbor('puppies')
# dogs.remove_neighbor('puppies')
# print(p_graph)
# print(p_graph.has_edge('apples', 'wolf'))
# p_graph.add_edge('puppies', 'apples')
# p_graph.add_edge('apples', 'puppies')
# p_graph.add_edge('apples', 'kittens')
# p_graph.add_edge('kittens', 'apples')
# p_graph.add_edge('indiana', 'california')
# p_graph.add_edge('california', 'indiana')
# p_graph.remove_edge('indiana', 'california')
# print('graph: ', p_graph)
# p_graph.remove_vertex('puppies')
# print('graph: ', p_graph)
