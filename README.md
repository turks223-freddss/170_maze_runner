# Turn-Based Maze Game

## Overview
The **Turn-Based Maze Game** is a strategic puzzle game where players navigate a grid-based maze, overcoming obstacles and utilizing special skills to reach the goal. The game alternates turns between the player and the AI-controlled "Maze Master."

## How to Play
- The player starts at the top-left corner of the grid (0,0).
- The goal is to reach the bottom-right corner of the grid.
- Movement is limited by a turn-based system.
- Players can utilize skills to enhance movement or bypass obstacles.
- Walls can be placed strategically to block paths.
- The game ends when the player reaches the goal or becomes trapped.

## Controls
- **Mouse Clicks**: Interact with skill buttons and place walls.

## Skills
1. **Extended Move**: Increases movement range for one turn.
2. **Teleport**: Allows the player to jump to a distant tile once per game.
3. **Skill 3 (Future Implementation)**
4. **Skill 4 (Future Implementation)**

## Game Elements
- **Walls**: Can be placed to create barriers and strategic advantages.
- **Turn System**: Players and the AI take turns.
- **Notifications**: Visual indicators show whose turn it is.
- **Highlighting**: Clickable areas and valid moves are highlighted for clarity.

## Winning Condition
The player wins upon reaching the designated goal tile at the bottom-right corner of the grid.

## Losing Condition
The game is lost if the player is completely blocked with no available moves.

## Installation & Requirements
- Install Python 3.x
- Install Pygame: `pip install pygame`
- Run the game: `python game.py`