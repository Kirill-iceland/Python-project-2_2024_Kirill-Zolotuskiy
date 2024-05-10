import pygame
import socket
import os
import threading
from time import sleep

pygame.init()
pygame.font.init()
width = 1500
height = 1000
screen = pygame.display.set_mode([1500, height])

from src.ui.button import Button
from src.card.card import Card
from src.card.card_type import CardType
from src.card.player import Player
from src.ui.text_box import TextBox


class Coup:
    server = '192.168.0.105'#"127.0.1.1"
    port = 5050
    address = (server, port)
    header = 64

    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(Coup.address)
        self.id = int(self.client.recv(Coup.header).decode())
        self.this_player: Player
        self.players: list[Player] = []
        self.discard: list[Card] = []
        self.packeges = []
        print(self.id)

    def add_to_discard(self, card: Card):
        card.button.rect.x = len(self.discard) * (Card.width + 10) + 10
        self.discard.append(card)

    def set_oponents(self):
        self.client.send("received".encode())
        message = self.get_packege()
        self.client.send("received".encode())
        message = message.split("+")
        length = len(message)
        index = 0
        self.players = []
        for i in range(length // 2):
            id = int(message[i * 2])
            name = message[i * 2 + 1]
            if id == self.id:
                continue
            y = 10
            x = index * (Player.width + 70) + 10
            self.players.append(Player(name, [CardType.back, CardType.back], id, x, y))
            index += 1

    def set_player(self):
        self.client.send("received".encode())
        message = self.get_packege()
        self.client.send("received".encode())
        message = message.split(" ")
        id = int(message[0])
        coins = int(message[1])
        card_count = int(message[2])
        cards = []
        
        for i in range(card_count):
            cards.append(CardType[message[3 + i]])
        
        player: Player
        if self.this_player.id == id:
            player = self.this_player
        else:
            for player_ in self.players:
                if player_.id == id:
                    player = player_
                    break
        
        player.coins = coins
        player.set_cards(cards)

    def handler(self, stop_event: threading.Event):
        while not stop_event.is_set():
            message = self.client.recv(Coup.header).decode()
            print(f"[MESSAGE] {message}")
            match message:
                case "set_player":
                    threading.Thread(target=self.set_player).start()
                case "set_oponents":
                    threading.Thread(target=self.set_oponents).start()
                case _:
                    self.packeges.append(message)

    def get_packege(self) -> str:
        while len(self.packeges) == 0:
            pass
        return self.packeges.pop()
    
    def send_name(self):
        self.client.send("set_name".encode())
        self.get_packege()
        print(self.this_player.name)
        self.client.send(self.this_player.name.encode())
        print(self.this_player.name)
        self.get_packege()


    def start(self):
        icon = pygame.image.load(os.path.join('src', 'textures', 'icon.png'))
        pygame.display.set_icon(icon)
        pygame.display.set_caption("Coup")
        screen.fill((255, 255, 255))
        running = True

        stop_event = threading.Event()
        self.thread = threading.Thread(
            target=self.handler, args=(stop_event,))
        self.thread.daemon = True
        self.thread.start()

        # confirm = Button(100, 100, 300, 66)
        # confirm.set_texture(os.path.join(Coup.button_path, "confirm.png"))
        # confirm.set_hover(os.path.join(Coup.button_path, "confirm_hover.png"))

        # card1 = Card(CardType.back, 200, 300)
        self.this_player = Player("Player 1", [CardType.ambassador, CardType.back],
                                  self.id, width // 2 - (Player.width // 2), height - Player.height - 20)
        
        self.name = TextBox(width - 250, height - Player.height - 20, 200, 50)
        self.name.set_color((255, 255, 255))
        self.name.set_background((156, 170, 189), (108, 117, 125))

        while running:
            screen.fill((255, 255, 255))
            res = self.this_player.draw(screen)
            if res != 0:
                self.add_to_discard(self.this_player.remove_card(res))

            for card in self.discard:
                card.draw(screen)

            for player in self.players:
                player.draw(screen)

            self.name.draw(screen)

            for event in pygame.event.get():
                # if confirm.draw(screen):
                #     pass
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and self.name.selected:
                    if event.key == pygame.K_BACKSPACE:
                        self.name.text = self.name.text[:-1]
                    elif event.key == pygame.K_RETURN:
                        self.name.selected = False
                        self.this_player.name = self.name.text
                        self.name.text = ""
                        self.send_name()
                    else:
                        self.name.text += event.unicode

            pygame.display.flip()
        pygame.quit()
        self.client.close()
        stop_event.set()


if __name__ == '__main__':
    coup = Coup()
    coup.start()
