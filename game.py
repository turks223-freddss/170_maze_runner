import pygame

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
walls_placed = 0
player_turns = 0
player_skill_active = False
maze_skill_active = False
skill_2_active = False  # Skill 2 activation flag
skill_2_used = False  # Track if skill 2 has been used
game_won = False  # Flag to track if the player has won

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

def reset_game():
    global player_x, player_y, walls, player_turns, player_skill_active, skill_2_active, skill_2_used, game_won
    player_x, player_y = 0, 0
    walls.clear()
    player_turns = 0
    player_skill_active = False
    maze_skill_active = False
    skill_2_active = False
    skill_2_used = False  # Reset skill usage
    game_won = False  # Reset win state

running = True
while running:
    screen.fill(OFF_WHITE)

    # Check if the player has reached the goal
    if player_x == end_x and player_y == end_y:
        game_won = True
    
    if game_won:
        turn_text = "Congratulations!"
        screen.blit(font.render(turn_text, True, BLUE), (SCREEN_WIDTH // 2 - 50, 15))
        pygame.display.flip()
        pygame.time.delay(2000)  # Display message for 2 seconds
        reset_game()
        continue  # Restart the loop after resetting

    else:
        turn_text = "Player's Turn" if player_turns < 4 else "Maze Master's Turn"
    
    text_surface = font.render(turn_text, True, BLUE)
    screen.blit(text_surface, (SCREEN_WIDTH // 2 - text_surface.get_width() // 2, 15))
    draw_buttons()
    
    for x in range(0, SCREEN_WIDTH, TILE_SIZE):
        for y in range(50, SCREEN_HEIGHT, TILE_SIZE):
            pygame.draw.rect(screen, BLACK, pygame.Rect(x, y, TILE_SIZE, TILE_SIZE), 1)
    
    for wx, wy in walls:
        pygame.draw.rect(screen, GRAY, (wx * TILE_SIZE, wy * TILE_SIZE + 50, TILE_SIZE, TILE_SIZE))
    
    pygame.draw.rect(screen, GREEN, (player_x * TILE_SIZE, player_y * TILE_SIZE + 50, TILE_SIZE, TILE_SIZE))
    pygame.draw.rect(screen, RED, (end_x * TILE_SIZE, end_y * TILE_SIZE + 50, TILE_SIZE, TILE_SIZE))
    
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
                player_skill_active = True  # Activate Skill 1 (Player)
                continue

            if skill_1_button.collidepoint(mx, my) and player_turns == 4:
                maze_skill_active = True  # Activate Skill 1 (Maze Master)
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

            else:   # Maze master's Turn

                if (clicked_x, clicked_y) != (player_x, player_y) and (clicked_x, clicked_y) != (end_x, end_y):
                    if maze_skill_active:   # Skill 1 is activated (Maze master)

                        if walls_placed < 2:    # Required to place 2 walls
                            if pygame.key.get_pressed()[pygame.K_LSHIFT]:
                                wall_positions = [(clicked_x, clicked_y + i) for i in range(3)]
                            else:
                                wall_positions = [(clicked_x + i, clicked_y) for i in range(3)]
                            walls_placed += 1
                        
                        valid = all(0 <= wx < GRID_SIZE and 0 <= wy < GRID_SIZE and (wx, wy) != (player_x, player_y) and (wx, wy) != (end_x, end_y) for wx, wy in wall_positions)
                        
                        if valid:
                            walls.update(wall_positions)
                            if walls_placed < 2:    # Checks if 2 walls have been placed
                                player_turns += 1
                            else:                   # 2 walls have been placed, exit skill and end turn.
                                player_turns = 0
                                walls_placed = 0
                                maze_skill_active = False
                            
                    else:   # Basic Maze master movement

                        if pygame.key.get_pressed()[pygame.K_LSHIFT]:
                            wall_positions = [(clicked_x, clicked_y + i) for i in range(3)]
                        else:
                            wall_positions = [(clicked_x + i, clicked_y) for i in range(3)]
                        
                        valid = all(0 <= wx < GRID_SIZE and 0 <= wy < GRID_SIZE and (wx, wy) != (player_x, player_y) and (wx, wy) != (end_x, end_y) for wx, wy in wall_positions)
                        
                        if valid:
                            walls.update(wall_positions)
                            player_turns = 0
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
