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

    def farthest_move(self):
        """Find the farthest valid move from the player's position."""
        farthest_distance = -1  # Start with a very small distance
        farthest_moves = []

        # Loop through all valid moves
        for dx, dy in self.valid_moves:
            # Calculate the new position
            new_x = self.player_pos_x + dx
            new_y = self.player_pos_y + dy
            
            # Calculate Manhattan distance
            distance = abs(new_x - self.player_pos_x) + abs(new_y - self.player_pos_y)
            
            # If this is the farthest distance found, update
            if distance > farthest_distance:
                farthest_distance = distance
                farthest_moves = [(dx, dy)]  # Reset to only this farthest move
            elif distance == farthest_distance:
                farthest_moves.append((dx, dy))  # Add this move if it equals the farthest distance

        return farthest_moves
    
    def move(self):
        #Move along the shortest path using A*.
        path = self.a_star_search()
        if path and len(path) > 1:
            moves = self.farthest_move()
            for x in moves:
                if x in path:
                    self.player_pos_x,self.player_pos_y = x
            if moves not in path:
               self.player_pos_x,self.player_pos_y = moves[0]
            
        
        print(path,"shortes path")
        print(moves,"farthes move")
        return (self.player_pos_x, self.player_pos_y)  # Return new position
