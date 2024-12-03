
import pygame 
import math
import numpy as np
from config import *


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
        global BLACK
        t_values = np.linspace(0, 1, num_segments + 1)
        points = [self.get_point(t) for t in t_values]
        for i in range(num_segments):
            pygame.draw.line(screen, self.color, points[i], points[i + 1], self.width)

    def draw_control_points(self, screen, point_color=BLACK, point_radius=5):
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