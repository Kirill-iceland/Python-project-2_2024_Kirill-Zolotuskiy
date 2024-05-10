import pygame
import os


class TextBox:
    font_size = 26

    def __init__(self, pos_x: int, pos_y: int, size_x: int, size_y: int):
        self.rect = pygame.rect.Rect(pos_x, pos_y, size_x, size_y)
        self.clicked = False
        self.my_font = pygame.font.Font(os.path.join("src", "fonts", "arial", "ARIAL.TTF"), TextBox.font_size)
        self.my_font.bold = True
        self.text = ""
        self.selected = False
    
    def set_background(self, color: tuple[int, int, int], hover: tuple[int, int, int]):
        self.background = color
        self.hover = hover

    def set_color(self, color: tuple[int, int, int]):
        self.color = color

    def draw(self, screen: pygame.Surface) -> str:
        action = False
        pos = pygame.mouse.get_pos()
        
        if self.rect.collidepoint(pos):
            pygame.draw.rect(screen, self.hover, self.rect)

            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                self.selected = not self.selected
                action = True
        else:
            if self.selected:
                pygame.draw.rect(screen, self.hover, self.rect)
            else:
                pygame.draw.rect(screen, self.background, self.rect)

        text = self.my_font.render(self.text, True, self.color)
        screen.blit(text, (self.rect.center[0] - (text.get_size()[
                    0] / 2), self.rect.center[1] - (text.get_size()[1] / 2)))

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        return action