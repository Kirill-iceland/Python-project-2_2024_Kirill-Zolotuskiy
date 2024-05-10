import pygame
import os

from src.card.card_type import CardType
from src.ui.texture import Texture
from src.ui.button import Button


class Card:
    height = 175
    width = 100

    card_path = os.path.join("src", "textures", "cards")

    card_textures = [
        Texture(os.path.join(card_path, "back.png"), width, height),
        Texture(os.path.join(card_path, "contessa.png"), width, height),
        Texture(os.path.join(card_path, "captain.png"), width, height),
        Texture(os.path.join(card_path, "duke.png"), width, height),
        Texture(os.path.join(card_path, "assassin.png"), width, height),
        Texture(os.path.join(card_path, "ambassador.png"), width, height)
    ]

    def __init__(self, card_type: CardType, x: int, y: int):
        self.card_type = card_type
        self.x = x
        self.y = y
        self.button = Button(x, y, self.width, self.height)
        self.button.set_texture(Card.card_textures[card_type.value].path)
        self.button.set_auto_hover()

    def draw(self, screen: pygame.Surface) -> bool:
        return self.button.draw(screen)
