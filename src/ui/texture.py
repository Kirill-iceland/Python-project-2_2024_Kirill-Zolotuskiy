import pygame
# 444444
# 9caabd

# 6c757d

class Texture:
    def __init__(self, path, width, height):
        self.path = path
        self.texture = pygame.image.load(path).convert_alpha()
        self.texture = pygame.transform.scale(self.texture, (width, height))
        self.width = self.texture.get_width()
        self.height = self.texture.get_height()

    def draw(self, screen: pygame.Surface, x, y):
        screen.blit(self.texture, (x, y))

    def draw_centered(self, screen: pygame.Surface, x, y):
        screen.blit(self.texture, (x - self.width // 2, y - self.height // 2))

    def copy(self) -> 'Texture':
        return Texture(self.path, self.width, self.height)
        