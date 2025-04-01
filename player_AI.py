import heapq
import random

class PlayerAI:
    def __init__(self, valid_moves, player_pos_x, player_pos_y, walls):
        self.grid = [[0 for _ in range(24)] for _ in range(24)]
        self.valid_moves = valid_moves  # List of possible move directions (dx, dy)
        self.player_pos_x = player_pos_x
        self.player_pos_y = player_pos_y
        self.goalx = 23
        self.goaly = 23

        # Mark walls on the grid
        for wx, wy in walls:
            self.grid[wy][wx] = 1  # Assuming 1 represents a wall

    def heuristic(self, x, y):
        """Manhattan distance heuristic."""
        return abs(x - self.goalx) + abs(y - self.goaly)

    def a_star_search(self):
        """Find the shortest path to the goal using A* algorithm."""
        start = (self.player_pos_x, self.player_pos_y)
        goal = (self.goalx, self.goaly)
        
        open_set = []
        heapq.heappush(open_set, (0, start))  # (priority, position)
        
        came_from = {start: None}
        g_score = {start: 0}
        f_score = {start: self.heuristic(*start)}
        
        while open_set:
            _, current = heapq.heappop(open_set)

            if current == goal:
                path = []
                while current:
                    path.append(current)
                    current = came_from[current]
                return path[::-1]  # Return the path in correct order

            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:  # Move in 4 directions
                neighbor = (current[0] + dx, current[1] + dy)

                if (0 <= neighbor[0] < 24 and 0 <= neighbor[1] < 24 and
                        self.grid[neighbor[1]][neighbor[0]] != 1):  # Check bounds and walls
                    tentative_g_score = g_score[current] + 1
                    
                    if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                        came_from[neighbor] = current
                        g_score[neighbor] = tentative_g_score
                        f_score[neighbor] = tentative_g_score + self.heuristic(*neighbor)
                        heapq.heappush(open_set, (f_score[neighbor], neighbor))

        return None  # No path found

    def move(self):
        """Move along the shortest path using A*."""
        path = self.a_star_search()
        if path and len(path) > 1:
            self.player_pos_x, self.player_pos_y = path[1]  # Move to the next step in path
        
        return (self.player_pos_x, self.player_pos_y)  # Return new position
