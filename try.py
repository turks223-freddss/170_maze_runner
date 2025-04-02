class PlayerAI:
    def __init__(self, valid_moves, player_pos_x, player_pos_y, walls):
        self.valid_moves = valid_moves  # List of possible move directions (dx, dy)
        self.player_pos_x = player_pos_x
        self.player_pos_y = player_pos_y

    def farthest_move(self):
        """Find the farthest valid move from the player's position."""
        # Calculate the Manhattan distance for each valid move
        farthest_moves = []
        max_distance = -1  # Start with a very small distance
        
        for dx, dy in self.valid_moves:
            # Calculate new position after applying the move
            new_x = self.player_pos_x + dx
            new_y = self.player_pos_y + dy
            # Calculate Manhattan distance from player's current position
            distance = abs(new_x - self.player_pos_x) + abs(new_y - self.player_pos_y)
            
            if distance > max_distance:
                max_distance = distance
                farthest_moves = [(dx, dy)]  # Start a new list with this move
            elif distance == max_distance:
                farthest_moves.append((dx, dy))  # Add this move if it's equally far
        
        return farthest_moves


# Example usage:
valid_moves = [(1, 0), (2, 0), (3, 0), (4, 0), (0, 1), (0, 2), (0, 3), (0, 4)]
player_pos_x = 0
player_pos_y = 0

player_ai = PlayerAI(valid_moves, player_pos_x, player_pos_y)
farthest_moves = player_ai.farthest_move()

print(farthest_moves)
