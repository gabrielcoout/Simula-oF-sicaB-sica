import pygame
from config import *
from slider import Slider
from bezier_curve import BezierCurve
from ball import Ball

# Constantes
FPS = 60
METERS_TO_PIXELS = 100
BASE_GRAVITY = 9.8 * METERS_TO_PIXELS / 60  # Gravidade base
FRICTION = 0.98  # Coeficiente de atrito

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Objetos do jogo
ball = Ball(WIDTH // 2, HEIGHT // 2, radius=20, color=BLUE)  # Bola principal
slider1 = Slider(2, HEIGHT - 60, WIDTH // 6, HEIGHT // 17, 10)  # Controle de gravidade
slider2 = Slider(2, HEIGHT - 120, WIDTH // 6, HEIGHT // 17, 10, 0)  # Controle de atrito
control_points = [(WIDTH // 6, 200), (250, 550), (400, 100), (550, 550), (5 * WIDTH // 6, 200)]  # Pontos de controle para a curva de Bézier
curve = BezierCurve(points=control_points, color=GRAY, width=7)  # Curva de Bézier

running = True
while running:
    dt = 1 / FPS  # Intervalo de tempo entre quadros
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # Verifica se o jogador deseja sair
            running = False
        ball.handle_event(event)  # Processa eventos relacionados à bola
        slider1.handle_event(event)  # Processa eventos relacionados ao controle de gravidade
        slider2.handle_event(event)  # Processa eventos relacionados ao controle de atrito
        curve.handle_event(event)  # Processa eventos relacionados à curva

    # Atualizações dos controles
    slider1.update()  # Atualiza o controle de gravidade
    slider2.update()  # Atualiza o controle de atrito
 
    gravity = slider1.get_percentage() * BASE_GRAVITY  # Calcula a gravidade baseada no slider
    friction = slider2.get_percentage() / 200  # Calcula o atrito baseado no slider

    ball.update(curve, dt, gravity, friction)  # Atualiza a posição e estado da bola

    # Desenho na tela
    screen.fill(WHITE)  # Preenche o fundo com cor branca
    curve.draw(screen)  # Desenha a curva de Bézier
    curve.draw_control_points(screen)  # Desenha os pontos de controle da curva

    # Botão de reset
    pygame.draw.rect(screen, GRAY, (10, 10, 100, 40), border_radius=5)  # Desenha o botão de reset
    font = pygame.font.Font(None, 36)
    text = font.render("Reset", True, WHITE)  # Texto do botão
    screen.blit(text, (60 - text.get_width() // 2, 30 - text.get_height() // 2))  # Centraliza o texto no botão

    slider1.draw(screen, "Gravidade")  # Desenha o controle de gravidade
    slider2.draw(screen, "Atrito")  # Desenha o controle de atrito
    ball.draw(screen, dt)  # Desenha a bola

    pygame.display.flip()  # Atualiza a tela
    clock.tick(FPS)  # Controla a taxa de quadros por segundo

pygame.quit()  # Encerra o jogo