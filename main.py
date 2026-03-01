"""
Dynamic Pathfinding System - Main Entry Point

A fully interactive pathfinding visualization with:
- GBFS and A* algorithms
- Multiple heuristics (Manhattan, Euclidean)
- Real-time dynamic re-planning
- Interactive GUI controls

Run: python main.py
"""

import pygame
import sys

from config import (
    DEFAULT_GRID_ROWS, DEFAULT_GRID_COLS,
    COLORS, NODE_STATES
)
from grid import Grid
from algorithms import run_search, run_search_animated
from replanner import Replanner
from metrics import Metrics, AnimationController
from ui import UI


class PathfindingApp:
    """
    Main application class for the dynamic pathfinding system.
    
    Integrates all components:
    - Grid management
    - Pathfinding algorithms
    - Dynamic re-planning
    - GUI controls
    - Metrics tracking
    """
    
    def __init__(self):
        self.grid = Grid(DEFAULT_GRID_ROWS, DEFAULT_GRID_COLS)
        self.grid.set_start(2, 2)
        self.grid.set_goal(DEFAULT_GRID_ROWS - 3, DEFAULT_GRID_COLS - 3)
        self.grid.set_agent(2, 2)
        
        self.ui = UI(self.grid)
        self.replanner = Replanner(self.grid)
        self.metrics = Metrics()
        self.animation = AnimationController()
        self.clock = pygame.time.Clock()
        
        self.is_searching = False
        self.moving_along_path = False
        self.current_path = []
        self.path_index = 0
        
        self.expansion_steps = []
        self.expansion_index = 0
        self.is_animating_search = False
        self.search_animation_complete = False
        
        self.setup_initial_state()
    
    def setup_initial_state(self):
        """Set up initial grid state."""
        self.grid.set_start(2, 2)
        self.grid.set_goal(self.grid.rows - 3, self.grid.cols - 3)
        self.grid.set_agent(2, 2)
    
    def run_search(self):
        """Execute the pathfinding search with animation."""
        if not self.grid.start_node or not self.grid.goal_node:
            return
        
        self.is_searching = True
        self.replanner.reset()
        
        self.grid.reset_search_visualization()
        
        start = self.grid.start_node
        if self.grid.agent_node:
            self.grid.agent_node.state = NODE_STATES['EMPTY']
            self.grid.agent_node = None
        
        self.grid.set_agent(start.row, start.col)
        
        expanded_steps, path_steps, result = run_search_animated(
            self.grid,
            self.ui.algorithm,
            start,
            self.grid.goal_node,
            self.ui.heuristic,
            self.ui.diagonal,
            self.ui.weight
        )
        
        self.expansion_steps = expanded_steps
        self.expansion_index = 0
        self.is_animating_search = True
        self.search_animation_complete = False
        self.final_result = result
        
        self.metrics.update_search(result, self.ui.algorithm, self.ui.heuristic)
    
    def process_search_animation(self):
        """Process one step of search animation."""
        if not self.is_animating_search or self.search_animation_complete:
            return
        
        if self.expansion_index < len(self.expansion_steps):
            expanded_node, frontier_nodes = self.expansion_steps[self.expansion_index]
            
            if expanded_node != self.grid.start_node and expanded_node != self.grid.goal_node:
                expanded_node.state = NODE_STATES['EXPANDED']
            
            for fnode in frontier_nodes:
                if fnode != self.grid.start_node and fnode != self.grid.goal_node:
                    if fnode.state != NODE_STATES['EXPANDED']:
                        fnode.state = NODE_STATES['FRONTIER']
            
            self.expansion_index += 1
        else:
            if self.final_result.success:
                self.current_path = self.final_result.path
                self.path_index = 0
                
                for node in self.current_path:
                    if node != self.grid.start_node and node != self.grid.goal_node:
                        node.state = NODE_STATES['PATH']
            else:
                self.current_path = []
            
            self.search_animation_complete = True
            self.is_animating_search = False
            self.search_complete = True
    
    def reset_grid(self):
        """Reset the grid to initial state."""
        self.grid.reset_all()
        self.grid.set_start(2, 2)
        self.grid.set_goal(self.grid.rows - 3, self.grid.cols - 3)
        self.grid.set_agent(2, 2)
        self.metrics.reset()
        self.replanner.reset()
        self.current_path = []
        self.path_index = 0
        self.search_complete = False
        self.is_searching = False
        self.is_animating_search = False
        self.search_animation_complete = False
        self.expansion_steps = []
        self.expansion_index = 0
    
    def generate_random_maze(self, density=None):
        """Generate random walls on the grid."""
        if density is None:
            density = self.ui.obstacle_density
        
        self.grid.random_walls(density)
        self.grid.set_start(2, 2)
        self.grid.set_goal(self.grid.rows - 3, self.grid.cols - 3)
        self.grid.set_agent(2, 2)
        self.metrics.reset()
        self.current_path = []
        self.path_index = 0
        self.search_complete = False
        self.is_animating_search = False
        self.search_animation_complete = False
        self.expansion_steps = []
        self.expansion_index = 0
    
    def best_case_scenario(self):
        """Generate best case scenario (almost empty grid)."""
        self.grid.reset_all()
        self.grid.set_start(2, 2)
        self.grid.set_goal(self.grid.rows - 3, self.grid.cols - 3)
        self.grid.set_agent(2, 2)
        self.metrics.reset()
        self.current_path = []
        self.path_index = 0
        self.search_complete = False
        self.is_animating_search = False
        self.search_animation_complete = False
        self.expansion_steps = []
        self.expansion_index = 0
    
    def worst_case_scenario(self):
        """Generate worst case scenario (dense grid)."""
        self.grid.reset_all()
        self.grid.random_walls(0.4)
        self.grid.set_start(2, 2)
        self.grid.set_goal(self.grid.rows - 3, self.grid.cols - 3)
        self.grid.set_agent(2, 2)
        self.metrics.reset()
        self.current_path = []
        self.path_index = 0
        self.search_complete = False
        self.is_animating_search = False
        self.search_animation_complete = False
        self.expansion_steps = []
        self.expansion_index = 0
    
    def toggle_dynamic_mode(self):
        """Toggle dynamic mode on/off."""
        self.ui.dynamic_mode = not self.ui.dynamic_mode
        self.ui.buttons['dynamic_toggle']['text'] = f"Dynamic: {'ON' if self.ui.dynamic_mode else 'OFF'}"
        self.ui.buttons['dynamic_toggle']['color'] = COLORS['BUTTON_ACTIVE'] if self.ui.dynamic_mode else COLORS['BUTTON']
        self.metrics.set_dynamic_mode(self.ui.dynamic_mode)
        
        if not self.ui.dynamic_mode:
            self.replanner.reset()
    
    def move_agent_along_path(self):
        """Move agent along the current path."""
        if not self.current_path or self.path_index >= len(self.current_path):
            self.moving_along_path = False
            return
        
        if self.path_index > 0:
            prev_node = self.current_path[self.path_index - 1]
            if prev_node != self.grid.start_node:
                prev_node.state = NODE_STATES['PATH']
        
        current_node = self.current_path[self.path_index]
        
        if current_node != self.grid.goal_node:
            if current_node != self.grid.start_node:
                self.grid.set_agent(current_node.row, current_node.col)
        
        self.path_index += 1
        
        if self.path_index >= len(self.current_path):
            self.moving_along_path = False
    
    def handle_dynamic_mode(self):
        """Handle dynamic obstacle spawning and re-planning."""
        if not self.ui.dynamic_mode or not self.search_complete:
            return
        
        if self.replanner.try_spawn_obstacle():
            pass
        
        if self.replanner.check_and_trigger_replan() == 'replan':
            self.metrics.increment_replans()
            
            start_node, goal_node = self.replanner.prepare_replan()
            
            expanded_steps, path_steps, result = run_search_animated(
                self.grid,
                self.ui.algorithm,
                start_node,
                goal_node,
                self.ui.heuristic,
                self.ui.diagonal,
                self.ui.weight
            )
            
            self.expansion_steps = expanded_steps
            self.expansion_index = 0
            self.is_animating_search = True
            self.search_animation_complete = False
            self.final_result = result
            
            if result.success:
                self.current_path = result.path
                self.path_index = 0
            else:
                self.current_path = []
    
    def run(self):
        """Main game loop."""
        running = True
        last_time = pygame.time.get_ticks()
        
        while running:
            current_time = pygame.time.get_ticks()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button in [1, 3]:
                        result = self.ui.handle_click(event.pos, event.button)
                        
                        if result == 'button_start':
                            self.run_search()
                        
                        elif result == 'button_reset':
                            self.reset_grid()
                        
                        elif result == 'button_random':
                            self.generate_random_maze()
                        
                        elif result == 'button_dynamic_toggle':
                            self.toggle_dynamic_mode()
                
                elif event.type == pygame.KEYDOWN:
                    action = self.ui.handle_keydown(event)
                    
                    if action == 'best_case':
                        self.best_case_scenario()
                    elif action == 'worst_case':
                        self.worst_case_scenario()
                    elif action == 'toggle_dynamic':
                        self.toggle_dynamic_mode()
                
                elif event.type == pygame.MOUSEMOTION:
                    if pygame.mouse.get_pressed()[0] or pygame.mouse.get_pressed()[2]:
                        if pygame.mouse.get_pos()[0] < 900:
                            self.ui.handle_click(event.pos, 
                                               1 if pygame.mouse.get_pressed()[0] else 3)
                
                elif event.type == pygame.MOUSEBUTTONUP:
                    pass
            
            self.ui.close_dropdowns()
            
            if self.is_animating_search and self.animation.should_update(current_time):
                self.process_search_animation()
            
            if self.moving_along_path and self.animation.should_update(current_time):
                self.move_agent_along_path()
            
            if self.ui.dynamic_mode and self.search_complete and not self.is_searching:
                self.handle_dynamic_mode()
            
            self.animation.set_speed(self.ui.animation_speed)
            
            self.ui.draw(self.metrics)
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()


def main():
    """Entry point."""
    try:
        app = PathfindingApp()
        app.run()
    except Exception as e:
        print(f"Error: {e}")
        pygame.quit()
        sys.exit(1)


if __name__ == "__main__":
    main()
