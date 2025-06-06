# A3 Game with AI

# Members:
# Banuag, Carl
# Deen, Marfred
# Ferolino, Jilliane
# Rodriguez, Andrea
# Rulete, Jeric
# Torres, John Angelo

import pygame
import random
import sys
import time
from ai_logic import MazeRunnerAI, MazeMasterAI

# Constants
GRID_SIZE = 24
TILE_SIZE = 25
SCREEN_WIDTH = GRID_SIZE * TILE_SIZE
SCREEN_HEIGHT = GRID_SIZE * TILE_SIZE + 50
MAX_AI_THINKING_TIME = 0.5  # Maximum time in seconds for AI to think
AI_THINKING_DEPTH = 3  # Depth for minimax search

# Colors
WHITE = (255, 255, 255)
OFF_WHITE = (245, 245, 220)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
GRAY = (169, 169, 169)
BLUE = (0, 0, 255)
LIGHT_BLUE = (173, 216, 230)
YELLOW = (255, 255, 0, 160)  # Semi-transparent yellow for highlights
LIGHT_ORANGE = (255, 200, 0, 100)  # Light orange for valid wall placements
ACTIVE_SKILL_COLOR = (50, 200, 50)  # Bright green for active skills
WALL_BREAK_COLOR = (255, 100, 0)  # Orange for wall break skill
DIAGONAL_WALL_COLOR = (128, 0, 128)  # Purple for diagonal walls

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Turn-Based Maze Game")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 30)
small_font = pygame.font.Font(None, 20)

# Player start position
player_x, player_y = 0, 0
end_x, end_y = GRID_SIZE - 1, GRID_SIZE - 1
walls = set()
walls_placed = 0
player_turns = 0
player_skill_active = False
player_skill_active_used=False
maze_skill1_active = False
maze_skill1_cooldown = 0
skill_2_active = False  # Skill 2 activation flag
skill_2_used = False  # Track if skill 2 has been used
skill_3_active = False  # Skill 3 (wall break) activation flag
skill_3_used = False  # Track if skill 3 has been used
skill_3_available = False  # Track if skill 3 is available
maze_skill_3_active = False  # Tracks if Maze Master's teleport skill is active
maze_skill_3_cooldown = 0    # Cooldown timer for Maze Master's teleport skill
MAZE_SKILL_3_COOLDOWN_MAX = 3  # Number of turns before skill can be used again
game_won = False  # Flag to track if the player has won
maze_skill2_active = False  # Tracks if Maze Master's diagonal wall skill is active
maze_skill2_used = False    # Tracks if diagonal wall skill has been used

# Track game progress for skill 3 availability
total_player_steps = 0
rounds_since_last_skill3 = 0  # Track moves since last skill 3 availability

# Animation variables for turn text
animation_time = 0
animation_speed = 5  # Speed of animation
show_turn_notification = False
turn_notification_timer = 0
turn_notification_duration = 60  # How long to show the notification (in frames)

# Skill button rects
def update_button_positions():
    global skill_1_button, skill_2_button, skill_3_button, reset_button
    button_width = 80
    button_height = 25
    spacing = 10

    skill_1_button = pygame.Rect(spacing, 10, button_width, button_height)
    skill_2_button = pygame.Rect(spacing + button_width + spacing, 10, button_width, button_height)
    skill_3_button = pygame.Rect(SCREEN_WIDTH - (2 * (button_width + spacing)), 10, button_width, button_height)
    reset_button = pygame.Rect(SCREEN_WIDTH - (2 * (button_width + spacing)) + 90, 10, button_width, button_height)

update_button_positions()

def draw_buttons():
    # Reset button
    pygame.draw.rect(screen, RED, reset_button)

    # Player's turn buttons
    if player_turns < 4:
        # Skill 1 button (Extended Move)
        # if player_skill_active_used:
        #     skill_1_color = GRAY
        # el
        if player_skill_active:
            skill_1_color = ACTIVE_SKILL_COLOR
        else:
            skill_1_color = BLUE if player_turns <= 2 else GRAY  # Gray out if less than 2 turns left
        pygame.draw.rect(screen, skill_1_color, skill_1_button)
        
        # Skill 2 button (Teleport)
        if skill_2_active:
            skill_2_color = ACTIVE_SKILL_COLOR
        elif skill_2_used:
            skill_2_color = GRAY
        else:
            skill_2_color = BLUE
        pygame.draw.rect(screen, skill_2_color, skill_2_button)
        
        # Skill 3 button (Wall Break)
        if skill_3_active:
            skill_3_color = WALL_BREAK_COLOR
        elif not skill_3_available or skill_3_used:
            skill_3_color = GRAY
        else:
            skill_3_color = BLUE
        pygame.draw.rect(screen, skill_3_color, skill_3_button)
    # Maze Master's turn buttons
    else:
        # Skill 1 button (Double Walls)
        if maze_skill1_active:
            skill_1_color = ACTIVE_SKILL_COLOR
        # elif maze_skill1_cooldown > 0:
        #     skill_1_color = GRAY
        else:
            skill_1_color = BLUE
        pygame.draw.rect(screen, skill_1_color, skill_1_button)
        
        # Skill 2 button (Diagonal Walls)
        if maze_skill2_active:
            skill_2_color = ACTIVE_SKILL_COLOR
        elif maze_skill2_used:
            skill_2_color = GRAY
        else:
            skill_2_color = BLUE
        pygame.draw.rect(screen, skill_2_color, skill_2_button)
        
        # Skill 3 button (Teleport Player)
        if maze_skill_3_active:
            skill_3_color = ACTIVE_SKILL_COLOR
        elif maze_skill_3_cooldown > 0:
            skill_3_color = GRAY
        else:
            skill_3_color = BLUE
        pygame.draw.rect(screen, skill_3_color, skill_3_button)
    
    # Common button labels
    pygame.draw.rect(screen, BLUE, skill_3_button)
    screen.blit(font.render("Skill 1", True, WHITE), (skill_1_button.x + 10, skill_1_button.y + 5))
    screen.blit(font.render("Skill 2", True, WHITE), (skill_2_button.x + 10, skill_2_button.y + 5))
    screen.blit(font.render("Skill 3", True, WHITE), (skill_3_button.x + 10, skill_3_button.y + 5))
    screen.blit(font.render("Reset", True, WHITE), (reset_button.x + 10, reset_button.y + 5))
    
    # Active skill indicators
    if player_skill_active:
        draw_active_indicator(skill_1_button)
    if skill_2_active:
        draw_active_indicator(skill_2_button)
    if skill_3_active:
        draw_active_indicator(skill_3_button, WALL_BREAK_COLOR)
    if maze_skill1_active:
        draw_active_indicator(skill_1_button)
    if maze_skill2_active:
        draw_active_indicator(skill_2_button)
    if maze_skill_3_active:
        draw_active_indicator(skill_3_button)
    
    # Unlocked indicators
    if skill_3_available and not skill_3_used and not skill_3_active and player_turns < 4:
        draw_unlocked_indicator(skill_3_button)

def draw_active_indicator(button, color=WHITE):
    skill_text = small_font.render("ACTIVE", True, color)
    text_x = button.x + (button.width - skill_text.get_width()) // 2
    screen.blit(skill_text, (text_x, button.y + button.height + 2))

def draw_unlocked_indicator(button):
    unlock_text = small_font.render("UNLOCKED", True, WALL_BREAK_COLOR)
    text_x = button.x + (button.width - unlock_text.get_width()) // 2
    screen.blit(unlock_text, (text_x, button.y + button.height + 2))

def is_valid_diagonal_wall_position(x, y, direction):
    """Check if a diagonal wall can be placed at (x,y) in given direction."""
    wall_positions = []
    for i in range(3):
        if direction == "uldr":  # Upper left to lower right
            wx, wy = x + i, y + i
        else:  # Upper right to lower left
            wx, wy = x - i, y + i
        wall_positions.append((wx, wy))
    
    return all(0 <= wx < GRID_SIZE and 0 <= wy < GRID_SIZE and 
              (wx, wy) not in walls and
              (wx, wy) != (player_x, player_y) and
              (wx, wy) != (end_x, end_y)
              for wx, wy in wall_positions), wall_positions


def draw_turn_text(custom_message=None):
    # Determine the current turn or show a custom message
    if custom_message:
        turn_text = custom_message
    elif game_won:
        turn_text = "Congratulations!"
    else:
        turn_text = "Player's Turn" if player_turns < 4 else "Maze Master's Turn"
    
    # Get the base text render
    base_text = font.render(turn_text, True, BLUE)
    
    # Center position
    x_pos = SCREEN_WIDTH // 2 - base_text.get_width() // 2
    y_pos = 15

    # Draw the text
    screen.blit(base_text, (x_pos, y_pos))
    
    # Add active skill info (Player)
    if player_skill_active or skill_2_active or skill_3_active:
        active_skill = ""
        active_color = ACTIVE_SKILL_COLOR
        
        if player_skill_active:
            active_skill = "Extended Move"
        elif skill_2_active:
            active_skill = "Teleport"
        elif skill_3_active:
            active_skill = "Wall Break"
            active_color = WALL_BREAK_COLOR
            
        skill_info = small_font.render(f"{active_skill} Active", True, active_color)
        x_pos = SCREEN_WIDTH // 2 - skill_info.get_width() // 2
        screen.blit(skill_info, (x_pos, y_pos + 20))

    # Add active skill info (Maze Master)
    if maze_skill1_active:
        active_skill = "Double Walls"
        active_color = ACTIVE_SKILL_COLOR

        skill_info = small_font.render(f"{active_skill} Active", True, active_color)
        x_pos = SCREEN_WIDTH // 2 - skill_info.get_width() // 2
        screen.blit(skill_info, (x_pos, y_pos + 20))

def show_turn_change_notification():
    global show_turn_notification, turn_notification_timer
    
    notification_text = "Your Turn!" if player_turns < 4 else "Maze Master's Turn!"
    
    # Create a semi-transparent surface for the notification
    notification_surface = pygame.Surface((350, 80), pygame.SRCALPHA)
    
    # Calculate alpha based on time (fade in/out)
    if turn_notification_timer < 15:
        alpha = min(255, turn_notification_timer * 17)  # Fade in
    elif turn_notification_timer > turn_notification_duration - 15:
        alpha = max(0, 255 - (turn_notification_timer - (turn_notification_duration - 15)) * 17)  # Fade out
    else:
        alpha = 255  # Fully visible
        
    notification_surface.fill((0, 0, 180, alpha))
    
    # Render the text
    text_size = 40
    big_font = pygame.font.Font(None, text_size)
    text = big_font.render(notification_text, True, WHITE)
    
    # Center text on notification
    text_x = (notification_surface.get_width() - text.get_width()) // 2
    text_y = (notification_surface.get_height() - text.get_height()) // 2
    
    notification_surface.blit(text, (text_x, text_y))
    
    # Position the notification in the center of the screen
    notification_x = (SCREEN_WIDTH - notification_surface.get_width()) // 2
    notification_y = (SCREEN_HEIGHT - notification_surface.get_height()) // 2
    
    # Draw the notification
    screen.blit(notification_surface, (notification_x, notification_y))
    
    # Update timer
    turn_notification_timer += 1
    
    # Check if we should stop showing the notification
    if turn_notification_timer >= turn_notification_duration:
        show_turn_notification = False
        turn_notification_timer = 0

def get_valid_moves(x, y, max_distance):
    """Get all valid moves from current position within max_distance."""
    valid_tiles = []
    
    # For skill 2 (teleport), use a square area around the player
    if skill_2_active:
        for dx in range(-max_distance, max_distance + 1):
            for dy in range(-max_distance, max_distance + 1):
                new_x, new_y = x + dx, y + dy
                if (0 <= new_x < GRID_SIZE and 
                    0 <= new_y < GRID_SIZE and 
                    (new_x, new_y) not in walls):
                    valid_tiles.append((new_x, new_y))
    elif player_skill_active:
        # Horizontal line
        for dx in range(1, 5):  # Moving right
            new_x, new_y = x + dx, y
            if new_x >= GRID_SIZE or (new_x, new_y) in walls:
                break
            valid_tiles.append((new_x, new_y))
        for dx in range(1, 5):  # Moving left
            new_x, new_y = x - dx, y
            if new_x < 0 or (new_x, new_y) in walls:
                break
            valid_tiles.append((new_x, new_y))
        # Vertical line
        for dy in range(1, 5):  # Moving down
            new_x, new_y = x, y + dy
            if new_y >= GRID_SIZE or (new_x, new_y) in walls:
                break
            valid_tiles.append((new_x, new_y))
        for dy in range(1, 5):  # Moving up
            new_x, new_y = x, y - dy
            if new_y < 0 or (new_x, new_y) in walls:
                break
            valid_tiles.append((new_x, new_y))
    else:
        # Regular movement (up, down, left, right)
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            new_x, new_y = x + dx, y + dy
            if (0 <= new_x < GRID_SIZE and 
                0 <= new_y < GRID_SIZE and 
                (new_x, new_y) not in walls):
                valid_tiles.append((new_x, new_y))
    return valid_tiles

def is_valid_wall_position(x, y, is_horizontal):
    """Check if a wall can be placed at a specific position."""
    if is_horizontal:
        wall_positions = [(x + i, y) for i in range(3)]
    else:
        wall_positions = [(x, y + i) for i in range(3)]

    # Define a protected area around the endpoint
    protected_area = {
        (px, py)
        for px in range(end_x - 6, end_x + 6)
        for py in range(end_y - 6, end_y + 6)
        if 0 <= px < GRID_SIZE and 0 <= py < GRID_SIZE
    }

    valid = all(
        0 <= wx < GRID_SIZE and
        0 <= wy < GRID_SIZE and
        (wx, wy) != (player_x, player_y) and
        (wx, wy) != (end_x, end_y) and
        (wx, wy) not in walls and
        (wx, wy) not in protected_area
        for wx, wy in wall_positions
    )

    return valid

def highlight_clickable_areas():
    """Highlight all valid moves or wall placements based on current game state."""
    # Create semi-transparent surface for highlights
    highlight_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    
    # Player's turn
    if player_turns < 4:
        # Player's turn highlighting (existing code)
        if skill_3_active:
            # Highlight all wall pieces that can be broken
            for wx, wy in walls:
                pygame.draw.rect(highlight_surface, (255, 100, 0, 100), 
                               (wx * TILE_SIZE, wy * TILE_SIZE + 50, TILE_SIZE, TILE_SIZE))
        else:
            # Determine movement range based on skill
            max_move = 4 if player_skill_active else 1
            max_teleport = 2 if skill_2_active else 0
            
            # Get valid moves
            if skill_2_active:
                valid_tiles = get_valid_moves(player_x, player_y, max_teleport)
                highlight_color = (255, 255, 0, 100)  # Yellow for teleport
            else:
                valid_tiles = get_valid_moves(player_x, player_y, max_move)
                highlight_color = (0, 255, 0, 100)  # Green for normal movement
                
            # Draw highlights for valid moves
            for tx, ty in valid_tiles:
                pygame.draw.rect(highlight_surface, highlight_color, 
                               (tx * TILE_SIZE, ty * TILE_SIZE + 50, TILE_SIZE, TILE_SIZE))
                
    else:
        # Maze Master's turn highlighting
        if maze_skill2_active:
            # Highlight valid diagonal wall placements
            for x in range(GRID_SIZE):
                for y in range(GRID_SIZE):
                    if (x, y) in walls or (x, y) == (player_x, player_y) or (x, y) == (end_x, end_y):
                        continue
                    
                    # Check both diagonal directions
                    uldr_valid, _ = is_valid_diagonal_wall_position(x, y, "uldr")
                    urdl_valid, _ = is_valid_diagonal_wall_position(x, y, "urdl")
                    
                    if uldr_valid or urdl_valid:
                        pygame.draw.rect(highlight_surface, DIAGONAL_WALL_COLOR + (100,), 
                                       (x * TILE_SIZE, y * TILE_SIZE + 50, TILE_SIZE, TILE_SIZE))
        else:
            # Regular wall placement highlighting
            is_horizontal = not pygame.key.get_pressed()[pygame.K_LSHIFT]
            for x in range(GRID_SIZE):
                for y in range(GRID_SIZE):
                    if (x, y) in walls or (x, y) == (player_x, player_y) or (x, y) == (end_x, end_y):
                        continue
                    
                    if is_valid_wall_position(x, y, is_horizontal):
                        wall_positions = [(x + i, y) for i in range(3)] if is_horizontal else [(x, y + i) for i in range(3)]
                        for wx, wy in wall_positions:
                            pygame.draw.rect(highlight_surface, LIGHT_ORANGE, 
                                           (wx * TILE_SIZE, wy * TILE_SIZE + 50, TILE_SIZE, TILE_SIZE))    
    screen.blit(highlight_surface, (0, 0))

def draw_skill_info():
    """Draw skill info based on what's active"""
    if player_turns < 4:  # Only show during player's turn
        info_text = ""
        info_color = WHITE
        
        if player_skill_active:
            info_text = "Skill 1: Extended Move (4 tiles)"
            info_color = WHITE
        elif skill_2_active:
            info_text = "Skill 2: Teleport (within 2 tiles)"
            info_color = WHITE
        elif skill_3_active:
            info_text = "Skill 3: Wall Break (click a wall to break it)"
            info_color = WALL_BREAK_COLOR
        
        if info_text:
            # Render text first to determine the width dynamically
            skill_info = font.render(info_text, True, info_color)
            text_width, text_height = skill_info.get_size()
            padding = 10  # Add some padding around the text
            
            # Create background surface based on text size
            bg_width = text_width + 2 * padding
            bg_height = text_height + 2 * padding
            info_surface = pygame.Surface((bg_width, bg_height), pygame.SRCALPHA)
            info_surface.fill((0, 0, 0, 200))  # Less transparent background
            
            # Compute positions
            x_pos = (SCREEN_WIDTH - bg_width) // 2  # Center the background
            y_pos = SCREEN_HEIGHT - 40
            screen.blit(info_surface, (x_pos, y_pos))
            
            # Draw text centered within the background
            text_x = x_pos + padding
            text_y = y_pos + padding
            screen.blit(skill_info, (text_x, text_y))
        
        # Check if skill 3 just became available
        elif skill_3_available and not skill_3_used and not skill_3_active:
            unlock_text = "Skill 3 (Wall Break) is now available!"
            unlock_info = font.render(unlock_text, True, WALL_BREAK_COLOR)
            text_width, text_height = unlock_info.get_size()
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
            screen.blit(unlock_info, (text_x, text_y))

def reset_game():
    global player_x, player_y, walls, player_turns, player_skill_active, skill_2_active, skill_2_used
    global show_turn_notification, turn_notification_timer, skill_3_active, skill_3_used, skill_3_available
    global total_player_steps, rounds_since_last_skill3, maze_skill_3_active, maze_skill_3_cooldown
    global maze_skill2_active, maze_skill2_used, player_skill_active_used, game_won
    global runner_ai, master_ai, game_mode

    # Reset player position and skills
    player_x, player_y = 0, 0
    walls.clear()
    player_turns = 0
    player_skill_active = False
    player_skill_active_used = False
    maze_skill1_active = False
    skill_2_active = False
    skill_2_used = False
    skill_3_active = False
    skill_3_used = False
    skill_3_available = False
    game_won = False
    total_player_steps = 0
    rounds_since_last_skill3 = 0
    maze_skill_3_active = False
    maze_skill_3_cooldown = 0
    maze_skill2_active = False
    maze_skill2_used = False

    # Re-initialize AI objects based on game mode
    if game_mode == "runner":
        master_ai = MazeMasterAI(GRID_SIZE)
        master_ai.max_depth = AI_THINKING_DEPTH  # Set the minimax depth
    elif game_mode == "master":
        runner_ai = MazeRunnerAI(GRID_SIZE)

    # Show turn notification after reset
    show_turn_notification = True
    turn_notification_timer = 0

    print("Game has been reset successfully.")  # Debug message to verify reset

# Show turn notification at game start
show_turn_notification = True

# Mouse tracking for hover effects
mouse_x, mouse_y = 0, 0


# Add this new function after the other skill-related functions
def teleport_player_random():
    """
    Teleports the player to a random valid location on the grid.
    
    Returns:
        bool: True if teleport was successful, False if no valid positions found
    """
    global player_x, player_y
    
    # Get all valid positions (excluding walls and end point)
    valid_positions = [
        (x, y) for x in range(GRID_SIZE) 
        for y in range(GRID_SIZE)
        if (x, y) not in walls and (x, y) != (end_x, end_y)
    ]
    
    if valid_positions:
        player_x, player_y = random.choice(valid_positions)
        return True
    return False

# Get game mode from command line argument
game_mode = "pvp"  # default mode
if len(sys.argv) > 1:
    game_mode = sys.argv[1]

# Initialize AI if needed
runner_ai = None
master_ai = None
if game_mode == "runner":
    master_ai = MazeMasterAI(GRID_SIZE)
    master_ai.max_depth = AI_THINKING_DEPTH  # Set the minimax depth
elif game_mode == "master":
    runner_ai = MazeRunnerAI(GRID_SIZE)

# Game loop
running = True
last_turn_state = player_turns < 4  # Track turn state to detect changes
while running:
    screen.fill(OFF_WHITE)

    # Update mouse position for hover effects
    mouse_x, mouse_y = pygame.mouse.get_pos()

    # AI moves if it's their turn
    if not game_won:
        if game_mode == "runner" and player_turns >= 4:
            # Maze Master AI's turn
            master_ai.update_state(walls, (player_x, player_y), total_player_steps)
            
            # Get AI move with time limit
            start_time = time.time()
            wall_pos, is_horizontal, skill = master_ai.decide_move(walls_placed)
            thinking_time = time.time() - start_time
            
            # If AI took too long, reduce depth for next time
            if thinking_time > MAX_AI_THINKING_TIME:
                master_ai.max_depth = max(1, master_ai.max_depth - 1)
            
            if skill == "skill_1":
                maze_skill1_active = True
                pos1 = wall_pos
                is_horizontal1 = is_horizontal

                if is_valid_wall_position(pos1[0], pos1[1], is_horizontal1):
                    walls.update([(pos1[0] + i, pos1[1]) for i in range(3)] if is_horizontal1 else [(pos1[0], pos1[1] + i) for i in range(3)])

                walls_placed += 1

                if walls_placed < 2:
                    wall_pos, is_horizontal, skill = master_ai.decide_move(walls_placed)
                    pos1 = wall_pos
                    is_horizontal1 = is_horizontal

                    if is_valid_wall_position(pos1[0], pos1[1], is_horizontal1):
                        walls.update([(pos1[0] + i, pos1[1]) for i in range(3)] if is_horizontal1 else [(pos1[0], pos1[1] + i) for i in range(3)])

                    walls_placed += 1

                if walls_placed == 2:
                    player_turns = 0
                    walls_placed = 0
                    master_ai.skill_1_cooldown = 3
                    maze_skill1_active = False

                show_turn_notification = True
                turn_notification_timer = 0
                rounds_since_last_skill3 += 1
                
            elif skill == "skill_2":
                maze_skill2_active = True
                maze_skill2_used = True
                direction = "urdl" if pygame.key.get_pressed()[pygame.K_LSHIFT] else "uldr"
                valid, wall_positions = is_valid_diagonal_wall_position(wall_pos[0], wall_pos[1], direction)
                if valid:
                    walls.update(wall_positions)
                    maze_skill2_active = False
                    master_ai.skill_2_used = True
                    player_turns = 0
                    show_turn_notification = True
                    turn_notification_timer = 0
                    rounds_since_last_skill3 += 1
                
            elif skill == "skill_3" and maze_skill_3_cooldown == 0:
                if teleport_player_random():
                    master_ai.skill_3_cooldown = MAZE_SKILL_3_COOLDOWN_MAX
                    player_turns = 0
                    show_turn_notification = True
                    turn_notification_timer = 0
            
            if not any([maze_skill1_active, maze_skill2_active, maze_skill_3_active]):
                # Place wall using AI's decision
                if is_valid_wall_position(wall_pos[0], wall_pos[1], is_horizontal):
                    if is_horizontal:
                        wall_positions = [(wall_pos[0] + i, wall_pos[1]) for i in range(3)]
                    else:
                        wall_positions = [(wall_pos[0], wall_pos[1] + i) for i in range(3)]
                    walls.update(wall_positions)
                    player_turns = 0
                    show_turn_notification = True
                    turn_notification_timer = 0
                    rounds_since_last_skill3 += 1
                    
                    # Check if walls cover 30% of the grid
                    total_tiles = GRID_SIZE * GRID_SIZE
                    if len(walls) >= total_tiles * 0.3:
                        game_won = True
                        draw_turn_text("Maze Master Wins!")
                        pygame.display.flip()
                        pygame.time.delay(2000)
                        reset_game()
                        continue

            if master_ai.skill_1_cooldown > 0:
                master_ai.skill_1_cooldown -= 1
            if master_ai.skill_3_cooldown > 0:
                master_ai.skill_3_cooldown -= 1
        
        elif game_mode == "master" and player_turns < 4:
            # Runner AI's turn
            runner_ai.update_state(walls, (player_x, player_y), rounds_since_last_skill3)
            next_pos, skill, use_skill = runner_ai.decide_move()
            
            if use_skill:
                if skill == "skill_1":
                    player_skill_active = True
                elif skill == "skill_2":
                    # Instead of just activating the skill, complete the teleport in one step
                    skill_2_active = True
                    valid_tiles = get_valid_moves(player_x, player_y, 2)  # Get valid teleport destinations
                    if valid_tiles and next_pos in valid_tiles:
                        player_x, player_y = next_pos
                        skill_2_active = False
                        skill_2_used = True
                        player_turns += 1
                        total_player_steps += 1
                    else:
                        # If we can't teleport to the desired position, choose any valid position
                        if valid_tiles:
                            player_x, player_y = random.choice(valid_tiles)
                            skill_2_active = False
                            skill_2_used = True
                            player_turns += 1
                            total_player_steps += 1
                        else:
                            # If no valid tiles for teleport, just disable the skill
                            skill_2_active = False
                elif skill == "skill_3" and skill_3_available and not skill_3_used:
                    # Execute wall break immediately when AI decides to use it
                    if next_pos in walls:  # next_pos contains the wall position to break
                        walls.remove(next_pos)
                        skill_3_used = True
                        skill_3_active = False
                        player_turns += 1
                        total_player_steps += 1
                        rounds_since_last_skill3 = 0  # Reset the counter after using skill 3
                        print(f"AI broke wall at position {next_pos}")  # Debug message
            
            if not any([player_skill_active, skill_2_active, skill_3_active]):
                # Move to AI's decided position
                if next_pos in get_valid_moves(player_x, player_y, 1):
                    player_x, player_y = next_pos
                    player_turns += 1
                    total_player_steps += 1

    # Check if the player has reached the goal
    if player_x == end_x and player_y == end_y:
        game_won = True
        if game_mode == "runner":
            draw_turn_text("Congratulations!")  # Show "Congratulations!" for runner
        elif game_mode == "master":
            draw_turn_text("You Lose!")  # Show "You Lose!" for master
        pygame.display.flip()
        pygame.time.delay(2000)  # Display message for 2 seconds
        reset_game()
        continue  # Restart the loop after resetting
    
    # Check if Skill 3 should become available (after 4 moves total and every 4 moves thereafter)
    if rounds_since_last_skill3 >= 4 and (skill_3_used or not skill_3_available):
        skill_3_available = True
        skill_3_used = False
        rounds_since_last_skill3 = 0

    # Draw the grid
    for x in range(0, SCREEN_WIDTH, TILE_SIZE):
        for y in range(50, SCREEN_HEIGHT, TILE_SIZE):
            pygame.draw.rect(screen, BLACK, pygame.Rect(x, y, TILE_SIZE, TILE_SIZE), 1)
    
    # Draw walls
    for wx, wy in walls:
        pygame.draw.rect(screen, GRAY, (wx * TILE_SIZE, wy * TILE_SIZE + 50, TILE_SIZE, TILE_SIZE))
    
    # Highlight valid moves
    highlight_clickable_areas()
    
    # Draw player and end positions (on top of highlights)
    pygame.draw.rect(screen, GREEN, (player_x * TILE_SIZE, player_y * TILE_SIZE + 50, TILE_SIZE, TILE_SIZE))
    pygame.draw.rect(screen, RED, (end_x * TILE_SIZE, end_y * TILE_SIZE + 50, TILE_SIZE, TILE_SIZE))
    
    # Draw turn text and buttons
    draw_turn_text()
    draw_buttons()
    
    # Draw skill info at the bottom of the screen
    draw_skill_info()
    
    # Check if turn state has changed
    current_turn_state = player_turns < 4
    if current_turn_state != last_turn_state:
        show_turn_notification = True
        turn_notification_timer = 0
        last_turn_state = current_turn_state
    
    # Show turn notification if active
    if show_turn_notification:
        show_turn_change_notification()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.VIDEORESIZE:
            SCREEN_WIDTH, SCREEN_HEIGHT = event.w, event.h
            screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
            update_button_positions()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()

            # Reset button logic
            if reset_button.collidepoint(mx, my):
                reset_game()
                continue
            
            # Skill button handling
            if skill_1_button.collidepoint(mx, my):
                if player_turns < 4:
                    # Only allow activation if player has at least 2 turns remaining
                    if player_turns < 3:
                        player_skill_active = True
                elif player_turns >= 4 and maze_skill1_cooldown == 0:
                    maze_skill1_active = True
                    maze_skill1_cooldown = 0
                continue
            
            if skill_2_button.collidepoint(mx, my):
                if player_turns < 4 and not skill_2_used:
                    skill_2_active = not skill_2_active
                    if skill_2_active:
                        player_skill_active = False
                        skill_3_active = False
                elif player_turns >= 4 and not maze_skill2_used:
                    maze_skill2_active = not maze_skill2_active
                    if maze_skill2_active:
                        maze_skill1_active = False
                continue
                
            if skill_3_button.collidepoint(mx, my):
                if player_turns < 4 and skill_3_available and not skill_3_used:
                    skill_3_active = not skill_3_active
                    if skill_3_active:
                        player_skill_active = False
                        skill_2_active = False
                elif player_turns >= 4 and maze_skill_3_cooldown == 0:
                    maze_skill_3_active = True
                    if teleport_player_random():
                        maze_skill_3_cooldown = MAZE_SKILL_3_COOLDOWN_MAX
                        player_turns = 0
                        show_turn_notification = True
                        turn_notification_timer = 0
                    maze_skill_3_active = False
                continue
            
            if my < 50:
                continue

            clicked_x = mx // TILE_SIZE
            clicked_y = (my - 50) // TILE_SIZE
            
            # Player actions
            if player_turns < 4:
                # Only allow player movement if NOT in master mode (playing as Maze Master)
                if game_mode != "master":
                    if skill_3_active and (clicked_x, clicked_y) in walls:
                        walls.remove((clicked_x, clicked_y))
                        skill_3_active = False
                        skill_3_used = True
                        player_turns += 1
                        total_player_steps += 1
                        continue

                    if skill_2_active:
                        valid_tiles = get_valid_moves(player_x, player_y, 2)  # Get valid tiles within teleport range
                        if (clicked_x, clicked_y) in valid_tiles and (clicked_x, clicked_y) not in walls:
                            player_x, player_y = clicked_x, clicked_y
                            skill_2_active = False
                            skill_2_used = True
                            player_turns += 1
                            total_player_steps += 1
                        continue

                    if player_skill_active:
                        if player_turns < 2:
                            player_skill_active_used = True
                        valid_moves = get_valid_moves(player_x, player_y, 1)
                        if (clicked_x, clicked_y) in valid_moves:
                            player_x, player_y = clicked_x, clicked_y
                            player_turns += 2
                            total_player_steps += 1
                            player_skill_active = False
                    else:
                        valid_moves = get_valid_moves(player_x, player_y, 1)
                        if (clicked_x, clicked_y) in valid_moves:
                            player_x, player_y = clicked_x, clicked_y
                            player_turns += 1
                            total_player_steps += 1
            # Maze Master actions
            else:
                if (clicked_x, clicked_y) == (player_x, player_y) or (clicked_x, clicked_y) == (end_x, end_y):
                    continue
                    
                if maze_skill2_active:
                    direction = "urdl" if pygame.key.get_pressed()[pygame.K_LSHIFT] else "uldr"
                    valid, wall_positions = is_valid_diagonal_wall_position(clicked_x, clicked_y, direction)
                    if valid:
                        walls.update(wall_positions)
                        maze_skill2_active = False
                        maze_skill2_used = True
                        player_turns = 0
                        show_turn_notification = True
                        turn_notification_timer = 0
                        rounds_since_last_skill3 += 1

                elif maze_skill1_active:   # Skill 1 is activated (Maze master)

                        if walls_placed < 2:    # Required to place 2 walls
                            if pygame.key.get_pressed()[pygame.K_LSHIFT]:
                                wall_positions = [(clicked_x, clicked_y + i) for i in range(3)]
                            else:
                                wall_positions = [(clicked_x + i, clicked_y) for i in range(3)]
                            
                            valid = all(0 <= wx < GRID_SIZE and 0 <= wy < GRID_SIZE and 
                                        (wx, wy) != (player_x, player_y) and (wx, wy) != (end_x, end_y) and 
                                        (wx, wy) not in walls for wx, wy in wall_positions)
                            
                            if valid:
                                walls.update(wall_positions)
                                walls_placed += 1  # Increment only if valid
                            
                            # End turn if invalid placement or two walls are placed
                            if walls_placed >= 2:
                                player_turns = 0  # End Maze Master's turn
                                walls_placed = 0  # Reset walls counter
                                maze_skill1_active = False  # Reset Skill 1 activation
                                continue
                        
                        # Reset Skill 1 activation if no walls were placed
                        if walls_placed == 0:
                            maze_skill1_active = False
                            walls_placed = 0
                            player_turns = 0
                            continue
                else:
                    is_horizontal = not pygame.key.get_pressed()[pygame.K_LSHIFT]

                    if is_valid_wall_position(clicked_x, clicked_y, is_horizontal):
                        wall_positions = [(clicked_x + i, clicked_y) for i in range(3)] if is_horizontal else [(clicked_x, clicked_y + i) for i in range(3)]
                        walls.update(wall_positions)
                        player_turns = 0
                        show_turn_notification = True
                        turn_notification_timer = 0
                        rounds_since_last_skill3 += 1

                        # Check if walls cover 50% of the grid
                        total_tiles = GRID_SIZE * GRID_SIZE
                        if len(walls) >= total_tiles * 0.3:
                            game_won = True
                            draw_turn_text("Maze Master Wins!")
                            pygame.display.flip()
                            pygame.time.delay(2000)
                            reset_game()
                            continue
                        
                # Update cooldowns
                if maze_skill1_cooldown > 0:
                    maze_skill1_cooldown -= 1
                if maze_skill_3_cooldown > 0:
                    maze_skill_3_cooldown -= 1
    pygame.display.flip()
    clock.tick(60)

pygame.quit()