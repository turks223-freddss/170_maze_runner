import pygame

# Constants
GRID_SIZE = 24
TILE_SIZE = 25
SCREEN_WIDTH = GRID_SIZE * TILE_SIZE
SCREEN_HEIGHT = GRID_SIZE * TILE_SIZE + 50

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
GRAY = (169, 169, 169)
BLUE = (0, 0, 255)
OVERLAY_BG = (0, 0, 0, 180)

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Turn-Based Maze Game")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)
large_font = pygame.font.Font(None, 72)

# Player start position
player_x, player_y = 0, 0
end_x, end_y = GRID_SIZE - 1, GRID_SIZE - 1
walls = set()
player_turns = 0
player_skill_active = False

# Skill button rects
skill_1_button = pygame.Rect(20, 10, 100, 30)
skill_2_button = pygame.Rect(130, 10, 100, 30)
skill_3_button = pygame.Rect(SCREEN_WIDTH - 230, 10, 100, 30)
skill_4_button = pygame.Rect(SCREEN_WIDTH - 120, 10, 100, 30)

def draw_buttons():
    pygame.draw.rect(screen, BLUE, skill_1_button)
    pygame.draw.rect(screen, BLUE, skill_2_button)
    pygame.draw.rect(screen, BLUE, skill_3_button)
    pygame.draw.rect(screen, BLUE, skill_4_button)
    
    screen.blit(font.render("Skill 1", True, WHITE), (30, 15))
    screen.blit(font.render("Skill 2", True, WHITE), (140, 15))
    screen.blit(font.render("Skill 3", True, WHITE), (SCREEN_WIDTH - 220, 15))
    screen.blit(font.render("Skill 4", True, WHITE), (SCREEN_WIDTH - 110, 15))

def reset_game():
    global player_x, player_y, walls, player_turns, player_skill_active
    player_x, player_y = 0, 0
    walls.clear()
    player_turns = 0
    player_skill_active = False

running = True
while running:
    screen.fill(WHITE)
    
    turn_text = "Player's Turn" if player_turns < 4 else "Maze Master's Turn"
    text_surface = font.render(turn_text, True, BLUE)
    screen.blit(text_surface, (SCREEN_WIDTH // 2 - text_surface.get_width() // 2, 10))
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
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            
            if skill_1_button.collidepoint(mx, my) and player_turns < 4:
                player_skill_active = True  # Activate Skill 1
                continue
            
            if my < 50:
                continue
            
            clicked_x = mx // TILE_SIZE
            clicked_y = (my - 50) // TILE_SIZE
            
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
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
