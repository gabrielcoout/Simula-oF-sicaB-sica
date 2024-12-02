import pygame 
from pygame.locals import *
import math
from numpy.linalg import norm
import numpy as np


WIDTH, HEIGHT = 800, 600

# constantes
gravity = 9.8/60
friction = 0.01
dissipation_rate = 0.995  
fps = 60

# Colors
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GRAY = (200, 200, 200)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

#---------------------------------------------------------------------------------------------------------------------------------------

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

class Ball:
    def __init__(self, x, y, radius, color, mass=1):
        self.pos = [x, y]
        self.velocity = [0, 0]
        self.radius = radius
        self.color = color
        self.mass = mass
        self.dragging = False

    def resolve_collision(self, curve):
        global friction, gravity

        # Encontrar o ponto mais próximo na curva e o vetor tangente
        closest_point, tangent_vector = curve.closest_point_and_tangent(self.pos)

        # Vetor da bola até o ponto da curva
        to_curve = [closest_point[0] - self.pos[0], closest_point[1] - self.pos[1]]
        distance_to_curve = math.sqrt(to_curve[0] ** 2 + to_curve[1] ** 2)

        if distance_to_curve < self.radius:  # Detectar colisão
            # Corrigir a posição da bola
            to_curve_unit = [to_curve[0] / distance_to_curve, to_curve[1] / distance_to_curve]
            self.pos[0] = closest_point[0] - to_curve_unit[0] * self.radius
            self.pos[1] = closest_point[1] - to_curve_unit[1] * self.radius

            # Projetar a velocidade no vetor tangente
            tangent_length = math.sqrt(tangent_vector[0] ** 2 + tangent_vector[1] ** 2)
            if tangent_length > 0:
                tangent_unit = [tangent_vector[0] / tangent_length, tangent_vector[1] / tangent_length]
            else:
                tangent_unit = [0, 0]  # Evitar divisão por zero

            vel_tangent = (
                self.velocity[0] * tangent_unit[0] +
                self.velocity[1] * tangent_unit[1]
            )

            # Atualizar velocidade projetada na tangente
            self.velocity[0] = vel_tangent * tangent_unit[0] * (1 - friction)
            self.velocity[1] = vel_tangent * tangent_unit[1] * (1 - friction)

            # Dissipação da energia devido à colisão
            self.velocity[0] *= dissipation_rate
            self.velocity[1] *= dissipation_rate


    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.pos[0]), int(self.pos[1])), self.radius)

    def update(self, bezier_curve):
        if not self.dragging:
            global gravity, dissipation_rate
            self.velocity[1] += gravity

            # Atualizar posição
            self.pos[0] += self.velocity[0]
            self.pos[1] += self.velocity[1]

            # Resolver colisão com a curva de Bézier
            self.resolve_collision(bezier_curve)

            # Dissipação
            self.velocity[0] *= dissipation_rate
            self.velocity[1] *= dissipation_rate

    def reset(self,pos1=WIDTH//2,pos2=0):
        self.pos = [pos1,pos2]
        self.velocity = [0, 0]
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check if the ball is being clicked
            mouse_pos = pygame.mouse.get_pos()
            dx = mouse_pos[0] - self.pos[0]
            dy = mouse_pos[1] - self.pos[1]
            if math.sqrt(dx**2 + dy**2) <= self.radius:
                self.dragging = True
            # Check if the reset button is clicked
            if 10 <= mouse_pos[0] <= 110 and 10 <= mouse_pos[1] <= 50:
                self.reset()
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.pos = list(pygame.mouse.get_pos())
            self.velocity = [0, 0]  

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
    
class BezierCurve:
    def __init__(self, points, color=(255, 255, 255), width=2):
        self.points = points
        self.color = color
        self.width = width
        self.dragging_point_index = None 

    def get_point(self, t):
        """Calculate the point on the Bézier curve at parameter t."""
        n = len(self.points) - 1
        point = [0, 0]
        for i in range(n + 1):
            binomial_coeff = math.comb(n, i)
            bernstein_poly = binomial_coeff * (t ** i) * ((1 - t) ** (n - i))
            point[0] += bernstein_poly * self.points[i][0]
            point[1] += bernstein_poly * self.points[i][1]
        return point
    
    def get_tangent(self, t):
        """Calculate the tangent vector on the Bézier curve at parameter t."""
        n = len(self.points) - 1
        tangent = [0, 0]
        for i in range(n):
            binomial_coeff = math.comb(n - 1, i)
            bernstein_poly = binomial_coeff * (t ** i) * ((1 - t) ** (n - 1 - i))
            tangent[0] += bernstein_poly * (self.points[i + 1][0] - self.points[i][0]) * n
            tangent[1] += bernstein_poly * (self.points[i + 1][1] - self.points[i][1]) * n
        return tangent
    
    def closest_point_and_tangent(self, point):
        min_distance = float('inf')
        closest_point = None
        tangent_vector = None

        for t in [i / 100 for i in range(101)]:
            curve_point = self.get_point(t)
            dx, dy = curve_point[0] - point[0], curve_point[1] - point[1]
            distance = math.sqrt(dx ** 2 + dy ** 2)
            if distance < min_distance:
                min_distance = distance
                closest_point = curve_point
                tangent_vector = self.get_tangent(t)

        return closest_point, tangent_vector


    def draw(self, screen, num_segments=100):
        for i in range(num_segments):
            t1 = i / num_segments
            t2 = (i + 1) / num_segments
            p1 = self.get_point(t1)
            p2 = self.get_point(t2)
            pygame.draw.line(screen, self.color, p1, p2, self.width)

    def draw_control_points(self, screen, point_color=(0, 255, 0), point_radius=5):
        for point in self.points:
            pygame.draw.circle(screen, point_color, (int(point[0]), int(point[1])), point_radius)

    def handle_event(self, event):
        """
        Handle mouse events to allow dragging of control points.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                for i, point in enumerate(self.points):
                    dx = event.pos[0] - point[0]
                    dy = event.pos[1] - point[1]
                    distance = math.sqrt(dx ** 2 + dy ** 2)
                    if distance < 10:  # Clicked near the control point
                        self.dragging_point_index = i
                        break

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left mouse button
                self.dragging_point_index = None

        elif event.type == pygame.MOUSEMOTION:
            if self.dragging_point_index is not None:
                self.points[self.dragging_point_index] =  [max(0,min([WIDTH, event.pos[0]])),max(0,min(HEIGHT,event.pos[1]))]

    def closest_point_angle(self, coord):
        # Get the closest point and tangent vector
        _, tangent_vector = self.closest_point_and_tangent(coord)
        
        # Normalize the tangent vector
        tangent_magnitude = math.sqrt(tangent_vector[0]**2 + tangent_vector[1]**2)
        normalized_tangent = [tangent_vector[0] / tangent_magnitude, tangent_vector[1] / tangent_magnitude]
        
        # Since the coordinate system flips the y-axis, use the x-axis [[1, 0], [0, -1]]
        axis_vector = [1, 0]  # Standard positive x-axis

        # Compute the dot product
        dot_product = normalized_tangent[0] * axis_vector[0] + normalized_tangent[1] * axis_vector[1]

        # Ensure the value is within the domain of arccos due to floating-point errors
        dot_product = max(-1.0, min(1.0, dot_product))

        # Compute the angle in radians
        angle = math.acos(dot_product)

        # Return the acute angle (it is always positive in [0, π/2])
        return min(angle, math.pi - angle)
   
