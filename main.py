# Bibliotecas
import pygame
import pygame.locals

# Módulos
from config import *
from slider import Slider
from bezier_curve import BezierCurve
from ball import Ball

# Setup
PRECISAO = 2
STANDARD_GRAVITY = 9.80665
TIME_TO_FALL = 1.5
pixels_per_meter = HEIGHT / (0.5 * 9.81 * TIME_TO_FALL**2)


# Constantes
FPS = 60
GRAVITY =  9.8 * pixels_per_meter # Base da gravidade
FRICTION = 0                      # Valor inicial de atrito

# Setup PYGAME
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption('test caption')

# Objetos do jogo
ball = Ball(WIDTH // 2, HEIGHT // 4, radius=20, color=BLUE)
slider1 = Slider(2, HEIGHT - 60, WIDTH // 6, HEIGHT // 17, 10)  # Gravidade
slider2 = Slider(2, HEIGHT - 120, WIDTH // 6, HEIGHT // 17, 10)  # Atrito
control_points = [(WIDTH // 6, 200), (250, 550), (400, 100), (550, 550), (5 * WIDTH // 6, 200)]
curve = BezierCurve(points=control_points, color=GRAY, width=6)

# imagem_de_fundo = pygame.image.load(r"img\fundo.jpg")
# FUNDO = pygame.transform.scale(imagem_de_fundo, (WIDTH, HEIGHT))

# Main loop
running = True
while running:
    dt = clock.tick(FPS) * 0.001 
    for event in pygame.event.get():
        # Controle da saída do jogo
        if event.type == pygame.QUIT:
            running = False
        # Controle das interações do usuário
        ball.handle_event(event)
        slider1.handle_event(event)
        slider2.handle_event(event)
        curve.handle_event(event)

    # Atualizações
    slider1.update()
    slider2.update()
    gravity = slider1.get_percentage() * GRAVITY * 2
    # friction = slider2.get_percentage() * FRICTION * 0.095 / 200  # Ajustar como fração
    ball.update(curve, dt, gravity, FRICTION)

    # Desenho na tela
    screen.fill(WHITE)
    # screen.blit(FUNDO, (0, 0))
    curve.draw(screen)
    curve.draw_control_points(screen)

    # Botão de reset
    pygame.draw.rect(screen, GRAY, (10, 10, 100, 40), border_radius=5)
    font = pygame.font.Font(None, 36)
    text = font.render("Reset", True, WHITE)
    screen.blit(text, (60 - text.get_width() // 2, 30 - text.get_height() // 2))

    ball.draw(screen, dt)
    slider1.draw(screen, "Gravidade", 2)
    slider2.draw(screen, "Atrito")
    ball.draw_time(screen, WIDTH-151, 30)

    fps = clock.get_fps()
    fps_text = font.render(f"FPS: {int(fps)}", True, BLACK)
    screen.blit(fps_text, (WIDTH-151, 10))

    pygame.display.flip()
    # clock.tick(FPS)

pygame.quit()