import pygame

# Constants
GRID_SIZE = 24
TILE_SIZE = 25
SCREEN_WIDTH = GRID_SIZE * TILE_SIZE
SCREEN_HEIGHT = GRID_SIZE * TILE_SIZE + 50  # nag +50 ko para sa header na part

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
GRAY = (169, 169, 169)
BLUE = (0, 0, 255)
OVERLAY_BG = (0, 0, 0, 180)  # Semi-transparent black

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Turn-Based Maze Game")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)
large_font = pygame.font.Font(None, 72)

# Player start position
player_x, player_y = 0, 0

# Endpoint position, e change lang nya ni nato na para ma random or anha lang gyud na siya sa ubos
end_x, end_y = GRID_SIZE - 1, GRID_SIZE - 1

# Walls stored as a set of (x, y) positions
walls = set()


player_turns = 0  # Player 1 must move four times before Player 2 can act

def show_win_screen():
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill(OVERLAY_BG)
    screen.blit(overlay, (0, 0))
    win_text = large_font.render("You Win!", True, WHITE)
    screen.blit(win_text, (SCREEN_WIDTH // 2 - win_text.get_width() // 2, SCREEN_HEIGHT // 2 - win_text.get_height() // 2))
    pygame.display.flip()
    pygame.time.delay(2000)  # Pause for 2 seconds

def reset_game():
    global player_x, player_y, walls, player_turns
    player_x, player_y = 0, 0
    walls.clear()
    player_turns = 0

running = True
while running:
    screen.fill(WHITE)

    # Draw turn indicator, mao ni ang header 
    turn_text = "Player's Turn" if player_turns < 4 else "Maze Master's Turn"
    text_surface = font.render(turn_text, True, BLUE)
    screen.blit(text_surface, (SCREEN_WIDTH // 2 - text_surface.get_width() // 2, 10))

    # Draw grid
    for x in range(0, SCREEN_WIDTH, TILE_SIZE):
        for y in range(50, SCREEN_HEIGHT, TILE_SIZE):  # Start drawing below the turn indicator
            rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, BLACK, rect, 1)

    # Draw walls
    for wx, wy in walls:
        pygame.draw.rect(
            screen, GRAY, (wx * TILE_SIZE, wy * TILE_SIZE + 50, TILE_SIZE, TILE_SIZE)
        )

    # Draw player
    pygame.draw.rect(
        screen,
        GREEN,
        (player_x * TILE_SIZE, player_y * TILE_SIZE + 50, TILE_SIZE, TILE_SIZE),
    )

    # Draw endpoint
    pygame.draw.rect(
        screen, RED, (end_x * TILE_SIZE, end_y * TILE_SIZE + 50, TILE_SIZE, TILE_SIZE)
    )

    # Check for win condition
    if (player_x, player_y) == (end_x, end_y):
        show_win_screen()
        reset_game()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            if my < 50:
                continue  # Ignore clicks on the turn indicator

            clicked_x = mx // TILE_SIZE
            clicked_y = (my - 50) // TILE_SIZE  # Adjust for the top border

            if player_turns < 4:
                # Player 1 moves
                if (
                    ((abs(clicked_x - player_x) == 1 and clicked_y == player_y)
                    or (abs(clicked_y - player_y) == 1 and clicked_x == player_x))
                    and (clicked_x, clicked_y) not in walls
                ):
                    player_x, player_y = clicked_x, clicked_y
                    player_turns += 1  # Count Player 1's move
            else:
                # Player 2 (Maze Master) places a wall after Player 1's four moves
                if (clicked_x, clicked_y) != (player_x, player_y) and (clicked_x, clicked_y) != (end_x, end_y):
                    # Choose a direction (horizontal or vertical) based on mouse position
                    if pygame.key.get_pressed()[pygame.K_LSHIFT]:  # Hold shift to place walls vertically
                        wall_positions = [(clicked_x, clicked_y + i) for i in range(3)]
                    else:  # Default is horizontal
                        wall_positions = [(clicked_x + i, clicked_y) for i in range(3)]

                    # Ensure all positions are within bounds and not overlapping the player or endpoint
                    valid = all(
                        0 <= wx < GRID_SIZE and 0 <= wy < GRID_SIZE
                        and (wx, wy) != (player_x, player_y)
                        and (wx, wy) != (end_x, end_y)
                        for wx, wy in wall_positions
                    )

                    if valid:
                        walls.update(wall_positions)
                        player_turns = 0  # Reset turn counter after Maze Master acts

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
