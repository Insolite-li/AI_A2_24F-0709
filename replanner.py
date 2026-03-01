"""
Dynamic re-planning controller for handling real-time obstacle spawning.

This module handles:
- Random obstacle spawning during agent movement
- Collision detection with current path
- Incremental re-planning from agent's current position

Theory Notes:
- Dynamic obstacles break static optimality guarantees
- Re-planning starts from agent's CURRENT position (not original start)
- Only re-computes when path is blocked
- Demonstrates understanding of incremental planning
"""

import random
from config import NODE_STATES, OBSTACLE_SPAWN_PROBABILITY


class Replanner:
    """
    Manages dynamic re-planning when obstacles appear on the path.
    
    Key behavior:
    1. Spawns obstacles with given probability each frame
    2. Checks if obstacle blocks remaining path
    3. Triggers re-plan only when necessary
    4. Starts from agent's current position (incremental)
    """
    
    def __init__(self, grid, spawn_probability=OBSTACLE_SPAWN_PROBABILITY):
        self.grid = grid
        self.spawn_probability = spawn_probability
        self.replan_count = 0
        self.last_spawned_obstacle = None
        self.replan_triggered = False
    
    def reset(self):
        """Reset re-planning state."""
        self.replan_count = 0
        self.last_spawned_obstacle = None
        self.replan_triggered = False
    
    def spawn_random_obstacle(self):
        """
        Attempt to spawn a random obstacle.
        
        Obstacle will NOT spawn on:
        - Agent position
        - Start node
        - Goal node
        - Current path (if exists)
        
        Returns:
            True if obstacle was spawned, False otherwise
        """
        if not self.grid.start_node or not self.grid.goal_node:
            return False
        
        spawn_row = random.randint(0, self.grid.rows - 1)
        spawn_col = random.randint(0, self.grid.cols - 1)
        
        node = self.grid.get_node(spawn_row, spawn_col)
        
        if node is None:
            return False
        
        if node == self.grid.agent_node:
            return False
        
        if node == self.grid.start_node:
            return False
        
        if node == self.grid.goal_node:
            return False
        
        if self.grid.agent_node:
            path = self.get_remaining_path()
            for path_node in path:
                if path_node == node:
                    return False
        
        if node.state != NODE_STATES['WALL']:
            node.state = NODE_STATES['WALL']
            self.last_spawned_obstacle = (spawn_row, spawn_col)
            return True
        
        return False
    
    def try_spawn_obstacle(self):
        """
        Try to spawn an obstacle based on probability.
        
        Returns:
            True if obstacle was spawned, False otherwise
        """
        if random.random() < self.spawn_probability:
            return self.spawn_random_obstacle()
        return False
    
    def get_remaining_path(self):
        """
        Get the remaining path from agent to goal.
        
        Returns:
            List of nodes from agent's current position to goal
        """
        if not self.grid.agent_node or not self.grid.goal_node:
            return []
        
        path = []
        node = self.grid.goal_node
        
        while node is not None:
            path.append(node)
            node = node.parent
        
        path.reverse()
        
        if self.grid.agent_node in path:
            agent_index = path.index(self.grid.agent_node)
            return path[agent_index:]
        
        return path
    
    def is_path_blocked(self):
        """
        Check if the remaining path is blocked by obstacles.
        
        Returns:
            True if path is blocked, False otherwise
        """
        if not self.grid.agent_node or not self.grid.goal_node:
            return True
        
        remaining_path = self.get_remaining_path()
        
        for node in remaining_path:
            if node.state == NODE_STATES['WALL']:
                return True
        
        return False
    
    def check_and_trigger_replan(self):
        """
        Check if re-planning is needed and return appropriate action.
        
        Returns:
            'replan' if re-planning should occur, 'continue' otherwise
        """
        if self.is_path_blocked():
            self.replan_triggered = True
            return 'replan'
        
        self.replan_triggered = False
        return 'continue'
    
    def prepare_replan(self):
        """
        Prepare grid for re-planning.
        
        Clears:
        - Frontier visualization
        - Expanded visualization
        
        Preserves:
        - All walls
        - Start and goal positions
        - Path so far
        """
        self.grid.reset_search_visualization()
        
        self.replan_count += 1
        
        return self.grid.agent_node, self.grid.goal_node
    
    def get_current_agent_position(self):
        """
        Get the current agent position for re-planning start.
        
        Returns:
            Current agent node
        """
        return self.grid.agent_node
    
    def clear_agent_path(self):
        """
        Clear the old path visualization from agent's position.
        
        This is called before re-planning to show fresh search.
        """
        self.grid.clear_path_visualization()
    
    def should_spawn_on_path(self, force=False):
        """
        Determine if obstacle should spawn on the current path.
        
        Args:
            force: Force spawn even if on path
        
        Returns:
            Whether to attempt spawning
        """
        if force:
            return True
        
        if not self.grid.agent_node:
            return False
        
        remaining_path = self.get_remaining_path()
        
        if not remaining_path:
            return random.random() < self.spawn_probability
        
        path_nodes = set((n.row, n.col) for n in remaining_path)
        
        attempts = 0
        max_attempts = 10
        
        while attempts < max_attempts:
            attempts += 1
            
            spawn_row = random.randint(0, self.grid.rows - 1)
            spawn_col = random.randint(0, self.grid.cols - 1)
            
            if (spawn_row, spawn_col) in path_nodes:
                continue
            
            node = self.grid.get_node(spawn_row, spawn_col)
            
            if node and node != self.grid.start_node and node != self.grid.goal_node and node != self.grid.agent_node:
                if node.state != NODE_STATES['WALL']:
                    node.state = NODE_STATES['WALL']
                    self.last_spawned_obstacle = (spawn_row, spawn_col)
                    return True
        
        return False
    
    def get_replan_count(self):
        """Get the number of re-plans performed."""
        return self.replan_count
