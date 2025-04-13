# A3 Game with AI

# Members:
# Banuag, Carl
# Deen, Marfred
# Ferolino, Jilliane
# Rodriguez, Andrea
# Rulete, Jeric
# Torres, John Angelo

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
        self.rounds_since_skill3 = 0
        self.total_steps = 0

    def update_state(self, walls: Set[Tuple[int, int]], player_pos: Tuple[int, int], rounds_since_last_skill3: int = None):
        """Update the AI's knowledge of the game state"""
        self.walls = walls
        self.player_pos = player_pos
        
        # Update skill 3 availability based on rounds
        if rounds_since_last_skill3 is not None:
            self.rounds_since_skill3 = rounds_since_last_skill3
            self.skill_3_available = rounds_since_last_skill3 >= 4
        
        # Other skills are always available when not used
        self.skill_2_available = True
        self.skill_1_available = True
        
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
                
                # Look for walls that might be blocking the path
                for wall in self.walls:
                    # Calculate manhattan distance to goal
                    distance_to_goal = abs(wall[0] - self.end_pos[0]) + abs(wall[1] - self.end_pos[1])
                    
                    # Temporarily remove wall to check if it creates a path
                    self.walls.remove(wall)
                    test_path = self.a_star_search(self.player_pos, self.end_pos)
                    self.walls.add(wall)
                    
                    if test_path:
                        # Prioritize walls that create shorter paths and are closer to the goal
                        path_length = len(test_path)
                        if path_length < best_path_length or (path_length == best_path_length and distance_to_goal < best_distance_to_goal):
                            best_wall = wall
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
        self.max_depth = 2  # Reduced depth for better performance
        self.move_cache = {}  # Cache for storing evaluated positions

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

    def evaluate_position(self, player_pos: Tuple[int, int], walls: Set[Tuple[int, int]]) -> float:
        """Evaluate the current game position from Maze Master's perspective"""
        # Cache key for this position
        cache_key = (player_pos, frozenset(walls))
        if cache_key in self.move_cache:
            return self.move_cache[cache_key]
            
        # Find shortest path for player
        player_path = self.find_shortest_path(player_pos, self.end_pos)
        
        if not player_path:
            self.move_cache[cache_key] = float('inf')
            return float('inf')  # Player is trapped, best case for Maze Master
            
        # Calculate score based on path length and wall coverage
        path_length = len(player_path)
        wall_coverage = len(walls) / (self.grid_size * self.grid_size)
        
        # Calculate distance from player to nearest wall
        min_wall_distance = float('inf')
        for wall in walls:
            dist = abs(wall[0] - player_pos[0]) + abs(wall[1] - player_pos[1])
            min_wall_distance = min(min_wall_distance, dist)
        
        if min_wall_distance == float('inf'):
            min_wall_distance = 0
            
        # Score components:
        # 1. Path length (longer is better for Maze Master)
        # 2. Wall coverage (more walls is better)
        # 3. Proximity to walls (closer walls are better)
        score = (path_length * 10 + 
                wall_coverage * 100 + 
                (1.0 / (min_wall_distance + 1)) * 50)
                
        self.move_cache[cache_key] = score
        return score

    def minimax(self, depth: int, alpha: float, beta: float, is_maximizing: bool, 
                player_pos: Tuple[int, int], walls: Set[Tuple[int, int]], 
                skill_1_available: bool, skill_2_available: bool, skill_3_available: bool) -> Tuple[float, Optional[Tuple[Tuple[int, int], bool, str]]]:
        """Minimax algorithm with alpha-beta pruning and optimizations"""
        # Early termination checks
        if depth == 0:
            return self.evaluate_position(player_pos, walls), None
            
        current_eval = self.evaluate_position(player_pos, walls)
        if current_eval == float('inf') or player_pos == self.end_pos:
            return current_eval, None

        if is_maximizing:  # Maze Master's turn
            max_eval = float('-inf')
            best_move = None
            
            # Get strategic positions instead of trying all possible positions
            wall_positions = self.get_strategic_wall_positions()[:5]  # Limit to top 5 positions
            
            for wall_pos, is_horizontal in wall_positions:
                # Create new wall set with the new wall
                new_walls = walls.copy()
                if is_horizontal:
                    wall_tiles = [(wall_pos[0] + i, wall_pos[1]) for i in range(3)]
                else:
                    wall_tiles = [(wall_pos[0], wall_pos[1] + i) for i in range(3)]
                    
                if all(0 <= wx < self.grid_size and 0 <= wy < self.grid_size and 
                      (wx, wy) not in walls for wx, wy in wall_tiles):
                    new_walls.update(wall_tiles)
                    
                    # Only try skills if they're available and would be useful
                    skills_to_try = ["none"]
                    if skill_1_available and len(wall_positions) >= 2:
                        skills_to_try.append("skill_1")
                    if skill_2_available and not self.skill_2_used:
                        skills_to_try.append("skill_2")
                    if skill_3_available and self.skill_3_cooldown == 0:
                        skills_to_try.append("skill_3")
                        
                    for skill in skills_to_try:
                        eval_score, _ = self.minimax(depth - 1, alpha, beta, False, player_pos, new_walls, 
                                                   skill_1_available and skill != "skill_1",
                                                   skill_2_available and skill != "skill_2",
                                                   skill_3_available and skill != "skill_3")
                        
                        if eval_score > max_eval:
                            max_eval = eval_score
                            best_move = (wall_pos, is_horizontal, skill)
                        
                        alpha = max(alpha, eval_score)
                        if beta <= alpha:
                            break
                            
            return max_eval, best_move
            
        else:  # Runner's turn
            min_eval = float('inf')
            best_move = None
            
            # Get valid moves for runner
            valid_moves = self.get_valid_moves(player_pos)
            
            # Sort moves by distance to goal to check most promising moves first
            valid_moves.sort(key=lambda pos: abs(pos[0] - self.end_pos[0]) + abs(pos[1] - self.end_pos[1]))
            
            for move in valid_moves[:4]:  # Limit to 4 best moves for performance
                eval_score, _ = self.minimax(depth - 1, alpha, beta, True, move, walls, 
                                           skill_1_available, skill_2_available, skill_3_available)
                
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = move
                
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
                    
            return min_eval, best_move

    def decide_move(self, walls_placed: int) -> Tuple[Tuple[int, int], bool, str]:
        """Decide the next wall placement and whether to use a skill"""
        # Clear the move cache before each decision
        self.move_cache.clear()
        
        try:
            # First try minimax with alpha-beta pruning with a timeout
            _, minimax_move = self.minimax(
                self.max_depth, float('-inf'), float('inf'), True,
                self.player_pos, self.walls,
                self.skill_1_cooldown == 0,
                not self.skill_2_used,
                self.skill_3_cooldown == 0
            )
            
            if minimax_move:
                return minimax_move
        except Exception:
            # If minimax fails, fall back to original strategy
            pass
            
        # Fall back to original strategy
        strategic_positions = self.get_strategic_wall_positions()
        if not strategic_positions:
            return (0, 0), False, "none"
            
        # Rest of the original strategy remains unchanged
        if self.skill_1_cooldown == 0 and len(strategic_positions) >= 2 and random.random() < self.difficulty:
            pos1, is_horizontal1 = strategic_positions[0]
            return pos1, is_horizontal1, "skill_1"
            
        if not self.skill_2_used and random.random() < self.difficulty:
            path = self.find_shortest_path(self.player_pos, self.end_pos)
            if path and len(path) > 2:
                mid_point = path[len(path)//2]
                if 0 <= mid_point[0] < self.grid_size-2 and 0 <= mid_point[1] < self.grid_size-2:
                    self.skill_2_used = True
                    return mid_point, True, "skill_2"
        
        if self.skill_3_cooldown == 0 and random.random() < self.difficulty:
            path = self.find_shortest_path(self.player_pos, self.end_pos)
            if path and len(path) < self.grid_size // 2:
                return (0, 0), False, "skill_3"
        
        pos, is_horizontal = random.choice(strategic_positions)
        return pos, is_horizontal, "none"

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