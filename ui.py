"""
GUI logic and controls for the pathfinding system.

Handles:
- Pygame rendering
- Mouse interactions (click, shift+click, ctrl+click)
- Control panel (dropdowns, buttons, sliders)
- Metrics display
- Keyboard hotkeys
"""

import pygame
import sys
from config import (
    COLORS, NODE_STATES, SCREEN_WIDTH, SCREEN_HEIGHT, GRID_PANEL_WIDTH,
    DEFAULT_GRID_ROWS, DEFAULT_GRID_COLS, NODE_SIZE, MARGIN,
    ALGORITHMS, HEURISTICS, WEIGHTS
)


class UI:
    """
    Manages all GUI interactions and rendering.
    """
    
    def __init__(self, grid):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Dynamic Pathfinding System")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 18)
        
        self.grid = grid
        
        self.node_size = NODE_SIZE
        self.margin = MARGIN
        
        self.panel_x = GRID_PANEL_WIDTH + 20
        
        self.algorithm = 'A*'
        self.heuristic = 'Euclidean'
        self.weight = 1.0
        self.diagonal = False
        self.dynamic_mode = False
        self.animation_speed = 50
        self.obstacle_density = 0.3
        
        self.buttons = {}
        self.dropdowns = {}
        self.sliders = {}
        
        self.is_running = False
        self.search_complete = False
        self.moving_along_path = False
        self.current_path_index = 0
        
        self.setup_controls()
    
    def setup_controls(self):
        """Initialize all control elements."""
        y_offset = 100
        
        self.dropdowns['algorithm'] = {
            'rect': pygame.Rect(self.panel_x, y_offset, 150, 30),
            'options': ALGORITHMS,
            'selected': self.algorithm,
            'open': False
        }
        
        y_offset += 50
        self.dropdowns['heuristic'] = {
            'rect': pygame.Rect(self.panel_x, y_offset, 150, 30),
            'options': HEURISTICS,
            'selected': self.heuristic,
            'open': False
        }
        
        y_offset += 50
        self.dropdowns['weight'] = {
            'rect': pygame.Rect(self.panel_x, y_offset, 150, 30),
            'options': [str(w) for w in WEIGHTS],
            'selected': str(self.weight),
            'open': False
        }
        
        y_offset += 50
        self.dropdowns['diagonal'] = {
            'rect': pygame.Rect(self.panel_x, y_offset, 150, 30),
            'options': ['4-Dir', '8-Dir'],
            'selected': '4-Dir',
            'open': False
        }
        
        y_offset += 60
        self.buttons['start'] = {
            'rect': pygame.Rect(self.panel_x, y_offset, 150, 35),
            'text': 'Start Search',
            'color': COLORS['BUTTON']
        }
        
        y_offset += 45
        self.buttons['reset'] = {
            'rect': pygame.Rect(self.panel_x, y_offset, 150, 35),
            'text': 'Reset Grid',
            'color': COLORS['BUTTON']
        }
        
        y_offset += 45
        self.buttons['random'] = {
            'rect': pygame.Rect(self.panel_x, y_offset, 150, 35),
            'text': 'Random Maze',
            'color': COLORS['BUTTON']
        }
        
        y_offset += 60
        self.sliders['density'] = {
            'rect': pygame.Rect(self.panel_x, y_offset, 150, 20),
            'min': 0,
            'max': 100,
            'value': int(self.obstacle_density * 100),
            'label': 'Obstacle Density'
        }
        
        y_offset += 40
        self.sliders['speed'] = {
            'rect': pygame.Rect(self.panel_x, y_offset, 150, 20),
            'min': 1,
            'max': 100,
            'value': self.animation_speed,
            'label': 'Animation Speed'
        }
        
        y_offset += 60
        self.buttons['dynamic_toggle'] = {
            'rect': pygame.Rect(self.panel_x, y_offset, 150, 35),
            'text': 'Dynamic: OFF',
            'color': COLORS['BUTTON']
        }
    
    def get_grid_offset(self):
        """Calculate grid drawing offset to center it."""
        grid_width = self.grid.cols * (self.node_size + self.margin)
        grid_height = self.grid.rows * (self.node_size + self.margin)
        x_offset = (GRID_PANEL_WIDTH - grid_width) // 2
        y_offset = (SCREEN_HEIGHT - grid_height) // 2
        return x_offset, y_offset
    
    def draw_grid(self):
        """Draw the grid and nodes."""
        x_offset, y_offset = self.get_grid_offset()
        
        for row in range(self.grid.rows):
            for col in range(self.grid.cols):
                node = self.grid.get_node(row, col)
                x = x_offset + col * (self.node_size + self.margin)
                y = y_offset + row * (self.node_size + self.margin)
                
                rect = pygame.Rect(x, y, self.node_size, self.node_size)
                
                color = COLORS['EMPTY']
                if node.state == NODE_STATES['WALL']:
                    color = COLORS['WALL']
                elif node.state == NODE_STATES['START']:
                    color = COLORS['START']
                elif node.state == NODE_STATES['GOAL']:
                    color = COLORS['GOAL']
                elif node.state == NODE_STATES['FRONTIER']:
                    color = COLORS['FRONTIER']
                elif node.state == NODE_STATES['EXPANDED']:
                    color = COLORS['EXPANDED']
                elif node.state == NODE_STATES['PATH']:
                    color = COLORS['PATH']
                elif node.state == NODE_STATES['AGENT']:
                    color = COLORS['AGENT']
                
                pygame.draw.rect(self.screen, color, rect)
    
    def draw_controls(self):
        """Draw the control panel."""
        pygame.draw.rect(self.screen, COLORS['PANEL'], 
                        (GRID_PANEL_WIDTH, 0, SCREEN_WIDTH - GRID_PANEL_WIDTH, SCREEN_HEIGHT))
        
        title = self.title_font.render("Controls", True, COLORS['TEXT'])
        self.screen.blit(title, (self.panel_x, 30))
        
        for name, btn in self.buttons.items():
            pygame.draw.rect(self.screen, btn['color'], btn['rect'])
            pygame.draw.rect(self.screen, COLORS['TEXT'], btn['rect'], 1)
            
            text = self.font.render(btn['text'], True, COLORS['TEXT'])
            text_rect = text.get_rect(center=btn['rect'].center)
            self.screen.blit(text, text_rect)
        
        for name, ddown in self.dropdowns.items():
            pygame.draw.rect(self.screen, COLORS['INPUT_BG'], ddown['rect'])
            pygame.draw.rect(self.screen, COLORS['TEXT'], ddown['rect'], 1)
            
            text = self.font.render(ddown['selected'], True, COLORS['TEXT'])
            self.screen.blit(text, (ddown['rect'].x + 5, ddown['rect'].y + 5))
            
            arrow = self.font.render("Click >", True, COLORS['TEXT'])
            self.screen.blit(arrow, (ddown['rect'].right - 60, ddown['rect'].y + 5))
        
        for name, slider in self.sliders.items():
            label = self.small_font.render(slider['label'], True, COLORS['TEXT'])
            self.screen.blit(label, (slider['rect'].x, slider['rect'].y - 15))
            
            pygame.draw.rect(self.screen, COLORS['INPUT_BG'], slider['rect'])
            pygame.draw.rect(self.screen, COLORS['TEXT'], slider['rect'], 1)
            
            fill_width = int((slider['value'] - slider['min']) / (slider['max'] - slider['min']) * slider['rect'].width)
            fill_rect = pygame.Rect(slider['rect'].x, slider['rect'].y, fill_width, slider['rect'].height)
            pygame.draw.rect(self.screen, COLORS['BUTTON_ACTIVE'], fill_rect)
            
            value_text = self.small_font.render(str(slider['value']), True, COLORS['TEXT'])
            self.screen.blit(value_text, (slider['rect'].right + 5, slider['rect'].y))
    
    def draw_metrics(self, metrics):
        """Draw the metrics panel."""
        y_offset = 450
        
        title = self.title_font.render("Metrics", True, COLORS['TEXT'])
        self.screen.blit(title, (self.panel_x, y_offset))
        
        y_offset += 40
        
        metrics_text = [
            f"Algorithm: {metrics.algorithm_name}",
            f"Heuristic: {metrics.heuristic_name}",
            f"Nodes Expanded: {metrics.nodes_expanded}",
            f"Path Cost: {metrics.path_cost}",
            f"Execution Time: {metrics.execution_time:.2f}ms",
            f"Path Length: {metrics.path_length}",
            f"Dynamic Mode: {'ON' if metrics.dynamic_mode else 'OFF'}",
            f"Re-plans: {metrics.replans_triggered}",
        ]
        
        for line in metrics_text:
            text = self.font.render(line, True, COLORS['TEXT'])
            self.screen.blit(text, (self.panel_x, y_offset))
            y_offset += 25
    
    def draw_instructions(self):
        """Draw control instructions."""
        y_offset = 750
        
        instructions = [
            "Controls:",
            "Left Click: Add Wall",
            "Right Click: Remove Wall",
            "Shift + Click: Move Start",
            "Ctrl + Click: Move Goal",
            "",
            "Hotkeys:",
            "B: Best Case (empty)",
            "W: Worst Case (dense)",
            "D: Toggle Dynamic Mode",
        ]
        
        for line in instructions:
            text = self.small_font.render(line, True, COLORS['TEXT'])
            self.screen.blit(text, (self.panel_x, y_offset))
            y_offset += 18
    
    def draw(self, metrics):
        """Main draw function."""
        self.screen.fill(COLORS['BACKGROUND'])
        
        pygame.draw.line(self.screen, COLORS['TEXT'], 
                        (GRID_PANEL_WIDTH, 0), (GRID_PANEL_WIDTH, SCREEN_HEIGHT), 2)
        
        self.draw_grid()
        self.draw_controls()
        self.draw_metrics(metrics)
        self.draw_instructions()
        
        pygame.display.flip()
    
    def get_grid_position(self, mouse_pos):
        """Convert mouse position to grid coordinates."""
        x_offset, y_offset = self.get_grid_offset()
        
        x = (mouse_pos[0] - x_offset) // (self.node_size + self.margin)
        y = (mouse_pos[1] - y_offset) // (self.node_size + self.margin)
        
        if 0 <= x < self.grid.cols and 0 <= y < self.grid.rows:
            return y, x
        return None
    
    def handle_click(self, mouse_pos, button):
        """Handle mouse click events."""
        grid_pos = self.get_grid_position(mouse_pos)
        
        if grid_pos:
            row, col = grid_pos
            keys = pygame.key.get_pressed()
            
            if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                self.grid.set_start(row, col)
                self.grid.set_agent(row, col)
            elif keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:
                self.grid.set_goal(row, col)
            elif button == 1:
                self.grid.set_wall(row, col, True)
            elif button == 3:
                self.grid.set_wall(row, col, False)
            
            return True
        
        # Click-to-cycle dropdowns
        if self.dropdowns['algorithm']['rect'].collidepoint(mouse_pos):
            opts = self.dropdowns['algorithm']['options']
            idx = opts.index(self.algorithm)
            self.algorithm = opts[(idx + 1) % len(opts)]
            self.dropdowns['algorithm']['selected'] = self.algorithm
            return True
        
        if self.dropdowns['heuristic']['rect'].collidepoint(mouse_pos):
            opts = self.dropdowns['heuristic']['options']
            idx = opts.index(self.heuristic)
            self.heuristic = opts[(idx + 1) % len(opts)]
            self.dropdowns['heuristic']['selected'] = self.heuristic
            return True
        
        if self.dropdowns['weight']['rect'].collidepoint(mouse_pos):
            opts = self.dropdowns['weight']['options']
            idx = opts.index(self.dropdowns['weight']['selected'])
            self.dropdowns['weight']['selected'] = opts[(idx + 1) % len(opts)]
            self.weight = float(self.dropdowns['weight']['selected'])
            return True
        
        if self.dropdowns['diagonal']['rect'].collidepoint(mouse_pos):
            opts = self.dropdowns['diagonal']['options']
            idx = opts.index(self.dropdowns['diagonal']['selected'])
            self.dropdowns['diagonal']['selected'] = opts[(idx + 1) % len(opts)]
            self.diagonal = (self.dropdowns['diagonal']['selected'] == '8-Dir')
            return True
        
        for name, btn in self.buttons.items():
            if btn['rect'].collidepoint(mouse_pos):
                return f"button_{name}"
        
        for name, slider in self.sliders.items():
            if slider['rect'].collidepoint(mouse_pos):
                rel_x = mouse_pos[0] - slider['rect'].x
                new_value = int(slider['min'] + (rel_x / slider['rect'].width) * (slider['max'] - slider['min']))
                new_value = max(slider['min'], min(slider['max'], new_value))
                slider['value'] = new_value
                
                if name == 'density':
                    self.obstacle_density = new_value / 100
                elif name == 'speed':
                    self.animation_speed = new_value
                
                return True
        
        return False
    
    def handle_keydown(self, event):
        """Handle keyboard events."""
        if event.key == pygame.K_b:
            return 'best_case'
        elif event.key == pygame.K_w:
            return 'worst_case'
        elif event.key == pygame.K_d:
            return 'toggle_dynamic'
        return None
    
    def close_dropdowns(self):
        """Close all dropdown menus."""
        for ddown in self.dropdowns.values():
            ddown['open'] = False
