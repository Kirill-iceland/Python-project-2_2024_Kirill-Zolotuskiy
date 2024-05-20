import os

import pygame

from src.card.card_type import CardType
from src.ui.texture import Texture
from src.ui.button import Button


class Card:
    height = 175
    width = 100

    card_path = os.path.join("src", "textures", "cards")

    card_textures: list[Texture] = []

    def init():
        Card.card_textures = [
            Texture(os.path.join(Card.card_path, "back.png"), Card.width, Card.height),
            Texture(os.path.join(Card.card_path, "contessa.png"), Card.width, Card.height),
            Texture(os.path.join(Card.card_path, "captain.png"), Card.width, Card.height),
            Texture(os.path.join(Card.card_path, "duke.png"), Card.width, Card.height),
            Texture(os.path.join(Card.card_path, "assassin.png"), Card.width, Card.height),
            Texture(os.path.join(Card.card_path, "ambassador.png"),Card. width,Card. height)
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
