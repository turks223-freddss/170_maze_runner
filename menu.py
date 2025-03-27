import pygame
import subprocess
import textwrap

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 600, 400
WHITE, BLACK, BLUE, RED, GRAY = (255, 255, 255), (0, 0, 0), (0, 0, 255), (255, 0, 0), (200, 200, 200)
HOVER_BLUE, HOVER_RED = (0, 100, 255), (200, 0, 0)

# Create screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Maze Runner")
font = pygame.font.Font(None, 40)
small_font = pygame.font.Font(None, 22)
clock = pygame.time.Clock()

# Buttons
buttons = {
    "Start": pygame.Rect(SCREEN_WIDTH // 2 - 50, 150, 100, 40),
    "Help": pygame.Rect(SCREEN_WIDTH // 2 - 50, 100, 100, 40),
    "Exit": pygame.Rect(SCREEN_WIDTH // 2 - 50, 200, 100, 40)
}

# Game States
menu = True
help_page = False

# Scroll variables
scroll_offset = 0
scroll_speed = 15
max_scroll_offset = 0

# Help text (wrapped)
raw_help_text = [
    "The runner starts at the top-left corner (0,0).",
    "Goal: Reach the bottom-right corner.",
    "Movement is turn-based.",
    "Use skills to bypass obstacles or move faster.",
    "Walls can be placed to block paths.",
    "Game ends when the runner reaches the goal or is trapped.",
    "",
    "Skills:",
    "Runner Skill 1: Move up to 4 tiles, costs 2 turns.",
    "Runner Skill 2: Teleport to a distant tile once.",
    "Runner Skill 3: Break a wall (unlocks every 4 rounds).",
    "Maze Master Skill 1: Place 2 walls in 1 turn (every 2 turns).",
    "Maze Master Skill 2: Place walls diagonally once.",
    "Maze Master Skill 3: Teleport player randomly.",
    "",
    "Game Elements:",
    "Walls: Block paths strategically.",
    "Turn System: Players take turns moving or placing walls.",
    "Notifications: Turn indicators appear visually.",
    "Highlighting: Clickable areas are highlighted.",
    "",
    "Win: Reach the goal tile.",
    "Lose: Get completely blocked.",
    "",
    "Scroll to read. Click to return."
]

# Wrap text to fit screen width (max 50 characters per line)
help_text = []
for line in raw_help_text:
    help_text.extend(textwrap.wrap(line, width=50))

def draw_text(text, font, color, x, y):
    """ Utility function to draw centered text inside buttons """
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x + (100 - text_surface.get_width()) // 2, y + 5))

def draw_menu():
    """ Draws the main menu screen """
    screen.fill(WHITE)

    # Title
    title_text = font.render("Maze Runner", True, BLACK)
    screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 50))

    # Get mouse position once
    mouse_x, mouse_y = pygame.mouse.get_pos()

    # Draw buttons with hover effects
    for text, rect in buttons.items():
        color = HOVER_BLUE if rect.collidepoint(mouse_x, mouse_y) else (BLUE if text != "Exit" else RED)
        pygame.draw.rect(screen, color, rect)
        draw_text(text, font, WHITE, rect.x, rect.y)

def draw_help():
    """ Displays help text with a sticky navbar """
    global scroll_offset, max_scroll_offset

    screen.fill(WHITE)

    # Sticky Title (Navbar Effect)
    pygame.draw.rect(screen, WHITE, (0, 0, SCREEN_WIDTH, 50))  # Background bar
    title_text = font.render("How to Play", True, BLACK)
    screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 10))  # Fixed at top

    # Calculate max scrollable height
    total_text_height = len(help_text) * 25
    max_scroll_offset = max(0, total_text_height - (SCREEN_HEIGHT - 70))  # Adjusted for navbar

    # Render text with scrolling
    y_offset = 60 - scroll_offset  # Below navbar
    for line in help_text:
        screen.blit(small_font.render(line, True, BLACK), (30, y_offset))
        y_offset += 25

def handle_scrolling(event):
    """ Handles scrolling input """
    global scroll_offset
    if event.button == 4:  # Scroll up
        scroll_offset = max(0, scroll_offset - scroll_speed)
    elif event.button == 5:  # Scroll down
        scroll_offset = min(max_scroll_offset, scroll_offset + scroll_speed)

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
                if buttons["Start"].collidepoint(mx, my):
                    subprocess.Popen(["python", "game.py"])  # Start the game
                    running = False
                elif buttons["Help"].collidepoint(mx, my):
                    help_page, menu = True, False
                elif buttons["Exit"].collidepoint(mx, my):
                    running = False
            elif help_page:
                if event.button in (4, 5):  # Scroll event (mouse wheel up/down)
                    handle_scrolling(event)
                else:
                    help_page, menu = False, True  # Click anywhere to return

pygame.quit()
