import pygame 
from pygame.locals import *

WIDTH, HEIGHT = 800, 600

# Colors
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GRAY = (200, 200, 200)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

#---------------------------------------------------------------------------------------------------------------------------------------

# Função para debug
def print_text(surface, text, x, y, font_name="Arial", font_size=24, color=(0, 0, 0), center=False):
    # Cria uma fonte
    font = pygame.font.SysFont(font_name, font_size)
    
    # Render the text into a surface
    text_surface = font.render(text, True, color)
    
    # Get the rectangle of the text surface
    text_rect = text_surface.get_rect()
    
    # Center the text if needed
    if center:
        text_rect.center = (x, y)
    else:
        text_rect.topleft = (x, y)
    
    # Blit the text surface onto the main surface
    surface.blit(text_surface, text_rect)
