import pygame 
from pygame.locals import *

# Configurações da janela
WIDTH, HEIGHT = 800, 600

# Definição de cores
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GRAY = (200, 200, 200)
RED = (255, 0, 0)
BLACK = (0, 0, 0)


# Função para exibir texto na tela (útil para debug)
def print_text(surface, text, x, y, font_name="Arial", font_size=24, color=(0, 0, 0), center=False):
    """
    Exibe texto na superfície fornecida.
    
    :param surface: Superfície onde o texto será renderizado.
    :param text: Texto a ser exibido.
    :param x: Coordenada x do texto.
    :param y: Coordenada y do texto.
    :param font_name: Nome da fonte a ser usada (padrão é "Arial").
    :param font_size: Tamanho da fonte.
    :param color: Cor do texto em formato RGB.
    :param center: Booleano para centralizar o texto nas coordenadas fornecidas.
    """
    # Cria uma fonte
    font = pygame.font.SysFont(font_name, font_size)
    
    # Renderiza o texto em uma superfície
    text_surface = font.render(text, True, color)
    
    # Obtém o retângulo do texto
    text_rect = text_surface.get_rect()
    
    # Centraliza o texto se necessário
    if center:
        text_rect.center = (x, y)
    else:
        text_rect.topleft = (x, y)
    
    # Renderiza o texto na superfície principal
    surface.blit(text_surface, text_rect)
