"""
Grid and Node classes for the pathfinding system.
"""

import random
from config import NODE_STATES


class Node:
    """
    Represents a single cell in the grid.
    
    Attributes:
        row: Row index
        col: Column index
        state: Current state (EMPTY, WALL, START, GOAL, etc.)
        g_cost: Cost from start to this node (for A*)
        h_cost: Heuristic cost from this node to goal
        f_cost: Total cost (g + h) for A*
        parent: Parent node for path reconstruction
        visited: Whether node has been visited (for GBFS)
        in_open: Whether node is currently in OPEN set
        in_closed: Whether node is currently in CLOSED set
    """
    
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.state = NODE_STATES['EMPTY']
        self.g_cost = float('inf')
        self.h_cost = 0
        self.f_cost = float('inf')
        self.parent = None
        self.visited = False
        self.in_open = False
        self.in_closed = False
    
    def reset_search_state(self):
        """Reset search-related attributes but keep grid position state."""
        self.g_cost = float('inf')
        self.h_cost = 0
        self.f_cost = float('inf')
        self.parent = None
        self.visited = False
        self.in_open = False
        self.in_closed = False
    
    def reset(self):
        """Reset all attributes to default."""
        self.state = NODE_STATES['EMPTY']
        self.reset_search_state()
    
    def __lt__(self, other):
        """For priority queue comparison based on f_cost."""
        return self.f_cost < other.f_cost
    
    def __eq__(self, other):
        """Check equality based on position."""
        if not isinstance(other, Node):
            return False
        return self.row == other.row and self.col == other.col
    
    def __hash__(self):
        """Hash based on position for use in sets/dicts."""
        return hash((self.row, self.col))
    
    def __repr__(self):
        return f"Node({self.row}, {self.col}, state={self.state})"


class Grid:
    """
    Manages the grid of nodes and provides operations on them.
    
    Attributes:
        rows: Number of rows
        cols: Number of columns
        nodes: 2D list of Node objects
        start_node: Reference to start node
        goal_node: Reference to goal node
        agent_node: Reference to agent node (current position)
    """
    
    def __init__(self, rows, cols):
        if rows < 2 or cols < 2 or rows > 75 or cols > 75:
            raise ValueError(f"Grid size must be between 2 and 75. Got {rows}x{cols}")
        
        self.rows = rows
        self.cols = cols
        self.nodes = [[Node(r, c) for c in range(cols)] for r in range(rows)]
        self.start_node = None
        self.goal_node = None
        self.agent_node = None
    
    def get_node(self, row, col):
        """Get node at specified position."""
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.nodes[row][col]
        return None
    
    def is_valid(self, row, col):
        """Check if position is within grid bounds."""
        return 0 <= row < self.rows and 0 <= col < self.cols
    
    def is_walkable(self, row, col):
        """Check if position is walkable (not a wall)."""
        node = self.get_node(row, col)
        if node is None:
            return False
        return node.state != NODE_STATES['WALL']
    
    def set_start(self, row, col):
        """Set start node at specified position."""
        if self.start_node:
            self.start_node.state = NODE_STATES['EMPTY']
        
        node = self.get_node(row, col)
        if node and node.state != NODE_STATES['GOAL']:
            node.state = NODE_STATES['START']
            self.start_node = node
    
    def set_goal(self, row, col):
        """Set goal node at specified position."""
        if self.goal_node:
            self.goal_node.state = NODE_STATES['EMPTY']
        
        node = self.get_node(row, col)
        if node and node.state != NODE_STATES['START']:
            node.state = NODE_STATES['GOAL']
            self.goal_node = node
    
    def set_wall(self, row, col, value=True):
        """Set or remove wall at specified position."""
        node = self.get_node(row, col)
        if node and node.state not in [NODE_STATES['START'], NODE_STATES['GOAL']]:
            node.state = NODE_STATES['WALL'] if value else NODE_STATES['EMPTY']
    
    def set_agent(self, row, col):
        """Set agent position."""
        if self.agent_node and self.agent_node.state != NODE_STATES['START']:
            self.agent_node.state = NODE_STATES['EMPTY']
        
        node = self.get_node(row, col)
        if node and node.state not in [NODE_STATES['WALL'], NODE_STATES['GOAL']]:
            if node.state != NODE_STATES['START']:
                node.state = NODE_STATES['AGENT']
            self.agent_node = node
    
    def reset_search_visualization(self):
        """Reset search-related visualization states (frontier, expanded, path)."""
        for row in range(self.rows):
            for col in range(self.cols):
                node = self.nodes[row][col]
                if node.state in [NODE_STATES['FRONTIER'], NODE_STATES['EXPANDED'], NODE_STATES['PATH'], NODE_STATES['AGENT']]:
                    if node.state == NODE_STATES['AGENT']:
                        continue
                    if node != self.start_node and node != self.goal_node:
                        node.state = NODE_STATES['EMPTY']
                node.reset_search_state()
    
    def reset_all(self):
        """Reset entire grid to empty state."""
        for row in range(self.rows):
            for col in range(self.cols):
                self.nodes[row][col].reset()
        self.start_node = None
        self.goal_node = None
        self.agent_node = None
    
    def random_walls(self, density):
        """Generate random walls based on density."""
        for row in range(self.rows):
            for col in range(self.cols):
                node = self.nodes[row][col]
                if node.state in [NODE_STATES['EMPTY'], NODE_STATES['WALL']]:
                    if random.random() < density:
                        if node != self.start_node and node != self.goal_node:
                            node.state = NODE_STATES['WALL']
                    else:
                        if node != self.start_node and node != self.goal_node:
                            node.state = NODE_STATES['EMPTY']
    
    def get_neighbors(self, node, diagonal=False):
        """
        Get valid neighbors of a node.
        
        Args:
            node: The node to get neighbors for
            diagonal: Whether to include diagonal neighbors
        
        Returns:
            List of valid neighbor nodes
        """
        neighbors = []
        directions = [
            (-1, 0), (1, 0), (0, -1), (0, 1)
        ]
        
        if diagonal:
            directions.extend([
                (-1, -1), (-1, 1), (1, -1), (1, 1)
            ])
        
        for dr, dc in directions:
            new_row, new_col = node.row + dr, node.col + dc
            if self.is_valid(new_row, new_col):
                neighbor = self.get_node(new_row, new_col)
                if neighbor.state != NODE_STATES['WALL']:
                    neighbors.append(neighbor)
        
        return neighbors
    
    def get_path(self, current_node):
        """
        Reconstruct path from current node to start.
        
        Args:
            current_node: Node to start path reconstruction from
        
        Returns:
            List of nodes representing the path
        """
        path = []
        node = current_node
        
        while node is not None:
            path.append(node)
            node = node.parent
        
        path.reverse()
        return path
    
    def visualize_path(self, path):
        """Set path visualization on grid."""
        for node in path:
            if node != self.start_node and node != self.goal_node:
                node.state = NODE_STATES['PATH']
    
    def clear_path_visualization(self):
        """Clear path visualization but keep walls."""
        for row in range(self.rows):
            for col in range(self.cols):
                node = self.nodes[row][col]
                if node.state == NODE_STATES['PATH']:
                    node.state = NODE_STATES['EMPTY']
    
    def get_random_empty_cell(self):
        """Get a random empty cell (not wall, start, or goal)."""
        empty_cells = []
        for row in range(self.rows):
            for col in range(self.cols):
                node = self.nodes[row][col]
                if node.state == NODE_STATES['EMPTY']:
                    empty_cells.append(node)
        
        if empty_cells:
            return random.choice(empty_cells)
        return None
    
    def is_position_blocked(self, row, col):
        """Check if a position is blocked (wall or out of bounds)."""
        node = self.get_node(row, col)
        if node is None:
            return True
        return node.state == NODE_STATES['WALL']
