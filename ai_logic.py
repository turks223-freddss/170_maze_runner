import heapq
import random
from collections import deque
from typing import List, Tuple, Set, Dict, Optional

class MazeRunnerAI:
    def __init__(self, grid_size: int):
        self.grid_size = grid_size
        self.walls: Set[Tuple[int, int]] = set()
        self.player_pos = (0, 0)
        self.end_pos = (grid_size - 1, grid_size - 1)
        self.skill_1_available = True
        self.skill_2_available = True
        self.skill_3_available = False
        self.total_steps = 0

    def update_state(self, walls: Set[Tuple[int, int]], player_pos: Tuple[int, int]):
        """Update the AI's knowledge of the game state"""
        self.walls = walls
        self.player_pos = player_pos
        
    def get_valid_moves(self, pos: Tuple[int, int], max_distance: int = 1) -> List[Tuple[int, int]]:
        """Get all valid moves from current position"""
        x, y = pos
        valid_tiles = []
        
        # Regular movement (up, down, left, right)
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            new_x, new_y = x + dx, y + dy
            if (0 <= new_x < self.grid_size and 
                0 <= new_y < self.grid_size and 
                (new_x, new_y) not in self.walls):
                valid_tiles.append((new_x, new_y))
                
        return valid_tiles

    def a_star_search(self, start: Tuple[int, int], goal: Tuple[int, int]) -> Optional[List[Tuple[int, int]]]:
        """A* search algorithm for pathfinding"""
        def heuristic(pos: Tuple[int, int]) -> float:
            return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])
        
        frontier = []
        heapq.heappush(frontier, (0, start))
        came_from = {start: None}
        cost_so_far = {start: 0}
        
        while frontier:
            current = heapq.heappop(frontier)[1]
            
            if current == goal:
                break
                
            for next_pos in self.get_valid_moves(current):
                new_cost = cost_so_far[current] + 1
                if next_pos not in cost_so_far or new_cost < cost_so_far[next_pos]:
                    cost_so_far[next_pos] = new_cost
                    priority = new_cost + heuristic(next_pos)
                    heapq.heappush(frontier, (priority, next_pos))
                    came_from[next_pos] = current
        
        # Reconstruct path
        if goal not in came_from:
            return None
            
        path = []
        current = goal
        while current is not None:
            path.append(current)
            current = came_from[current]
        path.reverse()
        return path

    def decide_move(self) -> Tuple[Tuple[int, int], str, bool]:
        """Decide the next move and whether to use a skill"""
        # Try to find optimal path
        path = self.a_star_search(self.player_pos, self.end_pos)
        
        # If no path exists, we're blocked - try to use skills to unblock
        if not path:
            # First priority: Use wall break if available
            if self.skill_3_available:
                # Find the most strategic wall to break
                best_wall = None
                best_path_length = float('inf')
                best_distance_to_goal = float('inf')
                
                # Look for walls adjacent to player that might lead to goal
                x, y = self.player_pos
                # Check in all 4 directions
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    wall_x, wall_y = x + dx, y + dy
                    if (wall_x, wall_y) in self.walls:
                        # Calculate manhattan distance to goal
                        distance_to_goal = abs(wall_x - self.end_pos[0]) + abs(wall_y - self.end_pos[1])
                        
                        # Temporarily remove wall to check if it creates a path
                        self.walls.remove((wall_x, wall_y))
                        test_path = self.a_star_search(self.player_pos, self.end_pos)
                        self.walls.add((wall_x, wall_y))
                        
                        if test_path:
                            # Prioritize walls that create shorter paths and are closer to the goal
                            path_length = len(test_path)
                            if path_length < best_path_length or (path_length == best_path_length and distance_to_goal < best_distance_to_goal):
                                best_wall = (wall_x, wall_y)
                                best_path_length = path_length
                                best_distance_to_goal = distance_to_goal
                
                if best_wall:
                    return best_wall, "skill_3", True

            # Second priority: Use teleport if available
            if self.skill_2_available:
                # Try to teleport to a position that might lead to better options
                best_teleport = None
                best_path_length = float('inf')
                best_distance_to_goal = float('inf')
                
                x, y = self.player_pos
                for dx in range(-2, 3):
                    for dy in range(-2, 3):
                        new_x, new_y = x + dx, y + dy
                        if (0 <= new_x < self.grid_size and 
                            0 <= new_y < self.grid_size and 
                            (new_x, new_y) not in self.walls):
                            # Calculate manhattan distance to goal
                            distance_to_goal = abs(new_x - self.end_pos[0]) + abs(new_y - self.end_pos[1])
                            
                            test_path = self.a_star_search((new_x, new_y), self.end_pos)
                            if test_path:
                                path_length = len(test_path)
                                if path_length < best_path_length or (path_length == best_path_length and distance_to_goal < best_distance_to_goal):
                                    best_teleport = (new_x, new_y)
                                    best_path_length = path_length
                                    best_distance_to_goal = distance_to_goal
                
                if best_teleport:
                    return best_teleport, "skill_2", True

            # If no skills available or useful, move to any valid adjacent tile
            # This helps stall for skill cooldowns
            valid_moves = self.get_valid_moves(self.player_pos)
            if valid_moves:
                # Choose the move that gets us closest to the goal
                best_move = min(valid_moves, 
                              key=lambda pos: abs(pos[0] - self.end_pos[0]) + abs(pos[1] - self.end_pos[1]))
                return best_move, "none", False
            return self.player_pos, "none", False

        if not path or len(path) < 2:
            # No path found or already at goal
            return self.player_pos, "none", False
            
        next_pos = path[1]
        
        # Check if using extended move (Skill 1) would be beneficial
        if self.skill_1_available and len(path) > 3:
            extended_moves = []
            x, y = self.player_pos
            # Check horizontal and vertical lines
            for dx, dy in [(1,0), (-1,0), (0,1), (0,-1)]:
                for i in range(1, 5):
                    new_x, new_y = x + dx*i, y + dy*i
                    if (new_x, new_y) in self.walls or not (0 <= new_x < self.grid_size and 0 <= new_y < self.grid_size):
                        break
                    if (new_x, new_y) in path:
                        extended_moves.append((new_x, new_y))
            
            if extended_moves:
                best_move = min(extended_moves, key=lambda pos: path.index(pos))
                if path.index(best_move) > 1:  # Only use if it gets us further than regular move
                    return best_move, "skill_1", True
        
        # Default to next position in optimal path
        return next_pos, "none", False

class MazeMasterAI:
    def __init__(self, grid_size: int):
        self.grid_size = grid_size
        self.walls: Set[Tuple[int, int]] = set()
        self.player_pos = (0, 0)
        self.end_pos = (grid_size - 1, grid_size - 1)
        self.skill_1_cooldown = 0
        self.skill_2_used = False
        self.skill_3_cooldown = 0
        self.difficulty = 0.5  # 0.0 to 1.0, adjusts based on player performance

    def update_state(self, walls: Set[Tuple[int, int]], player_pos: Tuple[int, int], player_steps: int):
        """Update the AI's knowledge of the game state and adjust difficulty"""
        self.walls = walls
        self.player_pos = player_pos
        
        # Adjust difficulty based on player performance
        optimal_path = self.find_shortest_path(self.player_pos, self.end_pos)
        if optimal_path:
            optimal_length = len(optimal_path)
            if player_steps > optimal_length * 2:
                self.difficulty = min(1.0, self.difficulty + 0.1)  # Player struggling, increase difficulty
            elif player_steps <= optimal_length * 1.2:
                self.difficulty = max(0.2, self.difficulty - 0.1)  # Player doing well, decrease difficulty

    def find_shortest_path(self, start: Tuple[int, int], goal: Tuple[int, int]) -> Optional[List[Tuple[int, int]]]:
        """Find shortest path using BFS"""
        queue = deque([[start]])
        visited = {start}
        
        while queue:
            path = queue.popleft()
            current = path[-1]
            
            if current == goal:
                return path
                
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                next_pos = (current[0] + dx, current[1] + dy)
                if (0 <= next_pos[0] < self.grid_size and 
                    0 <= next_pos[1] < self.grid_size and 
                    next_pos not in self.walls and 
                    next_pos not in visited):
                    visited.add(next_pos)
                    queue.append(path + [next_pos])
        
        return None

    def is_valid_wall_position(self, x: int, y: int, is_horizontal: bool) -> bool:
        """Check if a wall can be placed at a specific position"""
        if is_horizontal:
            wall_positions = [(x + i, y) for i in range(3)]
        else:
            wall_positions = [(x, y + i) for i in range(3)]
        
        return all(0 <= wx < self.grid_size and 
                  0 <= wy < self.grid_size and 
                  (wx, wy) != self.player_pos and 
                  (wx, wy) != self.end_pos and 
                  (wx, wy) not in self.walls
                  for wx, wy in wall_positions)

    def get_strategic_wall_positions(self) -> List[Tuple[Tuple[int, int], bool]]:
        """Get strategic positions for wall placement"""
        positions = []
        path = self.find_shortest_path(self.player_pos, self.end_pos)
        
        if not path:
            return positions
            
        # Try to block the shortest path
        for i in range(len(path) - 1):
            current = path[i]
            next_pos = path[i + 1]
            
            # Try horizontal and vertical walls near the path
            for is_horizontal in [True, False]:
                for offset in [-1, 0, 1]:
                    if is_horizontal:
                        wall_x = min(current[0], next_pos[0]) - 1
                        wall_y = current[1] + offset
                    else:
                        wall_x = current[0] + offset
                        wall_y = min(current[1], next_pos[1]) - 1
                        
                    if self.is_valid_wall_position(wall_x, wall_y, is_horizontal):
                        positions.append(((wall_x, wall_y), is_horizontal))
        
        # Add some random valid positions for variety
        for _ in range(5):
            x = random.randint(0, self.grid_size - 3)
            y = random.randint(0, self.grid_size - 3)
            is_horizontal = random.choice([True, False])
            if self.is_valid_wall_position(x, y, is_horizontal):
                positions.append(((x, y), is_horizontal))
        
        return positions

    def decide_move(self) -> Tuple[Tuple[int, int], bool, str]:
        """Decide the next wall placement and whether to use a skill"""
        strategic_positions = self.get_strategic_wall_positions()
        if not strategic_positions:
            return (0, 0), False, "none"  # No valid moves
            
        # Consider using Skill 1 (Double Walls)
        if self.skill_1_cooldown == 0 and len(strategic_positions) >= 2 and random.random() < self.difficulty:
            pos1, is_horizontal1 = strategic_positions[0]
            pos2, is_horizontal2 = strategic_positions[1]
            return pos1, is_horizontal1, "skill_1"
            
        # Consider using Skill 2 (Diagonal Walls)I
        if not self.skill_2_used and random.random() < self.difficulty:
            # Find a good position for diagonal wall
            path = self.find_shortest_path(self.player_pos, self.end_pos)
            if path and len(path) > 2:
                mid_point = path[len(path)//2]
                if 0 <= mid_point[0] < self.grid_size-2 and 0 <= mid_point[1] < self.grid_size-2:
                    return mid_point, True, "skill_2"
        
        # Consider using Skill 3 (Teleport Player)
        if self.skill_3_cooldown == 0 and random.random() < self.difficulty:
            # Only use if player is close to the goal
            path = self.find_shortest_path(self.player_pos, self.end_pos)
            if path and len(path) < self.grid_size // 2:
                return (0, 0), False, "skill_3"
        
        # Default to regular wall placement
        pos, is_horizontal = random.choice(strategic_positions)
        return pos, is_horizontal, "none" 