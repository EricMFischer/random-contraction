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


# input: filename
# output: object with vertex keys and their neighbors
def preprocess_adj_list(filename):
    result = []
    with open(filename) as f_handle:
        for line in f_handle:
            result.append(line.split())
    return graph_obj(result)


# input: vertex arrays with a vertex followed by its neighbors
# output: object with vertex keys and their neighbors
def graph_obj(arr_vertices):
    graph = {}
    for v in arr_vertices:
        graph[v[0]] = v[1:]
    return graph


# input: object with vertex keys and their neighbors
# output: Graph instantiated with input graph object
def create_graph(graph_obj):
    G = Graph()
    for v_key in graph_obj:
        v = Vertex(v_key)
        for nbr_k in graph_obj[v_key]:
            v.add_nbr(nbr_k)
        G.add_v(v)
    return G


# Vertex class for undirected graphs
class Vertex():
    def __init__(self, key):
        self._key = key
        self._nbrs = {}

    def __str__(self):
        return '{' + "'key': {}, 'nbrs': {}".format(
            self._key,
            self._nbrs
        ) + '}'

    def add_nbr(self, nbr_key, weight=1):
        if (nbr_key):
            self._nbrs[nbr_key] = weight

    def has_nbr(self, nbr_key):
        return nbr_key in self._nbrs

    def get_nbr_keys(self):
        return list(self._nbrs.keys())

    def remove_nbr(self, nbr_key):
        if nbr_key in self._nbrs:
            del self._nbrs[nbr_key]

    def get_e(self, nbr_key):
        if nbr_key in self._nbrs:
            return self._nbrs[nbr_key]


# Undirected graph class
class Graph():
    def __init__(self):
        self._vertices = {}

    # 'x in graph' will use this containment logic
    def __contains__(self, key):
        return key in self._vertices

    # 'for x in graph' will use this iter() definition, where x is a vertex in an array
    def __iter__(self):
        return iter(self._vertices.values())

    def __str__(self):
        output = '\n{\n'
        vertices = self._vertices.values()
        for v in vertices:
            graph_key = "{}".format(v._key)
            v_str = "\n   'key': {}, \n   'nbrs': {}".format(
                v._key,
                v._nbrs
            )
            output += ' ' + graph_key + ': {' + v_str + '\n },\n'
        return output + '}'

    def add_v(self, v):
        if v:
            self._vertices[v._key] = v
        return self

    def get_v(self, key):
        try:
            return self._vertices[key]
        except KeyError:
            return None

    def get_v_keys(self):
        return list(self._vertices.keys())

    # removes vertex as neighbor from all its neighbors, then deletes vertex
    def remove_v(self, key):
        if key in self._vertices:
            nbr_keys = self._vertices[key].get_nbr_keys()
            for nbr_key in nbr_keys:
                self.remove_e(nbr_key, key)
            del self._vertices[key]

    def add_e(self, from_key, to_key, weight=1):
        if from_key not in self._vertices:
            self.add_v(Vertex(from_key))
        if to_key not in self._vertices:
            self.add_v(Vertex(to_key))

        self._vertices[from_key].add_nbr(to_key, weight)
        self._vertices[to_key].add_nbr(from_key, weight)

    def get_e(self, from_key, to_key):
        if from_key and to_key in self._vertices:
            return self.get_v(from_key).get_e(to_key)

    # adds the weight for an edge if it exists already, with a default of 1
    def increase_e(self, from_key, to_key, weight=1):
        if from_key not in self._vertices:
            self.add_v(Vertex(from_key))
        if to_key not in self._vertices:
            self.add_v(Vertex(to_key))

        weight_u_v = self.get_v(from_key).get_e(to_key)
        new_weight_u_v = weight_u_v + weight if weight_u_v else weight

        weight_v_u = self.get_v(to_key).get_e(from_key)
        new_weight_v_u = weight_v_u + weight if weight_v_u else weight

        self._vertices[from_key].add_nbr(to_key, new_weight_u_v)
        self._vertices[to_key].add_nbr(from_key, new_weight_v_u)

    def has_e(self, from_key, to_key):
        if from_key in self._vertices:
            return self._vertices[from_key].has_nbr(to_key)

    def remove_e(self, from_key, to_key):
        if from_key in self._vertices:
            self._vertices[from_key].remove_nbr(to_key)
        if to_key in self._vertices:
            self._vertices[to_key].remove_nbr(from_key)

    def for_each_v(self, cb):
        for v in self._vertices:
            cb(v)


# input: Graph object
# output: array of all its edges
def compile_edges(graph):
    edges = []
    v_keys = graph.get_v_keys()
    for v_k in v_keys:
        nbr_keys = graph.get_v(v_k).get_nbr_keys()
        for nbr_k in nbr_keys:
            edges.append([v_k, nbr_k])
    return edges


# input: Graph object, array of all its edges
# output: a random edge [u,v] that still exists in the graph
def choose_edge(graph, edges):
    random_e = random.choice(edges)
    u_key = random_e[0]
    v_key = random_e[1]
    while(not graph.has_e(u_key, v_key)):
        random_e = random.choice(edges)
        u_key = random_e[0]
        v_key = random_e[1]
    return random_e


# input: array of all edges, v_key to be removed
# output: array of all edges none of which contain v_key
def remove_vertex_from_edges(edges, v_key):
    for e in edges:
        # can exit iteration early if edges are sorted by edge[0], because v_key
        # will not be found again at edge[0] if larger. note it could be found at edge[1],
        # but exiting the for loop here has massive time benefits. and if we happen to choose
        # a random edge at some point that includes this v_key which no longer exists,
        # (because we exited this for loop without deleting the edges in which it was at
        # edge[1]), choose_edge will discard this edge from the edges list and continue until
        # it finds a random edge that exists
        if int(v_key) > int(e[0]):
            break
        if v_key in e:
            edges.remove(e)
    return edges


# input: Graph object of 2 vertices with an equal number of edges to each other
# output: number of edges between 2 vertices
def count_edges(graph):
    edges = 0
    v = graph.get_v(graph.get_v_keys()[0])
    nbr_keys = v.get_nbr_keys()
    for nbr_k in nbr_keys:
        edges += v.get_e(nbr_k)
    return edges


# input: object with vertex keys and their neighbors
# output: minimum cut overall
def record_min_cut(graph_object):
    num_vertices = len(list(graph_object.keys()))
    # n(n-1)/2 is maximum possible number of edges, and hence the inverse is the success
    # probability of picking the correct edge for the min cut on the 1st iteration
    best_min_cut = num_vertices * (num_vertices - 1) / 2
    print('best_min_cut to start:', best_min_cut)
    # iters = n^2 (rough reciprocal of success probability on 1st iteration) * ln(n)
    # iters = int(num_vertices**2 * math.log(num_vertices))
    iters = 1000
    for i in range(iters):
        G = create_graph(graph_object)
        min_cut = random_contraction(G)
        print('min_cut:', min_cut)
        if min_cut < best_min_cut:
            best_min_cut = min_cut
            print('best_min_cut:', best_min_cut)
    return best_min_cut


# input: Graph object
# output: minimum cut of graph
def random_contraction(G):
    edges = compile_edges(G)
    while len(G.get_v_keys()) > 2:
        random_e = choose_edge(G, edges)
        u_k = random_e[0]
        v_k = random_e[1]
        u = G.get_v(u_k)
        v = G.get_v(v_k)

        # Merge or contract u and v into a single vertex u (3 steps)
        # To prepare to delete v:
        # 1) for each v_nbr, a) add it to the neighbors of u, and b) add u to its neighbors
        v_nbr_keys = v.get_nbr_keys()
        for v_nbr_k in v_nbr_keys:
            # a) add v_nbr and u as neighbors to each other with edge = v,v_nbr edge
            # (Note: self-loop created here when we eventually add u (also a v_nbr) as a
            # neighbor to itself, but it is removed in step 3)
            v_v_nbr_edge = v.get_e(v_nbr_k)
            G.increase_e(u_k, v_nbr_k, v_v_nbr_edge)
            # append the new edges formed to list of edges
            edges.append([u_k, v_nbr_k])
            edges.append([v_nbr_k, u_k])

        G.add_v(u)
        # 2) remove v from G, which removes it as anyones neighbor and deletes it
        # (remove from edges the edges v shared with neighbors and vice-versa)
        G.remove_v(v_k)
        edges = remove_vertex_from_edges(edges, v_k)
        # 3) remove self-loop added in step 1a. u should not have itself listed in its neighbors
        G.remove_e(u_k, u_k)

    # return edges between final 2 vertices (will be equal for each vertex)
    return count_edges(G)


graph_object = preprocess_adj_list('random_contraction.txt')
pprint.pprint(graph_object, width=260)

start = time.time()
best_min_cut = record_min_cut(graph_object)
print('final best min cut:', best_min_cut)
print('elapsed time:', time.time() - start)
