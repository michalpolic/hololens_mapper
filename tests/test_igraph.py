import pytest
from igraph import *

def test_graph_creation():
    g = Graph()
    g.add_vertices(3)
    g.add_edges([(0,1), (1,2), (0,2)])
    g.vs['label'] = ['img1','img2','img3']
    return g

def test_minimal_spanning_tree():
    g = test_graph_creation()
    st = g.spanning_tree(weights=[3, 2, 1])
    plot(st)

test_minimal_spanning_tree()
