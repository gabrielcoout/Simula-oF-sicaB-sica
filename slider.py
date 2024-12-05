import pygame
from pygame.locals import *

class Slider:
    def __init__(self, x:int, y:int, container_width:int, container_height:int, slider_width:int, percentage=50, slider_color=(255, 0, 0), container_color=(0, 0, 0)):
        # Inicializa os atributos do slider e do contêiner
        self.container_x = x
        self.container_y = y
        self.container_width = container_width
        self.container_height = container_height
        self.slider_width = slider_width
        self.slider_height = container_height - 1
        self.slider_color = slider_color
        self.container_color = container_color
        self.dragging = False
        # Define a porcentagem inicial
        self.percentage = percentage

        # Calcula a posição inicial do slider com base na porcentagem
        self.slider_x = x + int((percentage / 100) * (container_width - slider_width))
        self.slider_y = y + (container_height - self.slider_height) // 2

    def handle_event(self, event:pygame.event.Event):
        """Lida com eventos de interação do usuário."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Verifica se o mouse está sobre o slider
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if self.slider_x <= mouse_x <= self.slider_x + self.slider_width and \
                    self.slider_y <= mouse_y <= self.slider_y + self.slider_height:
                self.dragging = True

        elif event.type == pygame.MOUSEBUTTONUP:
            # Para o movimento ao soltar o botão do mouse
            self.dragging = False

    def update(self):
        """Atualiza a posição do slider enquanto ele é arrastado."""
        if self.dragging:
            # Obtém a posição do mouse
            mouse_x, _ = pygame.mouse.get_pos()
            self.slider_x = mouse_x - self.slider_width // 2
            # Garante que o slider fique dentro do contêiner
            self.slider_x = max(self.container_x, 
                                min(self.slider_x, self.container_x + self.container_width - self.slider_width))
            # Atualiza a porcentagem com base na posição
            self.percentage = ((self.slider_x - self.container_x) / (self.container_width - self.slider_width)) * 100

    def draw(self, surface:pygame.surface.Surface, text:str, k=1, font=None, text_color=(0, 0, 0)):
        """Desenha o slider e o contêiner na tela."""
        # Desenha o contêiner
        pygame.draw.rect(surface, self.container_color,
                         pygame.Rect(self.container_x, self.container_y, self.container_width, self.container_height))
        
        # Desenha o slider
        pygame.draw.rect(surface, self.slider_color,
                         pygame.Rect(self.slider_x, self.slider_y, self.slider_width, self.slider_height))
        
        # Configura a fonte para o texto
        if font is None:
            font = pygame.font.Font(None, 24)  # Fonte padrão, tamanho 24
        
        # Renderiza o texto
        text_surface = font.render(text, True, text_color)
        
        # Posiciona o texto centralizado acima do slider
        text_rect = text_surface.get_rect()
        text_rect.center = (self.container_x + self.container_width // 2, self.slider_y - text_rect.height // 2 - 5)
        
        # Adiciona o texto à superfície
        surface.blit(text_surface, text_rect)

        # Renderiza a porcentagem dentro do contêiner
        percentage_text = font.render(f"{2*self.percentage:.0f}%", True, (255, 255, 255))
        
        # Posiciona o texto centralizado no contêiner
        text_rect = percentage_text.get_rect()
        text_rect.center = (self.container_x + self.container_width // 2, 
                            self.container_y + self.container_height // 2)
        
        # Adiciona o texto à superfície
        surface.blit(percentage_text, text_rect)

    def get_percentage(self):
        """Retorna a porcentagem atual do slider."""
        return self.percentage/100