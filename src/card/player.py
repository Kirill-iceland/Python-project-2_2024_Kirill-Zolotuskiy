import os

import pygame

from src.card.card import Card
from src.card.card_type import CardType
from src.ui.texture import Texture


class Player:
    width = Card.width * 2 + 50
    font_size = 26
    height = Card.height + font_size + 10
    coin: Texture

    def init():
        Player.coin = Texture(os.path.join("src", "textures", "coin.png"), Player.font_size * 1.5, Player.font_size)
        Card.init()

    def __init__(self, name: str, cards: list[CardType], id: int, x: int, y: int):
        self.name = name
        self.x = x
        self.y = y
        self.set_cards(cards)
        self.coins = 2
        self.id = id
        self.my_font = pygame.font.Font(os.path.join("src", "fonts", "arial", "ARIAL.TTF"), Player.font_size)
        self.my_font.bold = True

    def set_cards(self, cards: list[CardType]):
        match len(cards):
            case 1:
                self.cards = [Card(cards[0], self.x + (Player.width // 2) -
                                   ((Card.width) // 2), self.y + Player.font_size + 10)]
            case 2:
                self.cards = [Card(cards[0], self.x, self.y + Player.font_size + 10), Card(
                    cards[1], self.x + Card.width + 50, self.y + Player.font_size + 10)]
            case 0:
                self.cards = []

    def remove_card(self, index: int) -> Card:
        card = self.cards.pop(index - 1)
        self.set_cards([card.card_type for card in self.cards])
        return card

    def draw(self, screen: pygame.Surface) -> int:
        text = self.my_font.render(self.name + " - " + str(self.coins) + " ", True, (0, 0, 0))
        old_width = text.get_width()
        text1 = pygame.Surface((old_width + (Player.font_size * 1.5), text.get_height()))
        text1.fill((255, 255, 255))
        text1.blit(text, (0, 0))
        text1.blit(Player.coin.texture, (old_width, 0))
        screen.blit(text1, (self.x + (Player.width // 2) - (text1.get_width() // 2), self.y))

        ans = 0
        self.cards.reverse()

        for card in self.cards:
            ans *= 2
            if card.draw(screen):
                ans += 1

        self.cards.reverse()
        return ans
