"""
Heuristic functions and helper utilities for pathfinding.
"""

import math


def manhattan_distance(node1, node2):
    """
    Manhattan distance heuristic.
    
    Calculates the sum of absolute differences in x and y coordinates.
    Appropriate for 4-directional movement (no diagonals).
    
    Args:
        node1: First node
        node2: Second node
    
    Returns:
        Manhattan distance between the two nodes
    """
    return abs(node1.row - node2.row) + abs(node1.col - node2.col)


def euclidean_distance(node1, node2):
    """
    Euclidean distance heuristic.
    
    Calculates the straight-line distance between two points.
    Appropriate for 8-directional movement (with diagonals).
    
    Args:
        node1: First node
        node2: Second node
    
    Returns:
        Euclidean distance between the two nodes
    """
    return math.sqrt((node1.row - node2.row) ** 2 + (node1.col - node2.col) ** 2)


def chebyshev_distance(node1, node2):
    """
    Chebyshev distance heuristic.
    
    The maximum of absolute differences in x and y coordinates.
    Appropriate when diagonal movement costs 1 (8-directional).
    
    Args:
        node1: First node
        node2: Second node
    
    Returns:
        Chebyshev distance between the two nodes
    """
    return max(abs(node1.row - node2.row), abs(node1.col - node2.col))


def octile_distance(node1, node2):
    """
    Octile distance heuristic.
    
    Appropriate when diagonal movement costs sqrt(2).
    
    Args:
        node1: First node
        node2: Second node
    
    Returns:
        Octile distance between the two nodes
    """
    dx = abs(node1.col - node2.col)
    dy = abs(node1.row - node2.row)
    return max(dx, dy) + (math.sqrt(2) - 1) * min(dx, dy)


HEURISTICS = {
    'Manhattan': manhattan_distance,
    'Euclidean': euclidean_distance,
    'Chebyshev': chebyshev_distance,
    'Octile': octile_distance,
}


def get_heuristic(heuristic_name):
    """
    Get heuristic function by name.
    
    Args:
        heuristic_name: Name of the heuristic
    
    Returns:
        Heuristic function
    
    Raises:
        ValueError: If heuristic name is not found
    """
    if heuristic_name not in HEURISTICS:
        raise ValueError(f"Unknown heuristic: {heuristic_name}")
    return HEURISTICS[heuristic_name]


def get_cost(node1, node2, diagonal=False):
    """
    Get movement cost between two adjacent nodes.
    
    Args:
        node1: First node
        node2: Second node
        diagonal: Whether movement is diagonal
    
    Returns:
        Movement cost (1 for cardinal, sqrt(2) for diagonal)
    """
    if diagonal:
        dr = abs(node1.row - node2.row)
        dc = abs(node1.col - node2.col)
        if dr > 0 and dc > 0:
            return math.sqrt(2)
    return 1


def reconstruct_path(node):
    """
    Reconstruct path from goal node to start node.
    
    Args:
        node: Goal node or any node in the path
    
    Returns:
        List of nodes from start to goal
    """
    path = []
    current = node
    
    while current is not None:
        path.append(current)
        current = current.parent
    
    path.reverse()
    return path


def is_consistent(heuristic_func, diagonal=False):
    """
    Check if a heuristic is consistent (admissible and satisfies triangle inequality).
    
    A* with a consistent heuristic never re-opens nodes.
    
    Args:
        heuristic_func: The heuristic function to check
        diagonal: Whether diagonal movement is allowed
    
    Returns:
        True if consistent, False otherwise
    """
    return heuristic_func in [euclidean_distance, chebyshev_distance, octile_distance]


def weighted_f(g, h, weight):
    """
    Calculate weighted f-score for Weighted A*.
    
    f(n) = g(n) + w * h(n)
    
    Where w > 1 makes the search more greedy.
    
    Args:
        g: g-cost (actual cost from start)
        h: h-cost (heuristic estimate to goal)
        weight: Weight for heuristic (w >= 1)
    
    Returns:
        Weighted f-score
    """
    return g + weight * h
