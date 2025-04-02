import pygame
import subprocess
import textwrap
import os

# Get the directory where this script (menu.py) is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 600, 400
WHITE, BLACK, BLUE, RED, GRAY = (255, 255, 255), (0, 0, 0), (0, 0, 255), (255, 0, 0), (200, 200, 200)
HOVER_BLUE, HOVER_RED = (0, 100, 255), (200, 0, 0)
LIGHT_BLUE = (200, 220, 255)
DARK_BLUE = (0, 50, 150)

# Create screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Maze Runner")
font = pygame.font.Font(None, 40)
small_font = pygame.font.Font(None, 22)
title_font = pygame.font.Font(None, 48)
section_font = pygame.font.Font(None, 32)
clock = pygame.time.Clock()

# Game States
menu = True
help_page = False
mode_select = False

# Button dimensions for main menu
button_width = 120
button_height = 40
button_spacing = 20
start_y = SCREEN_HEIGHT // 2 - (3 * button_height + 2 * button_spacing) // 2

# Buttons for main menu - centered vertically and horizontally
buttons = {
    "Play": pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, start_y, button_width, button_height),
    "Help": pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, start_y + button_height + button_spacing, button_width, button_height),
    "Exit": pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, start_y + 2 * (button_height + button_spacing), button_width, button_height)
}

# Buttons for mode selection - making them wider
button_width = 250
mode_buttons = {
    "PvP": pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, 100, button_width, 40),
    "Play as Runner": pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, 150, button_width, 40),
    "Play as Master": pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, 200, button_width, 40),
    "Back": pygame.Rect(SCREEN_WIDTH // 2 - 50, 250, 100, 40)
}

# Scroll variables
scroll_offset = 0
scroll_speed = 15
max_scroll_offset = 0

# Help sections with icons and colors
help_sections = {
    "Basics": {
        "color": BLUE,
        "content": [
            "Runner starts at (0,0) and has 4 moves each turn",
            "Goal: Reach bottom-right corner",
            "Movement is turn-based",
            "Game ends when runner reaches goal or is trapped",
            "Game ends when master occupies 30% of the maze"
        ]
    },
    "Runner Skills": {
        "color": (0, 150, 0),
        "content": [
            "(Skill 1) Sprint: Move up to 4 tiles (Consumes 2 moves)",
            "(Skill 2) Teleport: Jump to distant tile once",
            "(Skill 3) Break Wall: Remove obstacle (every 4 rounds)"
        ]
    },
    "Master Skills": {
        "color": (150, 0, 0),
        "content": [
            "(Skill 1) Double Wall: Place 2 walls in 1 turn",
            "(Skill 2) Diagonal Wall: Place walls diagonally once",
            "(Skill 3) Force Teleport: Move runner randomly"
        ]
    }
}

def draw_text(text, font, color, x, y, centered=True):
    """Utility function to draw text"""
    text_surface = font.render(text, True, color)
    if centered:
        x = x - text_surface.get_width() // 2
    screen.blit(text_surface, (x, y))

def draw_menu():
    """Draws the main menu screen"""
    screen.fill(WHITE)

    # Title with background
    pygame.draw.rect(screen, DARK_BLUE, (0, 0, SCREEN_WIDTH, 60))
    draw_text("Maze Runner", title_font, WHITE, SCREEN_WIDTH // 2, 15)

    # Get mouse position once
    mouse_x, mouse_y = pygame.mouse.get_pos()

    # Draw buttons with hover effects and improved visuals
    for text, rect in buttons.items():
        # Button background with hover effect
        color = HOVER_BLUE if rect.collidepoint(mouse_x, mouse_y) else (BLUE if text != "Exit" else RED)
        
        # Draw button with rounded corners
        pygame.draw.rect(screen, color, rect, border_radius=10)
        
        # Center text in button
        text_surface = font.render(text, True, WHITE)
        text_x = rect.centerx - text_surface.get_width() // 2
        text_y = rect.centery - text_surface.get_height() // 2
        screen.blit(text_surface, (text_x, text_y))

def draw_help():
    """Displays help text with sections and visual elements"""
    screen.fill(WHITE)
    
    # Title
    pygame.draw.rect(screen, DARK_BLUE, (0, 0, SCREEN_WIDTH, 60))
    draw_text("How to Play", title_font, WHITE, SCREEN_WIDTH // 2, 15)
    
    # Calculate visible area
    visible_height = SCREEN_HEIGHT - 70
    y_pos = 80 - scroll_offset
    
    # Draw sections
    total_height = 0
    for section, data in help_sections.items():
        section_height = len(data["content"]) * 30 + 90  # Header + content + padding
        total_height += section_height
        
        # Only draw if section is in view
        if y_pos + section_height > 60 and y_pos < SCREEN_HEIGHT:
            # Section header
            section_bg = pygame.Rect(20, y_pos, SCREEN_WIDTH - 40, 40)
            pygame.draw.rect(screen, data["color"], section_bg, border_radius=10)
            draw_text(section, section_font, WHITE, SCREEN_WIDTH // 2, y_pos + 5)
            
            # Content box
            content_bg = pygame.Rect(30, y_pos + 45, SCREEN_WIDTH - 60, len(data["content"]) * 30 + 10)
            pygame.draw.rect(screen, LIGHT_BLUE, content_bg, border_radius=5)
            
            # Content text
            for i, line in enumerate(data["content"]):
                draw_text(line, small_font, BLACK, 45, y_pos + 55 + i * 30, centered=False)
        
        y_pos += section_height

    # Update max scroll offset
    global max_scroll_offset
    max_scroll_offset = max(0, total_height - visible_height)

def handle_scrolling(event):
    """Handles scrolling input with improved boundaries"""
    global scroll_offset
    if event.button == 4:  # Scroll up
        scroll_offset = max(0, scroll_offset - scroll_speed)
    elif event.button == 5:  # Scroll down
        scroll_offset = min(max_scroll_offset, scroll_offset + scroll_speed)

def draw_mode_select():
    """Draws the mode selection screen"""
    screen.fill(WHITE)

    # Title with background
    pygame.draw.rect(screen, DARK_BLUE, (0, 0, SCREEN_WIDTH, 60))
    draw_text("Select Game Mode", title_font, WHITE, SCREEN_WIDTH // 2, 15)

    # Get mouse position once
    mouse_x, mouse_y = pygame.mouse.get_pos()

    # Draw buttons with hover effects and improved visuals
    for text, rect in mode_buttons.items():
        # Button background with hover effect
        color = HOVER_BLUE if rect.collidepoint(mouse_x, mouse_y) else BLUE
        if text == "Back":
            color = HOVER_RED if rect.collidepoint(mouse_x, mouse_y) else RED
        
        # Draw button with rounded corners
        pygame.draw.rect(screen, color, rect, border_radius=10)
        
        # Center text in button
        text_surface = font.render(text, True, WHITE)
        text_x = rect.centerx - text_surface.get_width() // 2
        text_y = rect.centery - text_surface.get_height() // 2
        screen.blit(text_surface, (text_x, text_y))

# Main menu loop
running = True
while running:
    screen.fill(WHITE)

    if menu:
        draw_menu()
    elif help_page:
        draw_help()
    elif mode_select:
        draw_mode_select()

    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()

            if menu:
                if buttons["Play"].collidepoint(mx, my):
                    mode_select = True
                    menu = False
                elif buttons["Help"].collidepoint(mx, my):
                    help_page, menu = True, False
                elif buttons["Exit"].collidepoint(mx, my):
                    running = False
            elif help_page:
                if event.button in (4, 5):
                    handle_scrolling(event)
                else:
                    help_page, menu = False, True
            elif mode_select:
                if mode_buttons["PvP"].collidepoint(mx, my):
                    subprocess.Popen(["python", os.path.join(SCRIPT_DIR, "game.py"), "pvp"])
                    running = False
                elif mode_buttons["Play as Runner"].collidepoint(mx, my):
                    subprocess.Popen(["python", os.path.join(SCRIPT_DIR, "game.py"), "runner"])
                    running = False
                elif mode_buttons["Play as Master"].collidepoint(mx, my):
                    subprocess.Popen(["python", os.path.join(SCRIPT_DIR, "game.py"), "master"])
                    running = False
                elif mode_buttons["Back"].collidepoint(mx, my):
                    mode_select = False
                    menu = True

pygame.quit()
