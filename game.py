import pygame
import random

# Constants
GRID_SIZE = 24
TILE_SIZE = 25
SCREEN_WIDTH = GRID_SIZE * TILE_SIZE
SCREEN_HEIGHT = GRID_SIZE * TILE_SIZE + 50

# Colors
WHITE = (255, 255, 255)
OFF_WHITE = (245, 245, 220)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
GRAY = (169, 169, 169)
BLUE = (0, 0, 255)
LIGHT_BLUE = (173, 216, 230)
YELLOW = (255, 255, 0, 160)
LIGHT_ORANGE = (255, 200, 0, 100)
ACTIVE_SKILL_COLOR = (50, 200, 50)
WALL_BREAK_COLOR = (255, 100, 0)
DIAGONAL_WALL_COLOR = (100, 50, 200)  # Purple for diagonal walls

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Turn-Based Maze Game")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 30)
small_font = pygame.font.Font(None, 20)

# Game state
class GameState:
    def __init__(self):
        self.player_x, self.player_y = 0, 0
        self.end_x, self.end_y = GRID_SIZE - 1, GRID_SIZE - 1
        self.walls = set()
        self.walls_placed = 0
        self.player_turns = 0
        self.player_skill_active = False
        self.maze_skill_active = False
        self.maze_skill_cooldown = 0
        self.skill_2_active = False
        self.skill_2_used = False
        self.skill_3_active = False
        self.skill_3_used = False
        self.skill_3_available = False
        self.game_won = False
        self.maze_skill_2_active = False
        self.maze_skill_2_used = False
        self.maze_skill_3_active = False
        self.maze_skill_3_cooldown = 0
        self.MAZE_SKILL_3_COOLDOWN_MAX = 3
        self.total_player_steps = 0
        self.rounds_since_last_skill3 = 0
        self.animation_time = 0
        self.show_turn_notification = False
        self.turn_notification_timer = 0
        self.turn_notification_duration = 60
        self.last_turn_state = True
        self.skill_1_button = None
        self.skill_2_button = None
        self.skill_3_button = None
        self.skill_4_button = None
        self.maze_skill1_active = False
        self.maze_skill1_cooldown = 0
        
        self.update_button_positions()
    
    def update_button_positions(self):
        button_width = 80
        button_height = 25
        spacing = 10

        self.skill_1_button = pygame.Rect(spacing, 10, button_width, button_height)
        self.skill_2_button = pygame.Rect(spacing + button_width + spacing, 10, button_width, button_height)
        self.skill_3_button = pygame.Rect(SCREEN_WIDTH - (2 * (button_width + spacing)), 10, button_width, button_height)
        self.skill_4_button = pygame.Rect(SCREEN_WIDTH - (button_width + spacing), 10, button_width, button_height)

game_state = GameState()

def draw_buttons():
    if game_state.player_turns < 4:
        # Player's turn buttons
        skill_1_color = ACTIVE_SKILL_COLOR if game_state.player_skill_active else BLUE
        pygame.draw.rect(screen, skill_1_color, game_state.skill_1_button)
        
        if game_state.skill_2_active:
            skill_2_color = ACTIVE_SKILL_COLOR
        elif game_state.skill_2_used:
            skill_2_color = GRAY
        else:
            skill_2_color = BLUE
        pygame.draw.rect(screen, skill_2_color, game_state.skill_2_button)
        
        if game_state.skill_3_active:
            skill_3_color = WALL_BREAK_COLOR
        elif not game_state.skill_3_available or game_state.skill_3_used:
            skill_3_color = GRAY
        else:
            skill_3_color = BLUE
        pygame.draw.rect(screen, skill_3_color, game_state.skill_3_button)
        
        pygame.draw.rect(screen, BLUE, game_state.skill_4_button)
        
        # Draw button labels
        screen.blit(font.render("Skill 1", True, WHITE), (game_state.skill_1_button.x + 10, game_state.skill_1_button.y + 5))
        screen.blit(font.render("Skill 2", True, WHITE), (game_state.skill_2_button.x + 10, game_state.skill_2_button.y + 5))
        screen.blit(font.render("Skill 3", True, WHITE), (game_state.skill_3_button.x + 10, game_state.skill_3_button.y + 5))
        screen.blit(font.render("Skill 4", True, WHITE), (game_state.skill_4_button.x + 10, game_state.skill_4_button.y + 5))
        
        # Draw active skill indicators
        if game_state.player_skill_active:
            draw_active_indicator(game_state.skill_1_button)
        if game_state.skill_2_active:
            draw_active_indicator(game_state.skill_2_button)
        if game_state.skill_3_active:
            draw_active_indicator(game_state.skill_3_button, WALL_BREAK_COLOR)
        
        # Show "Unlocked" indicator for skill 3
        if game_state.skill_3_available and not game_state.skill_3_used and not game_state.skill_3_active:
            draw_unlocked_indicator(game_state.skill_3_button)
    else:
        # Maze Master's turn buttons
        draw_buttons_maze_master()

def draw_active_indicator(button, color=WHITE):
    skill_text = small_font.render("ACTIVE", True, color)
    text_x = button.x + (button.width - skill_text.get_width()) // 2
    screen.blit(skill_text, (text_x, button.y + button.height + 2))

def draw_unlocked_indicator(button):
    unlock_text = small_font.render("UNLOCKED", True, WALL_BREAK_COLOR)
    text_x = button.x + (button.width - unlock_text.get_width()) // 2
    screen.blit(unlock_text, (text_x, button.y + button.height + 2))

def draw_buttons_maze_master():
    # Skill 1 button (Place Two Walls)
    skill_1_color = ACTIVE_SKILL_COLOR if game_state.maze_skill_active else BLUE
    pygame.draw.rect(screen, skill_1_color, game_state.skill_1_button)
    
    # Skill 2 button (Diagonal Walls)
    if game_state.maze_skill_2_active:
        skill_2_color = ACTIVE_SKILL_COLOR
    elif game_state.maze_skill_2_used:
        skill_2_color = GRAY
    else:
        skill_2_color = DIAGONAL_WALL_COLOR  # Purple color for diagonal wall skill
    pygame.draw.rect(screen, skill_2_color, game_state.skill_2_button)
    
    # Skill 3 button (Wall Break)
    # Orange if active, gray if not available or used up, blue if available
    if game_state.player_turns >= 4:  # During Maze Master's turn
        if game_state.maze_skill_3_active:
            skill_3_color = ACTIVE_SKILL_COLOR
        elif game_state.maze_skill_3_cooldown > 0:
            skill_3_color = GRAY
        else:
            skill_3_color = BLUE
    else:  # During Player's turn - keep existing player skill 3 logic
        if game_state.skill_3_active:
            skill_3_color = WALL_BREAK_COLOR
        elif not game_state.skill_3_available or game_state.skill_3_used:
            skill_3_color = GRAY
        else:
            skill_3_color = BLUE
    
    pygame.draw.rect(screen, skill_3_color, game_state.skill_3_button)
    
    pygame.draw.rect(screen, BLUE, game_state.skill_4_button)

    #Maze Master Skills (or merge nalang with the player skills?)
    
    if not game_state.player_turns < 4:
        if game_state.maze_skill1_active:
            skill_1_color = ACTIVE_SKILL_COLOR
        elif game_state.maze_skill1_cooldown:
            skill_1_color = GRAY
        elif not game_state.maze_skill1_active and game_state.maze_skill1_cooldown:
            skill_1_color = BLUE
        pygame.draw.rect(screen, skill_1_color, game_state.skill_1_button)
        
    # Draw button labels
    screen.blit(font.render("Skill 1", True, WHITE), (game_state.skill_1_button.x + 10, game_state.skill_1_button.y + 5))
    screen.blit(font.render("Skill 2", True, WHITE), (game_state.skill_2_button.x + 10, game_state.skill_2_button.y + 5))
    screen.blit(font.render("Skill 3", True, WHITE), (game_state.skill_3_button.x + 10, game_state.skill_3_button.y + 5))
    screen.blit(font.render("Skill 4", True, WHITE), (game_state.skill_4_button.x + 10, game_state.skill_4_button.y + 5))
    
    # Draw active skill indicators
    if game_state.maze_skill_active:
        draw_active_indicator(game_state.skill_1_button)
    if game_state.maze_skill_2_active:
        draw_active_indicator(game_state.skill_2_button)

def draw_turn_text():
    if game_state.game_won:
        turn_text = "Congratulations!"
    else:
        turn_text = "Player's Turn" if game_state.player_turns < 4 else "Maze Master's Turn"
    
    base_text = font.render(turn_text, True, BLUE)
    x_pos = SCREEN_WIDTH // 2 - base_text.get_width() // 2
    y_pos = 15
    screen.blit(base_text, (x_pos, y_pos))
    
    if game_state.player_skill_active or game_state.skill_2_active or game_state.skill_3_active:
        active_skill = ""
        active_color = ACTIVE_SKILL_COLOR
        
        if game_state.player_skill_active:
            active_skill = "Extended Move"
        elif game_state.skill_2_active:
            active_skill = "Teleport"
        elif game_state.skill_3_active:
            active_skill = "Wall Break"
            active_color = WALL_BREAK_COLOR
            
        skill_info = small_font.render(f"{active_skill} Active", True, active_color)
        x_pos = SCREEN_WIDTH // 2 - skill_info.get_width() // 2
        screen.blit(skill_info, (x_pos, y_pos + 20))

    # Add active skill info (Maze Master)
    if game_state.maze_skill1_active:
        active_skill = ""
        active_color = ACTIVE_SKILL_COLOR
        
        if game_state.maze_skill1_active:
            active_skill = "Double Walls"

        skill_info = small_font.render(f"{active_skill} Active", True, active_color)
        x_pos = SCREEN_WIDTH // 2 - skill_info.get_width() // 2
        screen.blit(skill_info, (x_pos, y_pos + 20))

def show_turn_change_notification():
    notification_text = "Your Turn!" if game_state.player_turns < 4 else "Maze Master's Turn!"
    notification_surface = pygame.Surface((350, 80), pygame.SRCALPHA)
    
    if game_state.turn_notification_timer < 15:
        alpha = min(255, game_state.turn_notification_timer * 17)
    elif game_state.turn_notification_timer > game_state.turn_notification_duration - 15:
        alpha = max(0, 255 - (game_state.turn_notification_timer - (game_state.turn_notification_duration - 15)) * 17)
    else:
        alpha = 255
        
    notification_surface.fill((0, 0, 180, alpha))
    big_font = pygame.font.Font(None, 40)
    text = big_font.render(notification_text, True, WHITE)
    text_x = (notification_surface.get_width() - text.get_width()) // 2
    text_y = (notification_surface.get_height() - text.get_height()) // 2
    notification_surface.blit(text, (text_x, text_y))
    
    notification_x = (SCREEN_WIDTH - notification_surface.get_width()) // 2
    notification_y = (SCREEN_HEIGHT - notification_surface.get_height()) // 2
    screen.blit(notification_surface, (notification_x, notification_y))
    
    game_state.turn_notification_timer += 1
    if game_state.turn_notification_timer >= game_state.turn_notification_duration:
        game_state.show_turn_notification = False
        game_state.turn_notification_timer = 0

def get_valid_moves(x, y, max_distance):
    valid_tiles = []
    
    if game_state.skill_2_active:
        for dx in range(-max_distance, max_distance + 1):
            for dy in range(-max_distance, max_distance + 1):
                new_x, new_y = x + dx, y + dy
                if (0 <= new_x < GRID_SIZE and 0 <= new_y < GRID_SIZE and 
                    (new_x, new_y) not in game_state.walls and (new_x, new_y) != (x, y)):
                    valid_tiles.append((new_x, new_y))
    else:
        for dx in range(-max_distance, max_distance + 1):
            for dy in range(-max_distance, max_distance + 1):
                if abs(dx) + abs(dy) <= max_distance and (dx != 0 or dy != 0):
                    new_x, new_y = x + dx, y + dy
                    if (0 <= new_x < GRID_SIZE and 0 <= new_y < GRID_SIZE and 
                        (new_x, new_y) not in game_state.walls):
                        valid_tiles.append((new_x, new_y))
    
    return valid_tiles

def is_valid_wall_position(x, y, is_horizontal):
    if is_horizontal:
        wall_positions = [(x + i, y) for i in range(3)]
    else:
        wall_positions = [(x, y + i) for i in range(3)]
    
    valid = all(0 <= wx < GRID_SIZE and 0 <= wy < GRID_SIZE and 
               (wx, wy) != (game_state.player_x, game_state.player_y) and 
               (wx, wy) != (game_state.end_x, game_state.end_y) and
               (wx, wy) not in game_state.walls
               for wx, wy in wall_positions)
    
    return valid

def is_valid_diagonal_wall_position(start_x, start_y, direction):
    """Check if a diagonal wall can be placed at a specific position."""
    wall_positions = []
    for i in range(3):
        if direction == "uldr":  # Upper left to lower right
            wall_positions.append((start_x + i, start_y + i))
        else:  # Upper right to lower left
            wall_positions.append((start_x - i, start_y + i))
    
    # Check if all positions are valid
    valid = all(0 <= wx < GRID_SIZE and 0 <= wy < GRID_SIZE and 
               (wx, wy) != (game_state.player_x, game_state.player_y) and 
               (wx, wy) != (game_state.end_x, game_state.end_y) and
               (wx, wy) not in game_state.walls
               for wx, wy in wall_positions)
    
    return valid, wall_positions

def highlight_clickable_areas():
    highlight_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    
    if game_state.player_turns < 4:
        if game_state.skill_3_active:
            for wx, wy in game_state.walls:
                pygame.draw.rect(highlight_surface, (255, 100, 0, 100), 
                               (wx * TILE_SIZE, wy * TILE_SIZE + 50, TILE_SIZE, TILE_SIZE))
        else:
            max_move = 4 if game_state.player_skill_active else 1
            max_teleport = 2 if game_state.skill_2_active else 0
            
            if game_state.skill_2_active:
                valid_tiles = get_valid_moves(game_state.player_x, game_state.player_y, max_teleport)
                highlight_color = (255, 255, 0, 100)
            else:
                valid_tiles = get_valid_moves(game_state.player_x, game_state.player_y, max_move)
                highlight_color = (0, 255, 0, 100)
                
            for tx, ty in valid_tiles:
                pygame.draw.rect(highlight_surface, highlight_color, 
                               (tx * TILE_SIZE, ty * TILE_SIZE + 50, TILE_SIZE, TILE_SIZE))
    else:
        if game_state.maze_skill_2_active:
            # Highlight all positions that can be starting points for diagonal walls
            for x in range(GRID_SIZE):
                for y in range(GRID_SIZE):
                    if (x, y) == (game_state.player_x, game_state.player_y) or (x, y) == (game_state.end_x, game_state.end_y) or (x, y) in game_state.walls:
                        continue
                    
                    # Check for both diagonal directions
                    uldr_valid, _ = is_valid_diagonal_wall_position(x, y, "uldr")
                    urdl_valid, _ = is_valid_diagonal_wall_position(x, y, "urdl")
                    
                    if uldr_valid or urdl_valid:
                        pygame.draw.rect(highlight_surface, DIAGONAL_WALL_COLOR + (100,), 
                                       (x * TILE_SIZE, y * TILE_SIZE + 50, TILE_SIZE, TILE_SIZE))
        else:
            is_horizontal = not pygame.key.get_pressed()[pygame.K_LSHIFT]
            
            for x in range(GRID_SIZE):
                for y in range(GRID_SIZE):
                    if (x, y) == (game_state.player_x, game_state.player_y) or (x, y) == (game_state.end_x, game_state.end_y) or (x, y) in game_state.walls:
                        continue
                    
                    if is_valid_wall_position(x, y, is_horizontal):
                        if is_horizontal:
                            wall_positions = [(x + i, y) for i in range(3)]
                        else:
                            wall_positions = [(x, y + i) for i in range(3)]
                        
                        for wx, wy in wall_positions:
                            pygame.draw.rect(highlight_surface, LIGHT_ORANGE, 
                                           (wx * TILE_SIZE, wy * TILE_SIZE + 50, TILE_SIZE, TILE_SIZE))
                    else:
                        if (is_horizontal and x + 2 < GRID_SIZE) or (not is_horizontal and y + 2 < GRID_SIZE):
                            pygame.draw.rect(highlight_surface, (255, 0, 0, 80), 
                                           (x * TILE_SIZE, y * TILE_SIZE + 50, TILE_SIZE, TILE_SIZE))
    
    screen.blit(highlight_surface, (0, 0))

def draw_skill_info():
    if game_state.player_turns < 4:
        info_text = ""
        info_color = WHITE
        
        if game_state.player_skill_active:
            info_text = "Skill 1: Extended Move (4 tiles)"
        elif game_state.skill_2_active:
            info_text = "Skill 2: Teleport (within 2 tiles)"
        elif game_state.skill_3_active:
            info_text = "Skill 3: Wall Break (click a wall to break it)"
            info_color = WALL_BREAK_COLOR
        
        if info_text:
            draw_info_panel(info_text, info_color)
        elif game_state.skill_3_available and not game_state.skill_3_used and not game_state.skill_3_active:
            draw_info_panel("Skill 3 (Wall Break) is now available!", WALL_BREAK_COLOR)

def draw_info_panel(text, color):
    skill_info = font.render(text, True, color)
    text_width, text_height = skill_info.get_size()
    padding = 10
    bg_width = text_width + 2 * padding
    bg_height = text_height + 2 * padding
    info_surface = pygame.Surface((bg_width, bg_height), pygame.SRCALPHA)
    info_surface.fill((0, 0, 0, 200))
    
    x_pos = (SCREEN_WIDTH - bg_width) // 2
    y_pos = SCREEN_HEIGHT - 40
    screen.blit(info_surface, (x_pos, y_pos))
    
    text_x = x_pos + padding
    text_y = y_pos + padding
    screen.blit(skill_info, (text_x, text_y))

def reset_game():
    game_state.__init__()
    game_state.show_turn_notification = True

def handle_player_click(mx, my):
    clicked_x = mx // TILE_SIZE
    clicked_y = (my - 50) // TILE_SIZE
    
    if game_state.skill_3_active and (clicked_x, clicked_y) in game_state.walls:
        game_state.walls.remove((clicked_x, clicked_y))
        game_state.skill_3_active = False
        game_state.skill_3_used = True
        game_state.player_turns += 1
        game_state.total_player_steps += 1
        return
    
    if game_state.skill_2_active:
        if abs(clicked_x - game_state.player_x) <= 2 and abs(clicked_y - game_state.player_y) <= 2 and (clicked_x, clicked_y) not in game_state.walls:
            game_state.player_x, game_state.player_y = clicked_x, clicked_y
            game_state.skill_2_active = False
            game_state.skill_2_used = True
            game_state.player_turns += 1
            game_state.total_player_steps += 1
        return
    
    max_move = 4 if game_state.player_skill_active else 1
    if (abs(clicked_x - game_state.player_x) + abs(clicked_y - game_state.player_y) <= max_move) and (clicked_x, clicked_y) not in game_state.walls:
        game_state.player_x, game_state.player_y = clicked_x, clicked_y
        game_state.player_turns += 1
        game_state.total_player_steps += 1
        game_state.player_skill_active = False

def handle_maze_master_click(mx, my):
    clicked_x = mx // TILE_SIZE
    clicked_y = (my - 50) // TILE_SIZE
    
    if (clicked_x, clicked_y) == (game_state.player_x, game_state.player_y) or (clicked_x, clicked_y) == (game_state.end_x, game_state.end_y):
        return
    
    if game_state.maze_skill_active:
        if game_state.walls_placed < 2:
            if pygame.key.get_pressed()[pygame.K_LSHIFT]:
                wall_positions = [(clicked_x, clicked_y + i) for i in range(3)]
            else:
                wall_positions = [(clicked_x + i, clicked_y) for i in range(3)]
            game_state.walls_placed += 1
        
        valid = all(0 <= wx < GRID_SIZE and 0 <= wy < GRID_SIZE and 
                    (wx, wy) != (game_state.player_x, game_state.player_y) and 
                    (wx, wy) != (game_state.end_x, game_state.end_y) and 
                    (wx, wy) not in game_state.walls for wx, wy in wall_positions)
        
        if valid:
            game_state.walls.update(wall_positions)
            if game_state.walls_placed >= 2:
                game_state.player_turns = 0
                game_state.walls_placed = 0
                game_state.maze_skill_active = False
                game_state.show_turn_notification = True
                game_state.turn_notification_timer = 0
                game_state.rounds_since_last_skill3 += 1
    elif game_state.maze_skill_2_active:
        # Determine direction based on shift key
        direction = "urdl" if pygame.key.get_pressed()[pygame.K_LSHIFT] else "uldr"
        valid, wall_positions = is_valid_diagonal_wall_position(clicked_x, clicked_y, direction)
        
        if valid:
            game_state.walls.update(wall_positions)
            game_state.maze_skill_2_active = False
            game_state.maze_skill_2_used = True
            game_state.player_turns = 0
            game_state.show_turn_notification = True
            game_state.turn_notification_timer = 0
            game_state.rounds_since_last_skill3 += 1
    else:
        if pygame.key.get_pressed()[pygame.K_LSHIFT]:
            wall_positions = [(clicked_x, clicked_y + i) for i in range(3)]
        else:
            wall_positions = [(clicked_x + i, clicked_y) for i in range(3)]
        
        valid = all(0 <= wx < GRID_SIZE and 0 <= wy < GRID_SIZE and 
                    (wx, wy) != (game_state.player_x, game_state.player_y) and 
                    (wx, wy) != (game_state.end_x, game_state.end_y) and 
                    (wx, wy) not in game_state.walls for wx, wy in wall_positions)
        
        if valid:
            game_state.walls.update(wall_positions)
            game_state.player_turns = 0
            game_state.show_turn_notification = True
            game_state.turn_notification_timer = 0
            game_state.rounds_since_last_skill3 += 1

        if game_state.maze_skill_cooldown > 0:
            game_state.maze_skill_cooldown -= 1

# Show turn notification at game start
game_state.show_turn_notification = True

# Add this new function after the other skill-related functions
def teleport_player_random():
    """
    Teleports the player to a random valid location on the grid.
    
    Returns:
        bool: True if teleport was successful, False if no valid positions found
    """
    # Get all valid positions (excluding walls and end point)
    valid_positions = [
        (x, y) for x in range(GRID_SIZE) 
        for y in range(GRID_SIZE)
        if (x, y) not in game_state.walls and (x, y) != (game_state.end_x, game_state.end_y)
    ]
    
    if valid_positions:
        game_state.player_x, game_state.player_y = random.choice(valid_positions)
        return True
    return False

# Game loop
running = True
while running:
    screen.fill(OFF_WHITE)

    # Check if the player has reached the goal
    if game_state.player_x == game_state.end_x and game_state.player_y == game_state.end_y:
        game_state.game_won = True
    
    # Check if Skill 3 should become available
    if game_state.rounds_since_last_skill3 >= 4 and (game_state.skill_3_used or not game_state.skill_3_available):
        game_state.skill_3_available = True
        game_state.skill_3_used = False
        game_state.rounds_since_last_skill3 = 0

    if game_state.game_won:
        draw_turn_text()
        pygame.display.flip()
        pygame.time.delay(2000)
        reset_game()
        continue

    # Draw the grid
    for x in range(0, SCREEN_WIDTH, TILE_SIZE):
        for y in range(50, SCREEN_HEIGHT, TILE_SIZE):
            pygame.draw.rect(screen, BLACK, pygame.Rect(x, y, TILE_SIZE, TILE_SIZE), 1)
    
    # Draw walls
    for wx, wy in game_state.walls:
        pygame.draw.rect(screen, GRAY, (wx * TILE_SIZE, wy * TILE_SIZE + 50, TILE_SIZE, TILE_SIZE))
    
    # Highlight valid moves
    highlight_clickable_areas()
    
    # Draw player and end positions
    pygame.draw.rect(screen, GREEN, (game_state.player_x * TILE_SIZE, game_state.player_y * TILE_SIZE + 50, TILE_SIZE, TILE_SIZE))
    pygame.draw.rect(screen, RED, (game_state.end_x * TILE_SIZE, game_state.end_y * TILE_SIZE + 50, TILE_SIZE, TILE_SIZE))
    
    # Draw UI elements
    draw_turn_text()
    draw_buttons()
    draw_skill_info()
    
    # Check if turn state has changed
    current_turn_state = game_state.player_turns < 4
    if current_turn_state != game_state.last_turn_state:
        game_state.show_turn_notification = True
        game_state.turn_notification_timer = 0
        game_state.last_turn_state = current_turn_state
    
    # Show turn notification if active
    if game_state.show_turn_notification:
        show_turn_change_notification()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.VIDEORESIZE:
            SCREEN_WIDTH, SCREEN_HEIGHT = event.w, event.h
            screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
            game_state.update_button_positions()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            
            # Handle button clicks
            if game_state.skill_1_button.collidepoint(mx, my):
                if game_state.player_turns < 4:
                    game_state.player_skill_active = True
                elif game_state.player_turns >= 4 and game_state.maze_skill_cooldown == 0:
                    game_state.maze_skill_active = True
                    game_state.maze_skill_cooldown = 3
                continue

            if game_state.skill_1_button.collidepoint(mx, my) and game_state.player_turns >= 4 and game_state.maze_skill_cooldown != 0:
                print("Skill is on cooldown!")  # Removable (This was just for debugging purposes)
                continue

            if game_state.skill_2_button.collidepoint(mx, my) and not game_state.skill_2_used and game_state.player_turns < 4:
                game_state.skill_2_active = not game_state.skill_2_active
                if game_state.skill_2_active:
                    game_state.player_skill_active = False
                    game_state.skill_3_active = False
                continue
                
            if game_state.skill_3_button.collidepoint(mx, my) and game_state.skill_3_available and not game_state.skill_3_used and game_state.player_turns < 4:
                game_state.skill_3_active = not game_state.skill_3_active
                if game_state.skill_3_active:
                    game_state.player_skill_active = False
                    game_state.skill_2_active = False
                continue
            
            # Maze Master's Skill 3 (Random Teleport)
            if (game_state.skill_3_button.collidepoint(mx, my) and 
                game_state.player_turns >= 4 and  # Maze Master's turn
                game_state.maze_skill_3_cooldown == 0):  # Skill not on cooldown
                
                game_state.maze_skill_3_active = True
                if teleport_player_random():
                    # Apply cooldown and end turn
                    game_state.maze_skill_3_cooldown = game_state.MAZE_SKILL_3_COOLDOWN_MAX
                    game_state.player_turns = 0
                    game_state.show_turn_notification = True
                    game_state.turn_notification_timer = 0
                game_state.maze_skill_3_active = False
                continue
            
            if my < 50:
                continue

            clicked_x = mx // TILE_SIZE
            clicked_y = (my - 50) // TILE_SIZE
            
            # Wall break skill logic
            if game_state.skill_3_active and (clicked_x, clicked_y) in game_state.walls:
                game_state.walls.remove((clicked_x, clicked_y))  # Remove the clicked wall
                game_state.skill_3_active = False  # Deactivate wall break mode
                game_state.skill_3_used = True  # Mark skill as used
                game_state.player_turns += 1  # Use a turn after breaking a wall
                game_state.total_player_steps += 1  # Increment total steps
                continue
            
            # If Skill 2 is active, allow teleporting within 2x2 area
            if game_state.skill_2_active:
                if abs(clicked_x - game_state.player_x) <= 2 and abs(clicked_y - game_state.player_y) <= 2 and (clicked_x, clicked_y) not in game_state.walls:
                    game_state.player_x, game_state.player_y = clicked_x, clicked_y
                    game_state.skill_2_active = False  # Deactivate teleport mode
                    game_state.skill_2_used = True  # Mark skill as used
                    game_state.player_turns += 1  # Use a turn after teleporting
                    game_state.total_player_steps += 1  # Increment total steps
                continue
            
            if game_state.player_turns < 4:
                max_move = 4 if game_state.player_skill_active else 1
                
                if (abs(clicked_x - game_state.player_x) + abs(clicked_y - game_state.player_y) <= max_move) and (clicked_x, clicked_y) not in game_state.walls:
                    game_state.player_x, game_state.player_y = clicked_x, clicked_y
                    game_state.player_turns += 1
                    game_state.total_player_steps += 1  # Increment total steps
                    game_state.player_skill_active = False  # Deactivate skill after use

            else:   # Maze master's Turn

                if (clicked_x, clicked_y) != (game_state.player_x, game_state.player_y) and (clicked_x, clicked_y) != (game_state.end_x, game_state.end_y):
                    if game_state.maze_skill_active:   # Skill 1 is activated (Maze master)

                        if game_state.walls_placed < 2:    # Required to place 2 walls
                            if pygame.key.get_pressed()[pygame.K_LSHIFT]:
                                wall_positions = [(clicked_x, clicked_y + i) for i in range(3)]
                            else:
                                wall_positions = [(clicked_x + i, clicked_y) for i in range(3)]
                            game_state.walls_placed += 1
                        
                        valid = all(0 <= wx < GRID_SIZE and 0 <= wy < GRID_SIZE and 
                                    (wx, wy) != (game_state.player_x, game_state.player_y) and (wx, wy) != (game_state.end_x, game_state.end_y) and 
                                    (wx, wy) not in game_state.walls for wx, wy in wall_positions)
                        
                        if valid:
                            game_state.walls.update(wall_positions)
                            if game_state.walls_placed < 2:    # Checks if 2 walls have been placed
                                game_state.player_turns += 1
                            else:                   # 2 walls have been placed, exit skill and end turn.
                                game_state.player_turns = 0
                                game_state.walls_placed = 0
                                game_state.maze_skill_active = False
                                
                        # Show turn notification when Maze Master completes their turn
                        game_state.show_turn_notification = True
                        game_state.turn_notification_timer = 0
                        game_state.rounds_since_last_skill3 += 1
                            
                    else:   # Basic Maze master movement
                        
                        if pygame.key.get_pressed()[pygame.K_LSHIFT]:
                            wall_positions = [(clicked_x, clicked_y + i) for i in range(3)]
                        else:
                            wall_positions = [(clicked_x + i, clicked_y) for i in range(3)]
                        
                        valid = all(0 <= wx < GRID_SIZE and 0 <= wy < GRID_SIZE and 
                                    (wx, wy) != (game_state.player_x, game_state.player_y) and (wx, wy) != (game_state.end_x, game_state.end_y) and 
                                    (wx, wy) not in game_state.walls for wx, wy in wall_positions)
                        
                        if valid:
                            game_state.walls.update(wall_positions)
                            game_state.player_turns = 0

                        # Show turn notification when Maze Master completes their turn
                        game_state.show_turn_notification = True
                        game_state.turn_notification_timer = 0
                        game_state.rounds_since_last_skill3 += 1

                        if game_state.maze_skill_cooldown > 0:     # Maze Skill 1 cooldown decrementer (To refresh skill)
                            game_state.maze_skill_cooldown -= 1

    pygame.display.flip()
    clock.tick(60)

pygame.quit()