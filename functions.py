import pygame 
from pygame.locals import *
import math
from numpy.linalg import norm
import numpy as np


WIDTH, HEIGHT = 800, 600

# constantes
GRAVITY = 9.8/60
FRICTION = 0.01
DISSIPATION_RATE = 0.995  
fps = 60

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

#---------------------------------------------------------------------------------------------------------------------------------------

class Slider:
    def __init__(self, x, y, container_width, container_height, slider_width, slider_color=(255, 0, 0), container_color=(0, 0, 0)):
        self.container_x = x
        self.container_y = y
        self.container_width = container_width
        self.container_height = container_height
        self.slider_width = slider_width
        self.slider_height = container_height - 1
        self.slider_x = x
        self.slider_y = y + (container_height - self.slider_height) // 2
        self.slider_color = slider_color
        self.container_color = container_color
        self.dragging = False
        self.percentage = 0

    def handle_event(self, event):
        """Handle mouse events."""
        if event.type == MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if self.slider_x <= mouse_x <= self.slider_x + self.slider_width and \
                    self.slider_y <= mouse_y <= self.slider_y + self.slider_height:
                self.dragging = True

        elif event.type == MOUSEBUTTONUP:
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

        pygame.draw.rect(surface, self.container_color,
                        Rect(self.container_x, self.container_y, self.container_width, self.container_height))
        
        # Draw slider
        pygame.draw.rect(surface, self.slider_color,
                        Rect(self.slider_x, self.slider_y, self.slider_width, self.slider_height))
        
        # Prepare font
        if font is None:
            font = pygame.font.Font(None, 24)  # Default font, size 24
        
        # Render text
        text_surface = font.render(text, True, text_color)
        
        # Position the text centered above the slider
        text_rect = text_surface.get_rect()
        text_rect.center = (self.container_width // 2, self.slider_y - text_rect.height // 2 - 5)
        
        # Blit the text onto the surface
        surface.blit(text_surface, text_rect)


    def get_percentage(self):
        """Return the current percentage of the slider."""
        return self.percentage

#---------------------------------------------------------------------------------------------------------------------------------------

class Ball:
    def __init__(self, x, y, radius, color, mass=1):
        self.pos = np.array([x, y], dtype=np.float64)  # Use NumPy array for position
        self.velocity = np.zeros(2, dtype=np.float64)  # Use NumPy array for velocity
        self.radius = radius
        self.color = color
        self.mass = mass
        self.dragging = False

    def resolve_collision(self, curve):
        global FRICTION, GRAVITY, DISSIPATION_RATE
        
        closest_point, tangent_vector = curve.closest_point_and_tangent(self.pos)
        to_curve = closest_point - self.pos
        distance_to_curve = np.linalg.norm(to_curve)

        if distance_to_curve < self.radius:
            
            to_curve_unit = to_curve / distance_to_curve
            self.pos = closest_point - to_curve_unit * self.radius

            # Project velocity onto tangent vector
            tangent_norm = np.linalg.norm(tangent_vector)
            if tangent_norm > 0:
                tangent_unit = tangent_vector / tangent_norm
            else:
                tangent_unit = np.zeros(2)  # Avoid division by zero
            
            vel_tangent = np.dot(self.velocity, tangent_unit)

            # Update velocity along tangent
            self.velocity = vel_tangent * tangent_unit * (1 - FRICTION)

            # Apply dissipation
            self.velocity *= DISSIPATION_RATE

    def draw(self, screen):
        """Draw the ball on the screen."""
        pygame.draw.circle(screen, self.color, self.pos.astype(int), self.radius)

    def update(self, curve):
        """Update the ball's state."""
        if not self.dragging:
            # Apply GRAVITY
            self.velocity[1] += GRAVITY

            # Update position
            self.pos += self.velocity

            # Resolve collision with the Bézier curve
            self.resolve_collision(curve)

    def reset(self, pos1=400, pos2=0):
        """Reset the ball's position and velocity."""
        self.pos = np.array([pos1, pos2], dtype=np.float64)
        self.velocity = np.zeros(2, dtype=np.float64)

    def handle_event(self, event):
        """Handle mouse events for dragging and resetting the ball."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = np.array(pygame.mouse.get_pos(), dtype=np.float64)
            if np.linalg.norm(mouse_pos - self.pos) <= self.radius:
                self.dragging = True
            # Check if the reset button is clicked
            if 10 <= mouse_pos[0] <= 110 and 10 <= mouse_pos[1] <= 50:
                self.reset()
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.pos = np.array(pygame.mouse.get_pos(), dtype=np.float64)
            self.velocity = np.zeros(2, dtype=np.float64)

class BezierCurve:
    def __init__(self, points, color=(255, 255, 255), width=2):
        self.points = np.array(points)  # Use NumPy array for better performance
        self.color = color
        self.width = width
        self.dragging_point_index = None 

    def get_point(self, t):
        """Calculate the point on the Bézier curve at parameter t using De Casteljau's algorithm."""
        n = len(self.points) - 1
        binomial_coeffs = np.array([math.comb(n, i) for i in range(n + 1)])
        bernstein_poly = binomial_coeffs * (t ** np.arange(n + 1)) * ((1 - t) ** np.arange(n, -1, -1))
        point = np.dot(bernstein_poly, self.points)
        return point

    def get_tangent(self, t):
        """Calculate the tangent vector on the Bézier curve at parameter t."""
        n = len(self.points) - 1
        if n == 0:  # Edge case: No tangent for single-point curve
            return np.array([0, 0])
        
        diff_points = np.diff(self.points, axis=0)  # Differences between control points
        binomial_coeffs = np.array([math.comb(n - 1, i) for i in range(n)])
        bernstein_poly = binomial_coeffs * (t ** np.arange(n)) * ((1 - t) ** np.arange(n - 1, -1, -1))
        tangent = n * np.dot(bernstein_poly, diff_points)
        return tangent

    def closest_point_and_tangent(self, point, num_samples=100):
        """Find the closest point on the curve to the given point and its tangent."""
        t_values = np.linspace(0, 1, num_samples)
        curve_points = np.array([self.get_point(t) for t in t_values])
        distances = np.linalg.norm(curve_points - point, axis=1)
        min_index = np.argmin(distances)
        closest_point = curve_points[min_index]
        tangent_vector = self.get_tangent(t_values[min_index])
        return closest_point, tangent_vector

    def closest_point_angle(self, coord):
        """Calculate the angle between the tangent at the closest point and the x-axis."""
        _, tangent_vector = self.closest_point_and_tangent(coord)
        tangent_norm = np.linalg.norm(tangent_vector)
        if tangent_norm == 0:  # Handle zero-length tangent vector
            return 0.0
        
        normalized_tangent = tangent_vector / tangent_norm
        dot_product = np.dot(normalized_tangent, [1, 0])  # Compare with the x-axis
        dot_product = np.clip(dot_product, -1.0, 1.0)  # Ensure within arccos domain
        angle = math.acos(dot_product)
        return min(angle, math.pi - angle)

    def draw(self, screen, num_segments=100):
        """Draw the Bézier curve on the screen."""
        t_values = np.linspace(0, 1, num_segments + 1)
        points = [self.get_point(t) for t in t_values]
        for i in range(num_segments):
            pygame.draw.line(screen, self.color, points[i], points[i + 1], self.width)

    def draw_control_points(self, screen, point_color=(0, 255, 0), point_radius=5):
        """Draw control points as circles."""
        for point in self.points:
            pygame.draw.circle(screen, point_color, point.astype(int), point_radius)

    def handle_event(self, event):
        global WIDTH, HEIGHT
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                for i, point in enumerate(self.points):
                    dx, dy = event.pos[0] - point[0], event.pos[1] - point[1]
                    distance = math.sqrt(dx ** 2 + dy ** 2)
                    if distance < 10:  # Clicked near the control point
                        self.dragging_point_index = i
                        break

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left mouse button
                self.dragging_point_index = None

        elif event.type == pygame.MOUSEMOTION:
            if self.dragging_point_index is not None:
                self.points[self.dragging_point_index] = np.array([
                    max(0, min(WIDTH, event.pos[0])),
                    max(0, min(HEIGHT, event.pos[1]))])