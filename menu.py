### Handles the game menu and launches game.py
import pygame
import subprocess  # Used to launch game.py

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 600, 400
WHITE, BLACK, BLUE, RED = (255, 255, 255), (0, 0, 0), (0, 0, 255), (255, 0, 0)

# Create screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Maze Runner")
font = pygame.font.Font(None, 40)
clock = pygame.time.Clock()

# Buttons
start_button = pygame.Rect(SCREEN_WIDTH // 2 - 50, 150, 100, 40)
help_button = pygame.Rect(SCREEN_WIDTH // 2 - 50, 100, 100, 40)
exit_button = pygame.Rect(SCREEN_WIDTH // 2 - 50, 200, 100, 40)

# Game States
menu = True
help_page = False

def draw_menu():
    """ Draws the main menu screen """
    screen.fill(WHITE)
    screen.blit(font.render("Maze Runner", True, BLACK), (SCREEN_WIDTH // 2 - 80, 50))
    pygame.draw.rect(screen, BLUE, start_button)
    pygame.draw.rect(screen, BLUE, help_button)
    pygame.draw.rect(screen, RED, exit_button)
    screen.blit(font.render("Start", True, WHITE), (start_button.x + 25, start_button.y + 5))
    screen.blit(font.render("Help", True, WHITE), (help_button.x + 25, help_button.y + 5))
    screen.blit(font.render("Exit", True, WHITE), (exit_button.x + 25, exit_button.y + 5))

def draw_help():
    """ Displays help instructions """
    screen.fill(WHITE)
    help_text = [
        "Maze Runner Game:", "1. Reach the red tile to win.",
        "2. Player can move 1 tile per turn.", "3. Use skills to gain advantages.",
        "4. Maze Master can place walls.", "Click anywhere to go back."
    ]
    for i, line in enumerate(help_text):
        screen.blit(font.render(line, True, BLACK), (50, 100 + i * 40))

# Main menu loop
running = True
while running:
    screen.fill(WHITE)
    if menu:
        draw_menu()
    elif help_page:
        draw_help()
    pygame.display.flip()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            if menu:
                if start_button.collidepoint(mx, my):
                    subprocess.Popen(["python", "game.py"])  # Start the game
                    running = False
                elif help_button.collidepoint(mx, my):
                    help_page = True
                    menu = False
                elif exit_button.collidepoint(mx, my):
                    running = False
            elif help_page:
                help_page = False
                menu = True  # Return to menu

pygame.quit()
