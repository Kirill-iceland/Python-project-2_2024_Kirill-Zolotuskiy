import pygame
import os

from src.ui.texture import Texture

class Button:
    button_path = os.path.join("src", "textures", "buttons")

    def __init__(self, pos_x: int, pos_y: int, size_x: int, size_y: int):
        self.rect = pygame.rect.Rect(pos_x, pos_y, size_x, size_y)
        self.clicked = True

    def set_texture(self, path: str):
        self.texture = Texture(path, self.rect.width, self.rect.height)

    def set_hover(self, path: str):
        self.hover = Texture(path, self.rect.width, self.rect.height)

    def set_auto_hover(self):
        self.hover = self.texture.copy()
        brighten = 25
        self.hover.texture.fill((brighten, brighten, brighten), special_flags=pygame.BLEND_RGB_ADD)


    def draw(self, screen: pygame.Surface) -> bool:
        action = False
        pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(pos):
            self.hover.draw(screen, self.rect.x, self.rect.y)
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                action = True
        else:
            self.texture.draw(screen, self.rect.x, self.rect.y)

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        return action
