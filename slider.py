import pygame
from pygame.locals import *

class Slider:
    def __init__(self, x, y, container_width, container_height, slider_width, percentage=50, slider_color=(255, 0, 0), container_color=(0, 0, 0)):
        self.container_x = x
        self.container_y = y
        self.container_width = container_width
        self.container_height = container_height
        self.slider_width = slider_width
        self.slider_height = container_height - 1
        self.slider_color = slider_color
        self.container_color = container_color
        self.dragging = False
        # Inicializa a porcentagem
        self.percentage = percentage
        # Calcula a posição inicial do slider com base na porcentagem
        self.slider_x = x + int((percentage / 100) * (container_width - slider_width))
        self.slider_y = y + (container_height - self.slider_height) // 2

    def handle_event(self, event):
        """Handle mouse events."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if self.slider_x <= mouse_x <= self.slider_x + self.slider_width and \
                    self.slider_y <= mouse_y <= self.slider_y + self.slider_height:
                self.dragging = True

        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False

    def update(self):
        """Update the slider's position if dragging."""
        if self.dragging:
            mouse_x, _ = pygame.mouse.get_pos()
            self.slider_x = mouse_x - self.slider_width // 2
            # Keep the slider within the container
            self.slider_x = max(self.container_x, 
                                min(self.slider_x, self.container_x + self.container_width - self.slider_width))
            # Update percentage
            self.percentage = ((self.slider_x - self.container_x) / (self.container_width - self.slider_width)) * 100

    def draw(self, surface, text, font=None, text_color=(0, 0, 0)):
        """Draw the slider and the container."""
        # Draw container
        pygame.draw.rect(surface, self.container_color,
                         pygame.Rect(self.container_x, self.container_y, self.container_width, self.container_height))
        
        # Draw slider
        pygame.draw.rect(surface, self.slider_color,
                         pygame.Rect(self.slider_x, self.slider_y, self.slider_width, self.slider_height))
        
        # Prepare font
        if font is None:
            font = pygame.font.Font(None, 24)  # Default font, size 24
        
        # Render text
        text_surface = font.render(text, True, text_color)
        
        # Position the text centered above the slider
        text_rect = text_surface.get_rect()
        text_rect.center = (self.container_x + self.container_width // 2, self.slider_y - text_rect.height // 2 - 5)
        
        # Blit the text onto the surface
        surface.blit(text_surface, text_rect)

    def get_percentage(self):
        """Return the current percentage of the slider."""
        return self.percentage