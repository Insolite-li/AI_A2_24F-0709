"""
Performance tracking and metrics for the pathfinding system.

Tracks:
- Nodes expanded
- Path cost
- Execution time
- Algorithm name
- Heuristic name
- Dynamic mode status
- Re-plans triggered count
"""

import time


class Metrics:
    """
    Tracks performance metrics for pathfinding operations.
    
    All metrics reset properly on new runs.
    """
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Reset all metrics to initial state."""
        self.nodes_expanded = 0
        self.path_cost = 0
        self.execution_time = 0
        self.algorithm_name = 'N/A'
        self.heuristic_name = 'N/A'
        self.dynamic_mode = False
        self.replans_triggered = 0
        self.searches_run = 0
        self.path_length = 0
        self.found_path = False
    
    def update_search(self, result, algorithm, heuristic):
        """
        Update metrics after a:
            result: search completes.
        
        Args SearchResult from algorithm
            algorithm the: Algorithm name
            heuristic: Heuristic name
        """
        self.nodes_expanded = result.nodes_expanded
        self.execution_time = result.execution_time
        self.algorithm_name = algorithm
        self.heuristic_name = heuristic
        self.searches_run += 1
        
        if result.success:
            self.found_path = True
            self.path = result.path
            self.path_length = len(result.path)
            self.path_cost = self.calculate_path_cost(result.path)
        else:
            self.found_path = False
            self.path = []
            self.path_length = 0
            self.path_cost = 0
    
    def calculate_path_cost(self, path):
        """
        Calculate the cost of a path.
        
        Args:
            path: List of nodes representing the path
        
        Returns:
            Total path cost
        """
        if not path or len(path) < 2:
            return 0
        
        cost = 0
        for i in range(1, len(path)):
            prev = path[i - 1]
            curr = path[i]
            
            dr = abs(curr.row - prev.row)
            dc = abs(curr.col - prev.col)
            
            if dr > 0 and dc > 0:
                cost += 1.414
            else:
                cost += 1
        
        return round(cost, 2)
    
    def increment_replans(self):
        """Increment the re-plan counter."""
        self.replans_triggered += 1
    
    def set_dynamic_mode(self, enabled):
        """
        Set dynamic mode status.
        
        Args:
            enabled: Whether dynamic mode is enabled
        """
        self.dynamic_mode = enabled
    
    def get_summary(self):
        """
        Get a summary dictionary of all metrics.
        
        Returns:
            Dictionary of metric names and values
        """
        return {
            'nodes_expanded': self.nodes_expanded,
            'path_cost': self.path_cost,
            'execution_time': round(self.execution_time, 2),
            'algorithm': self.algorithm_name,
            'heuristic': self.heuristic_name,
            'dynamic_mode': 'ON' if self.dynamic_mode else 'OFF',
            'replans_triggered': self.replans_triggered,
            'path_length': self.path_length,
            'found_path': self.found_path,
        }
    
    def __str__(self):
        """String representation of metrics."""
        return (
            f"Nodes Expanded: {self.nodes_expanded}\n"
            f"Path Cost: {self.path_cost}\n"
            f"Execution Time: {self.execution_time:.2f}ms\n"
            f"Algorithm: {self.algorithm_name}\n"
            f"Heuristic: {self.heuristic_name}\n"
            f"Dynamic Mode: {'ON' if self.dynamic_mode else 'OFF'}\n"
            f"Re-plans: {self.replans_triggered}"
        )


class AnimationController:
    """
    Controls the animation speed for path visualization.
    
    Supports variable speed playback of path exploration.
    """
    
    def __init__(self, speed=50):
        self.speed = speed
        self.min_speed = 1
        self.max_speed = 100
        self.last_update_time = 0
        self.update_interval = 0.001
    
    def set_speed(self, speed):
        """
        Set animation speed.
        
        Args:
            speed: Speed value (1-100)
        """
        self.speed = max(self.min_speed, min(self.max_speed, speed))
        self.update_interval = (100 - self.speed + 1) / 1000.0
    
    def should_update(self, current_time):
        """
        Check if animation should update.
        
        Args:
            current_time: Current timestamp
        
        Returns:
            True if enough time has passed to update
        """
        if current_time - self.last_update_time >= self.update_interval:
            self.last_update_time = current_time
            return True
        return False
    
    def get_delay_ms(self):
        """Get delay in milliseconds based on current speed."""
        return int(self.update_interval * 1000)
