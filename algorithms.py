"""
Pathfinding algorithms: Greedy Best-First Search and A*.

Theory Notes:
- GBFS: f(n) = h(n). Not optimal but fast. Uses strict visited list.
- A*: f(n) = g(n) + h(n). Optimal if heuristic is admissible.
- A* may re-open nodes if heuristic is not consistent.
- Strict visited breaks UCS/A* because we might find better paths later.
"""

import heapq
import time
from config import NODE_STATES
from utils import get_heuristic, get_cost


class SearchResult:
    """Container for search algorithm results."""
    
    def __init__(self, success, path, nodes_expanded, execution_time, frontier_nodes=None):
        self.success = success
        self.path = path
        self.nodes_expanded = nodes_expanded
        self.execution_time = execution_time
        self.frontier_nodes = frontier_nodes or []


def greedy_best_first_search(grid, start, goal, heuristic_name, diagonal=False):
    """
    Greedy Best-First Search (GBFS) implementation.
    
    f(n) = h(n) - expands nodes with lowest heuristic first.
    
    Properties:
    - Not optimal (may not find shortest path)
    - Complete in finite spaces
    - Uses STRICT visited list (no re-opening)
    - Fast but sacrifices optimality
    
    Args:
        grid: Grid object
        start: Start node
        goal: Goal node
        heuristic_name: Name of heuristic to use
        diagonal: Whether to allow diagonal movement
    
    Returns:
        SearchResult object with path and metrics
    """
    start_time = time.time()
    
    heuristic = get_heuristic(heuristic_name)
    
    grid.reset_search_visualization()
    
    if not start or not goal:
        return SearchResult(False, [], 0, 0)
    
    open_set = []
    closed_set = set()
    
    start.g_cost = 0
    start.h_cost = heuristic(start, goal)
    start.f_cost = start.h_cost
    start.in_open = True
    
    heapq.heappush(open_set, (start.f_cost, start))
    
    nodes_expanded = 0
    frontier_history = []
    
    while open_set:
        current = heapq.heappop(open_set)[1]
        current.in_open = False
        
        if current in closed_set:
            continue
        
        closed_set.add(current)
        current.in_closed = True
        nodes_expanded += 1
        
        if current == goal:
            path = grid.get_path(current)
            execution_time = (time.time() - start_time) * 1000
            return SearchResult(
                True, path, nodes_expanded, execution_time,
                frontier_nodes=[n for n in open_set if n[1].in_open]
            )
        
        current.state = NODE_STATES['EXPANDED']
        
        neighbors = grid.get_neighbors(current, diagonal)
        
        frontier_snapshot = []
        
        for neighbor in neighbors:
            if neighbor in closed_set:
                continue
            
            neighbor.h_cost = heuristic(neighbor, goal)
            neighbor.f_cost = neighbor.h_cost
            neighbor.parent = current
            
            if not neighbor.in_open:
                heapq.heappush(open_set, (neighbor.f_cost, neighbor))
                neighbor.in_open = True
                neighbor.state = NODE_STATES['FRONTIER']
                frontier_snapshot.append(neighbor)
        
        frontier_history.append(frontier_snapshot)
    
    execution_time = (time.time() - start_time) * 1000
    return SearchResult(False, [], nodes_expanded, execution_time)


def astar_search(grid, start, goal, heuristic_name, diagonal=False, weight=1.0):
    """
    A* Search implementation.
    
    f(n) = g(n) + h(n) - expands nodes with lowest f-score first.
    
    Properties:
    - Optimal if heuristic is admissible (never overestimates)
    - Complete in finite spaces
    - Uses OPEN set (priority queue) and CLOSED set (expanded set)
    - May re-open nodes if better g-cost is found (inconsistent heuristic)
    - With consistent heuristic, never re-opens nodes
    
    Args:
        grid: Grid object
        start: Start node
        goal: Goal node
        heuristic_name: Name of heuristic to use
        diagonal: Whether to allow diagonal movement
        weight: Weight for weighted A* (w >= 1)
    
    Returns:
        SearchResult object with path and metrics
    """
    start_time = time.time()
    
    heuristic = get_heuristic(heuristic_name)
    
    grid.reset_search_visualization()
    
    if not start or not goal:
        return SearchResult(False, [], 0, 0)
    
    open_set = []
    closed_set = set()
    
    g_costs = {}
    
    start.g_cost = 0
    start.h_cost = heuristic(start, goal)
    start.f_cost = start.g_cost + weight * start.h_cost
    start.in_open = True
    
    heapq.heappush(open_set, (start.f_cost, start))
    g_costs[(start.row, start.col)] = 0
    
    nodes_expanded = 0
    
    while open_set:
        current = heapq.heappop(open_set)[1]
        current.in_open = False
        
        if current in closed_set:
            continue
        
        closed_set.add(current)
        current.in_closed = True
        nodes_expanded += 1
        
        if current == goal:
            path = grid.get_path(current)
            execution_time = (time.time() - start_time) * 1000
            return SearchResult(
                True, path, nodes_expanded, execution_time
            )
        
        current.state = NODE_STATES['EXPANDED']
        
        neighbors = grid.get_neighbors(current, diagonal)
        
        for neighbor in neighbors:
            if neighbor in closed_set:
                continue
            
            move_cost = get_cost(current, neighbor, diagonal)
            tentative_g = current.g_cost + move_cost
            
            neighbor_pos = (neighbor.row, neighbor.col)
            
            if neighbor_pos in g_costs:
                if tentative_g >= g_costs[neighbor_pos]:
                    continue
            
            g_costs[neighbor_pos] = tentative_g
            
            neighbor.g_cost = tentative_g
            neighbor.h_cost = heuristic(neighbor, goal)
            neighbor.f_cost = neighbor.g_cost + weight * neighbor.h_cost
            neighbor.parent = current
            
            if not neighbor.in_open:
                heapq.heappush(open_set, (neighbor.f_cost, neighbor))
                neighbor.in_open = True
                neighbor.state = NODE_STATES['FRONTIER']
    
    execution_time = (time.time() - start_time) * 1000
    return SearchResult(False, [], nodes_expanded, execution_time)


def run_search(grid, algorithm, start, goal, heuristic_name, diagonal=False, weight=1.0):
    """
    Run the appropriate search algorithm based on parameters.
    
    Args:
        grid: Grid object
        algorithm: Algorithm name ('GBFS' or 'A*')
        start: Start node
        goal: Goal node
        heuristic_name: Heuristic name
        diagonal: Allow diagonal movement
        weight: Weight for A*
    
    Returns:
        SearchResult object
    """
    if algorithm == 'GBFS':
        return greedy_best_first_search(grid, start, goal, heuristic_name, diagonal)
    elif algorithm == 'A*':
        return astar_search(grid, start, goal, heuristic_name, diagonal, weight)
    else:
        raise ValueError(f"Unknown algorithm: {algorithm}")


def run_search_animated(grid, algorithm, start, goal, heuristic_name, diagonal=False, weight=1.0):
    """
    Run search and return expansion steps for animation.
    
    Returns tuple: (expanded_steps, path_steps, final_result)
    - expanded_steps: list of (newly_expanded_node, frontier_nodes) per step
    - path_steps: list of nodes to show as path progressively
    - final_result: SearchResult with full path
    """
    if algorithm == 'GBFS':
        return _gbfs_animated(grid, start, goal, heuristic_name, diagonal)
    elif algorithm == 'A*':
        return _astar_animated(grid, start, goal, heuristic_name, diagonal, weight)
    else:
        raise ValueError(f"Unknown algorithm: {algorithm}")


def _gbfs_animated(grid, start, goal, heuristic_name, diagonal):
    """GBFS with animation steps."""
    import heapq
    
    grid.reset_search_visualization()
    
    if not start or not goal:
        return [], [], SearchResult(False, [], 0, 0)
    
    open_set = []
    closed_set = set()
    
    start.h_cost = get_heuristic(heuristic_name)(start, goal)
    start.f_cost = start.h_cost
    
    heapq.heappush(open_set, (start.f_cost, start))
    
    expanded_steps = []
    nodes_expanded = 0
    
    while open_set:
        current = heapq.heappop(open_set)[1]
        
        if current in closed_set:
            continue
        
        closed_set.add(current)
        nodes_expanded += 1
        
        if current != start:
            expanded_steps.append((current, []))
        
        if current == goal:
            path = grid.get_path(current)
            result = SearchResult(True, path, nodes_expanded, 0)
            return expanded_steps, [], result
        
        neighbors = grid.get_neighbors(current, diagonal)
        
        frontier_snapshot = []
        
        for neighbor in neighbors:
            if neighbor in closed_set:
                continue
            
            neighbor.h_cost = get_heuristic(heuristic_name)(neighbor, goal)
            neighbor.f_cost = neighbor.h_cost
            neighbor.parent = current
            
            heapq.heappush(open_set, (neighbor.f_cost, neighbor))
            frontier_snapshot.append(neighbor)
        
        if frontier_snapshot:
            expanded_steps.append((current, frontier_snapshot))
    
    return expanded_steps, [], SearchResult(False, [], nodes_expanded, 0)


def _astar_animated(grid, start, goal, heuristic_name, diagonal, weight):
    """A* with animation steps."""
    import heapq
    
    grid.reset_search_visualization()
    
    if not start or not goal:
        return [], [], SearchResult(False, [], 0, 0)
    
    open_set = []
    closed_set = set()
    g_costs = {}
    
    start.g_cost = 0
    start.h_cost = get_heuristic(heuristic_name)(start, goal)
    start.f_cost = start.g_cost + weight * start.h_cost
    
    heapq.heappush(open_set, (start.f_cost, start))
    g_costs[(start.row, start.col)] = 0
    
    expanded_steps = []
    nodes_expanded = 0
    
    while open_set:
        current = heapq.heappop(open_set)[1]
        
        if current in closed_set:
            continue
        
        closed_set.add(current)
        nodes_expanded += 1
        
        if current != start:
            expanded_steps.append((current, []))
        
        if current == goal:
            path = grid.get_path(current)
            result = SearchResult(True, path, nodes_expanded, 0)
            return expanded_steps, [], result
        
        neighbors = grid.get_neighbors(current, diagonal)
        
        frontier_snapshot = []
        
        for neighbor in neighbors:
            if neighbor in closed_set:
                continue
            
            move_cost = get_cost(current, neighbor, diagonal)
            tentative_g = current.g_cost + move_cost
            
            neighbor_pos = (neighbor.row, neighbor.col)
            
            if neighbor_pos in g_costs:
                if tentative_g >= g_costs[neighbor_pos]:
                    continue
            
            g_costs[neighbor_pos] = tentative_g
            
            neighbor.g_cost = tentative_g
            neighbor.h_cost = get_heuristic(heuristic_name)(neighbor, goal)
            neighbor.f_cost = neighbor.g_cost + weight * neighbor.h_cost
            neighbor.parent = current
            
            heapq.heappush(open_set, (neighbor.f_cost, neighbor))
            frontier_snapshot.append(neighbor)
        
        if frontier_snapshot:
            expanded_steps.append((current, frontier_snapshot))
    
    return expanded_steps, [], SearchResult(False, [], nodes_expanded, 0)
