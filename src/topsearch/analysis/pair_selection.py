""" Routines that act on a KineticTransitionNetwork object to select pairs 
    of minima for sampling by different criteria """

import logging
import numpy as np
import networkx as nx
from topsearch.data.coordinates import StandardCoordinates

from topsearch.data.kinetic_transition_network import KineticTransitionNetwork
from topsearch.similarity.similarity import StandardSimilarity
from .graph_properties import unconnected_component
from .minima_properties import get_distance_matrix, get_distance_from_minimum
logger = logging.getLogger()

def connect_unconnected(ktn: KineticTransitionNetwork, similarity: StandardSimilarity,
                        coords: StandardCoordinates, neighbours: int) -> list:
    """
    Find all minima not connected to global minimum set and their nearest
    neighbours. Return the list of minima pairs
    """
    # Check for emptiness
    if ktn.n_minima == 0:
        return []
    # Get the set of minima not connected to the global minimum
    unconnected_set = unconnected_component(ktn)
    total_pairs = []
    if len(unconnected_set) > 0:
        for i in unconnected_set:
            pairs = connect_to_set(ktn, similarity, coords, i, neighbours)
            for j in pairs:
                total_pairs.append(j)
    # Can generate a lot of repeats so remove any repeated pairs
    total_pairs = unique_pairs(total_pairs)
    return total_pairs


def connect_to_set(ktn: KineticTransitionNetwork, similarity: StandardSimilarity, coords: StandardCoordinates,
                   node1: int, cycles: int) -> list:
    """
    Finds all minima connected to node1 and finds the pairs closest
    in distance where one is connected and one is not. Returns the
    set of minima pairs in a list for use in connect_unconnected
    """

    # Set of nodes connected to node1
    s_set = nx.node_connected_component(ktn.G, node1)
    # Find list of nodes not connected to node 1
    f_set = set(range(ktn.n_minima)) - set(s_set)
    if f_set == set():
        logger.info("No unconnected minima\n")
        return []
    # Get ordered distances to this node
    dist_vector = get_distance_from_minimum(ktn, similarity, coords, node1)
    nearest = np.argsort(dist_vector).tolist()[1:]
    # Remove any minima in same set
    pairs = [i for i in nearest if i in f_set]
    total_pairs = []
    for i in pairs[:cycles]:
        total_pairs.append([node1, i])
    return unique_pairs(total_pairs)


def closest_enumeration(ktn: KineticTransitionNetwork, similarity: StandardSimilarity,
                        coords: StandardCoordinates, neighbours: int) -> list:
    """
    Selector that attempts to connect all minima in the fewest number of
    attempts by connecting each minimum to its N nearest neighbours.
    Returns a list of pairs
    """
    pairs = []
    dist_matrix = get_distance_matrix(ktn, similarity, coords)
    for i in range(ktn.n_minima):
        nearest = np.argsort(dist_matrix[i, :]).tolist()[1:neighbours+1]
        for j in nearest:
            pairs.append([i, j])
    return unique_pairs(pairs)


def read_pairs(text_path: str = ''):
    """ Read the set of pairs from the file pairs.txt """
    pairs = np.genfromtxt(f'{text_path}pairs.txt', dtype=int)
    return unique_pairs(pairs.tolist())


def unique_pairs(initial_pairs: list) -> list:
    """ Remove any repeated pairs from a given list """
    # Sort the pairs as [0, 1] and [1, 0] are equivalent
    final_pairs = [tuple(sorted(i)) for i in initial_pairs if i != [0, 0]]
    return [list(i) for i in set(final_pairs)]
