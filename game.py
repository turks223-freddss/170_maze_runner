import pygame
import math

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

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Turn-Based Maze Game")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 30)

# Player start position
player_x, player_y = 0, 0
end_x, end_y = GRID_SIZE - 1, GRID_SIZE - 1
walls = set()
player_turns = 0
player_skill_active = False
skill_2_active = False  # Skill 2 activation flag
skill_2_used = False  # Track if skill 2 has been used
game_won = False  # Flag to track if the player has won

# Animation variables for turn text
animation_time = 0
animation_speed = 5  # Speed of animation
show_turn_notification = False
turn_notification_timer = 0
turn_notification_duration = 60  # How long to show the notification (in frames)

# Skill button rects
def update_button_positions():
    global skill_1_button, skill_2_button, skill_3_button, skill_4_button
    button_width = 80
    button_height = 25
    spacing = 10

    skill_1_button = pygame.Rect(spacing, 10, button_width, button_height)
    skill_2_button = pygame.Rect(spacing + button_width + spacing, 10, button_width, button_height)
    skill_3_button = pygame.Rect(SCREEN_WIDTH - (2 * (button_width + spacing)), 10, button_width, button_height)
    skill_4_button = pygame.Rect(SCREEN_WIDTH - (button_width + spacing), 10, button_width, button_height)

update_button_positions()

def draw_buttons():
    pygame.draw.rect(screen, BLUE, skill_1_button)
    
    # Skill 2 should be green only if used AND it's still the player's turn
    skill_2_color = GREEN if skill_2_used and player_turns < 4 else BLUE
    pygame.draw.rect(screen, skill_2_color, skill_2_button)

    pygame.draw.rect(screen, BLUE, skill_3_button)
    pygame.draw.rect(screen, BLUE, skill_4_button)
    
    screen.blit(font.render("Skill 1", True, WHITE), (skill_1_button.x + 10, skill_1_button.y + 5))
    screen.blit(font.render("Skill 2", True, WHITE), (skill_2_button.x + 10, skill_2_button.y + 5))
    screen.blit(font.render("Skill 3", True, WHITE), (skill_3_button.x + 10, skill_3_button.y + 5))
    screen.blit(font.render("Skill 4", True, WHITE), (skill_4_button.x + 10, skill_4_button.y + 5))

def draw_turn_text():
    # Determine the current turn
    if game_won:
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

def reset_game():
    global player_x, player_y, walls, player_turns, player_skill_active, skill_2_active, skill_2_used, game_won
    global show_turn_notification, turn_notification_timer
    
    player_x, player_y = 0, 0
    walls.clear()
    player_turns = 0
    player_skill_active = False
    skill_2_active = False
    skill_2_used = False  # Reset skill usage
    game_won = False  # Reset win state
    
    # Show turn notification after reset
    show_turn_notification = True
    turn_notification_timer = 0

# Show turn notification at game start
show_turn_notification = True

# Game loop
running = True
last_turn_state = player_turns < 4  # Track turn state to detect changes
while running:
    screen.fill(OFF_WHITE)

    # Check if the player has reached the goal
    if player_x == end_x and player_y == end_y:
        game_won = True
    
    if game_won:
        draw_turn_text()  # Show "Congratulations!"
        pygame.display.flip()
        pygame.time.delay(2000)  # Display message for 2 seconds
        reset_game()
        continue  # Restart the loop after resetting

    # Draw turn text and buttons
    draw_turn_text()
    draw_buttons()
    
    # Draw the grid
    for x in range(0, SCREEN_WIDTH, TILE_SIZE):
        for y in range(50, SCREEN_HEIGHT, TILE_SIZE):
            pygame.draw.rect(screen, BLACK, pygame.Rect(x, y, TILE_SIZE, TILE_SIZE), 1)
    
    # Draw walls
    for wx, wy in walls:
        pygame.draw.rect(screen, GRAY, (wx * TILE_SIZE, wy * TILE_SIZE + 50, TILE_SIZE, TILE_SIZE))
    
    # Draw player and end positions
    pygame.draw.rect(screen, GREEN, (player_x * TILE_SIZE, player_y * TILE_SIZE + 50, TILE_SIZE, TILE_SIZE))
    pygame.draw.rect(screen, RED, (end_x * TILE_SIZE, end_y * TILE_SIZE + 50, TILE_SIZE, TILE_SIZE))
    
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
            
            # Skill 1 activation
            if skill_1_button.collidepoint(mx, my) and player_turns < 4:
                player_skill_active = True  # Activate Skill 1
                continue

            # Skill 2 activation (Only available to Player, not Maze Master)
            if skill_2_button.collidepoint(mx, my) and not skill_2_used and player_turns < 4:
                skill_2_active = True  # Activate teleport mode
                continue
            
            if my < 50:
                continue

            clicked_x = mx // TILE_SIZE
            clicked_y = (my - 50) // TILE_SIZE
            
            # If Skill 2 is active, allow teleporting within 3x3 area
            if skill_2_active:
                if abs(clicked_x - player_x) <= 2 and abs(clicked_y - player_y) <= 2 and (clicked_x, clicked_y) not in walls:
                    player_x, player_y = clicked_x, clicked_y
                    skill_2_active = False  # Deactivate teleport mode
                    skill_2_used = True  # Mark skill as used
                continue
            
            if player_turns < 4:
                max_move = 4 if player_skill_active else 1
                
                if (abs(clicked_x - player_x) + abs(clicked_y - player_y) <= max_move) and (clicked_x, clicked_y) not in walls:
                    player_x, player_y = clicked_x, clicked_y
                    player_turns += 1
                    player_skill_active = False  # Deactivate skill after use
            else:
                if (clicked_x, clicked_y) != (player_x, player_y) and (clicked_x, clicked_y) != (end_x, end_y):
                    if pygame.key.get_pressed()[pygame.K_LSHIFT]:
                        wall_positions = [(clicked_x, clicked_y + i) for i in range(3)]
                    else:
                        wall_positions = [(clicked_x + i, clicked_y) for i in range(3)]
                    
                    valid = all(0 <= wx < GRID_SIZE and 0 <= wy < GRID_SIZE and (wx, wy) != (player_x, player_y) and (wx, wy) != (end_x, end_y) for wx, wy in wall_positions)
                    
                    if valid:
                        walls.update(wall_positions)
                        player_turns = 0
                        # Show turn notification when Maze Master completes their turn
                        show_turn_notification = True
                        turn_notification_timer = 0
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()