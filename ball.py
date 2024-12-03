import pygame 
from pygame.locals import *
from numpy.linalg import norm
import numpy as np
from bezier_curve import *
from config import *


class Ball:
    def __init__(self, x, y, radius, color):
        self.pos = np.array([x, y], dtype=np.float64)  # Vetor Posição
        self.velocity = np.zeros(2, dtype=np.float64)  # Vetor Velocidade
        self.radius = radius
        self.color = color
        self.dragging = False

        # Animação do Sonic sendo Carregado
        lifted_image = "img/lifted.png"
        self.lifted = pygame.image.load(lifted_image).convert_alpha() if lifted_image else None
        self.lifted = pygame.transform.scale(self.lifted, (radius * 4, radius * 2)) if self.lifted else None

        # Animação de Rolar
        self.roll_images = [
            pygame.image.load(f"img/roll{i}.png").convert_alpha() for i in range(1, 5)
        ]
        self.roll_images = [
            pygame.transform.scale(img, (radius * 2, radius * 2)) for img in self.roll_images
        ]

        self.roll_index = 0  # Índice de frame de Animação
        self.animation_speed = 0.1  # Velocidade da Animação
        self.time_since_last_frame = 0  # Timer para a Animação

        # Carregar as Animações Estática
        self.steady_images = [
            pygame.image.load(f"img/steady{i}.png").convert_alpha() for i in range(1, 3)
        ]
        self.steady_images = [
            pygame.transform.scale(img, (radius * 3, radius * 3)) for img in self.steady_images
        ]

        self.steady_index = 0  # índice da animção estática


    def draw(self, screen, dt):
        
        if self.dragging and self.lifted:
            screen.blit(self.lifted, (self.pos[0] - self.radius, self.pos[1] - self.radius))
        else:
            speed = np.linalg.norm(self.velocity)
            if speed > 5e-1:  # Se não estiver parado
                self.time_since_last_frame += dt
                if self.time_since_last_frame >= self.animation_speed:
                    self.time_since_last_frame = 0
                    self.roll_index = (self.roll_index + 1) % len(self.roll_images)

                # Desenhar o quadro atual da animação de rolamento
                current_image = self.roll_images[self.roll_index]
                screen.blit(current_image, (self.pos[0] - self.radius, self.pos[1] - self.radius))
            else:
                # A bola está estacionária, desenhe como um círculo
                self.time_since_last_frame += dt
                if self.time_since_last_frame >= self.animation_speed:
                    self.time_since_last_frame = 0
                    self.steady_index = (self.steady_index + 1) % len(self.steady_images)

                # Desenhar o quadro atual da animação estacionária
                current_image = self.steady_images[self.steady_index]
                screen.blit(current_image, (self.pos[0] - self.radius, self.pos[1] - self.radius*2))

    def update(self, bezier_curve, dt, GRAVITY, FRICTION):
        # Aplicar aceleração da gravidade à velocidade vertical
        self.velocity[1] += GRAVITY * dt

        # Atualizar posição com base na velocidade
        self.pos += self.velocity * dt

        # Verificar colisão com a curva de Bézier
        closest_point, tangent_vector = bezier_curve.closest_point_and_tangent(self.pos)
        distance = np.linalg.norm(self.pos - closest_point)

        if distance < self.radius:
            # Ajustar posição para não atravessar a curva
            normal = (self.pos - closest_point) / distance if distance > 0 else np.array([0, 1])
            overlap = self.radius - distance
            self.pos += normal * overlap

            # Projetar velocidade no vetor tangente para simular deslizamento
            tangent_unit = tangent_vector / np.linalg.norm(tangent_vector)
            self.velocity = np.dot(self.velocity, tangent_unit) * tangent_unit

            self.velocity *= (1-FRICTION)




    def reset(self, pos1=WIDTH//2, pos2=HEIGHT//6):
            """Reset the ball's position and velocity."""
            self.pos = np.array([pos1, pos2], dtype=np.float64)
            self.velocity = np.zeros(2, dtype=np.float64)


    def handle_event(self, event, reset_button_area=(10, 10, 100, 40)):
        """Lida com eventos de interação do usuário."""
        mouse_pos = np.array(pygame.mouse.get_pos(), dtype=np.float64)

        if event.type == pygame.MOUSEBUTTONDOWN:
            # Verificar se a bola está sendo clicada
            if norm(mouse_pos - self.pos) <= self.radius:
                self.dragging = True
            # Verificar se o botão de reset foi clicado
            x1, y1, w, h = reset_button_area
            if x1 <= mouse_pos[0] <= x1 + w and y1 <= mouse_pos[1] <= y1 + h:
                self.reset()

        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False

        elif event.type == pygame.MOUSEMOTION and self.dragging:
            # Atualizar a posição da bola enquanto arrastada
            self.pos = mouse_pos
            self.velocity = np.zeros(2, dtype=np.float64)



