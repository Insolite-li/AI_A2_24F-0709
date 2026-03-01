"""
Global configuration constants for the dynamic pathfinding system.
"""

import pygame

SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 900
GRID_PANEL_WIDTH = 900

DEFAULT_GRID_ROWS = 30
DEFAULT_GRID_COLS = 30
MAX_GRID_SIZE = 75

NODE_SIZE = 20
MARGIN = 1

COLORS = {
    'BACKGROUND': (30, 30, 30),
    'GRID_BG': (40, 40, 40),
    'EMPTY': (60, 60, 60),
    'WALL': (0, 0, 0),
    'START': (0, 255, 255),
    'GOAL': (128, 0, 128),
    'FRONTIER': (255, 255, 0),
    'EXPANDED': (255, 100, 100),
    'PATH': (0, 255, 0),
    'AGENT': (50, 100, 255),
    'TEXT': (255, 255, 255),
    'BUTTON': (70, 70, 70),
    'BUTTON_HOVER': (100, 100, 100),
    'BUTTON_ACTIVE': (0, 150, 200),
    'PANEL': (50, 50, 50),
    'INPUT_BG': (60, 60, 60),
}

NODE_STATES = {
    'EMPTY': 0,
    'WALL': 1,
    'START': 2,
    'GOAL': 3,
    'FRONTIER': 4,
    'EXPANDED': 5,
    'PATH': 6,
    'AGENT': 7,
}

STATE_NAMES = {v: k for k, v in NODE_STATES.items()}

ALGORITHMS = ['GBFS', 'A*']
HEURISTICS = ['Manhattan', 'Euclidean']
WEIGHTS = [1.0, 1.5, 2.0]

DEFAULT_ALGORITHM = 'A*'
DEFAULT_HEURISTIC = 'Euclidean'
DEFAULT_WEIGHT = 1.0
DEFAULT_OBSTACLE_DENSITY = 0.3
DEFAULT_ANIMATION_SPEED = 50
DEFAULT_DIAGONAL = False

OBSTACLE_SPAWN_PROBABILITY = 0.03
