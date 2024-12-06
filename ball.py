import pygame 
from pygame.locals import *
from numpy.linalg import norm
import numpy as np
from bezier_curve import *
from config import *

STANDARD_GRAVITY = 9.80665
TIME_TO_FALL = 1.5
pixels_per_meter = HEIGHT / (0.5 * 9.81 * TIME_TO_FALL**2)

class Ball:
    def __init__(self, x, y, radius, mass, color):
        self.pos = np.array([x, y], dtype=np.float64)  # Vetor Posição
        self.velocity = np.zeros(2, dtype=np.float64)  # Vetor Velocidade
        self.aceleration = np.zeros(2, dtype=np.float64)
        self.radius = radius
        self.mass = mass
        self.color = color
        self.dragging = False
        self.sliding = False

        # funções para o tempo
        self.elapsed_time = 0  # Tempo total
        self.start_time = 0  # Tempo quando a bola para de ser arrastada

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
            speed = np.linalg.norm(self.velocity/pixels_per_meter)
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

    def update(self, bezier_curve:BezierCurve, dt:float, GRAVITY:float, FRICTION:float):
        # Encontrar ponto mais próximo na curva e vetor tangente
        closest_point, tangent_vector = bezier_curve.closest_point_and_tangent(self.pos, 800)
        distance = np.linalg.norm(self.pos - closest_point)

        if distance - self.radius< 1e-3:
            if not self.sliding or norm(self.velocity)<0.1:  # Apenas no primeiro toque
                minimos = bezier_curve.find_max_point(self.pos)
                index = np.argmin([np.linalg.norm(i) for i in minimos])
                height = minimos[index][1] - (self.pos[1] - self.radius)
                self.total_energy = self.mass * (
                    0.5 * np.linalg.norm(self.velocity)**2 - GRAVITY * height
                )
                self.sliding = True
                
            # Correção de posição para evitar interseção
            normal = (self.pos - closest_point) / distance if distance > 0 else np.array([0, 1])
            overlap = self.radius - distance
            self.pos += normal * overlap

            # # Calcular o ângulo theta baseado no vetor tangente
            theta = np.arctan2(tangent_vector[1], tangent_vector[0])
            
            # Calcular componentes do ângulo
            sin_theta = np.sin(theta)
            cos_theta = np.cos(theta)

            # # Atualizar velocidade devido à gravidade e atrito
            tangent_unit = tangent_vector / np.linalg.norm(tangent_vector)
            self.velocity = np.dot(self.velocity, tangent_unit) * tangent_unit
            self.aceleration[1] = GRAVITY * (sin_theta**2) 
            self.aceleration[0] = GRAVITY * (sin_theta * cos_theta) 
            self.velocity += self.aceleration * dt
            self.velocity *= (1-FRICTION)

        elif distance - self.radius > 1:
            # Se não houver colisão, aplicar apenas a gravidade
            self.aceleration = np.array([0,GRAVITY])
            self.velocity += self.aceleration*dt

            # Atualizar posição da bola com base na velocidade
        self.pos += self.velocity * dt

        if self.sliding and (self.dragging or distance - self.radius > 1):
            # Sair do estado de deslizamento
            self.sliding = False

        if not self.dragging and self.start_time is not None:
            # Atualiza o tempo enquanto não está sendo arrastada
            self.elapsed_time += dt
    
    def draw_time(self, screen, width, height):
        # Desenhar o tempo
        font = pygame.font.Font(None, 36)
        time_text = font.render(f"Tempo: {self.elapsed_time:.1f}s", True, (0, 0, 0))
        screen.blit(time_text, (width, height))


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
                self.start_time = None  # Pausar o tempo ao arrastar

            # Verificar se o botão de reset foi clicado
            x1, y1, w, h = reset_button_area
            if x1 <= mouse_pos[0] <= x1 + w and y1 <= mouse_pos[1] <= y1 + h:
                self.reset()

        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
            self.start_time = pygame.time.get_ticks() / 1000.0  # Reinicia o tempo quando solta

        elif event.type == pygame.MOUSEMOTION and self.dragging:
            # Atualizar a posição da bola enquanto arrastada
            self.pos = mouse_pos
            self.velocity = np.zeros(2, dtype=np.float64)
            self.elapsed_time = 0
            self.start_time = None

    def draw_velocity(self, screen, pixels_per_meter, scale=0.25):
        """Desenha a velocidade da bola como uma seta na tela."""
        # Converter a velocidade para metros por segundo
        velocity_meters = self.velocity / pixels_per_meter

        # Calcular o ponto final da seta (escalado)
        arrow_end = self.pos + velocity_meters * pixels_per_meter * scale

        # Desenhar a seta representando a velocidade
        arrow_color = (255, 0, 0)  # Cor vermelha para a seta
        pygame.draw.line(screen, arrow_color, self.pos, arrow_end, 2)

        # Desenhar a ponta da seta (triângulo)
        direction = velocity_meters / np.linalg.norm(velocity_meters) if np.linalg.norm(velocity_meters) > 0 else np.array([1, 0])
        perpendicular = np.array([-direction[1], direction[0]])  # Vetor perpendicular à direção
        arrow_size = 10  # Tamanho da ponta da seta

        tip1 = arrow_end - direction * arrow_size + perpendicular * (arrow_size / 2)
        tip2 = arrow_end - direction * arrow_size - perpendicular * (arrow_size / 2)
        pygame.draw.polygon(screen, arrow_color, [arrow_end, tip1, tip2])

        # Desenhar o valor da velocidade em texto
        speed = np.linalg.norm(velocity_meters)  # Magnitude da velocidade em m/s
        font = pygame.font.Font(None, 24)
        velocity_text = font.render(f"Velocidade: {speed:.1f} m/s", True, (0, 0, 0))
        screen.blit(velocity_text, (self.pos[0] + 40, self.pos[1] - 20))




