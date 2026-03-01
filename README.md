# AI_A2_24F-0709
# Dynamic Pathfinding System

A fully interactive, dynamically re-planning pathfinding visualization system built with Python and Pygame.

## Features

- **Algorithms**: Greedy Best-First Search (GBFS) and A* Search
- **Heuristics**: Manhattan, Euclidean (extensible)
- **Dynamic Mode**: Real-time obstacle spawning with automatic re-planning
- **Interactive GUI**: Click to draw walls, drag to move start/goal
- **Performance Metrics**: Live tracking of nodes expanded, path cost, execution time

## Installation

```bash
pip install -r requirements.txt
```

## How to Run

```bash
cd dynamic_pathfinder
python main.py
```

## Controls

### Mouse
- **Left Click**: Add wall
- **Right Click**: Remove wall
- **Shift + Click**: Move Start position
- **Ctrl + Click**: Move Goal position
- **Drag**: Paint walls

### Keyboard
- **B**: Best Case scenario (almost empty grid)
- **W**: Worst Case scenario (dense grid)
- **D**: Toggle Dynamic Mode

### GUI Controls
- **Algorithm**: Select GBFS or A*
- **Heuristic**: Select Manhattan or Euclidean
- **Weight**: Select weight for Weighted A* (1.0, 1.5, 2.0)
- **4-Dir/8-Dir**: Toggle diagonal movement
- **Start Search**: Begin pathfinding
- **Reset Grid**: Clear all walls and reset
- **Random Maze**: Generate random obstacles
- **Dynamic Toggle**: Enable/disable dynamic obstacle spawning
- **Sliders**: Adjust obstacle density and animation speed

## Architecture

```
dynamic_pathfinder/
├── main.py          # Entry point
├── config.py        # Global configuration
├── grid.py          # Grid and Node classes
├── algorithms.py   # GBFS and A* implementations
├── replanner.py     # Dynamic re-planning controller
├── ui.py            # GUI logic
├── metrics.py       # Performance tracking
└── utils.py         # Heuristics and helpers
```

## Theory Notes

### OPEN vs CLOSED Sets

- **OPEN Set**: Priority queue of nodes to be evaluated. Contains nodes that have been discovered but not yet explored.
- **CLOSED Set (Expanded)**: Set of nodes that have already been evaluated. Prevents re-visiting.

### Strict Visited List

Using a strict "visited" list (once visited, never re-open) breaks A* and UCS because:
- The first path to a node might not be optimal
- A later path might have lower cost but would be rejected

A* correctly uses CLOSED to track *expanded* nodes, not *visited* nodes, allowing re-opening when a better g-cost is found.

### Why A* May Re-open Nodes

A* may re-open nodes if the heuristic is **inconsistent** (not monotone). With a consistent heuristic:
- h(n) ≤ cost(n, n') + h(n')
- A* never re-opens nodes after expansion

### Dynamic Re-planning Strategy

When obstacles appear on the current path:
1. Start re-planning from agent's **current position** (not original start)
2. Keep the same goal
3. Preserve all walls
4. Clear frontier/expanded visualization
5. Re-run search algorithm

This demonstrates understanding of incremental planning - we don't restart from scratch, we continue from where the agent is.

## Algorithm Comparison

| Algorithm | Optimal | Complete | Fast | Memory |
|-----------|---------|----------|------|--------|
| GBFS      | No     | Yes      | Yes  | Low    |
| A*        | Yes*   | Yes      | Medium| Medium |
| Weighted A* | Sub-optimal | Yes | Fast | Low    |

*With admissible heuristic
