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
    server = '192.168.0.104'#"127.0.1.1"
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
        self.card_buttons: list[Button] = []
        self.show_choises = 0
        self.move = -1
        
        for type in CardType:
            if type.value == 0:
                continue
            self.card_buttons.append(Button(width - 350,    Player.height + 20 + 76 * (type.value - 1), 300, 66))
            self.card_buttons[-1].set_texture(os.path.join("src", "textures", "buttons", type.name + ".png"))
            self.card_buttons[-1].set_hover(os.path.join("src", "textures", "buttons", type.name + "_hover.png"))

        self.card_buttons.append(Button(width - 350,    Player.height + 20 + 76 * 5, 300, 66))
        self.card_buttons[-1].set_texture(os.path.join("src", "textures", "buttons", "passive_income.png"))
        self.card_buttons[-1].set_hover(os.path.join("src", "textures", "buttons", "passive_income_hover.png"))
        self.card_buttons.append(Button(width - 350,    Player.height + 20 + 76 * 6, 300, 66))
        self.card_buttons[-1].set_texture(os.path.join("src", "textures", "buttons", "foreign_aid.png"))
        self.card_buttons[-1].set_hover(os.path.join("src", "textures", "buttons", "foreign_aid_hover.png"))
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

    def update_opponent(self):
        print(0)
        self.client.send("received".encode())
        print(1)
        message = self.get_packege()
        print(2)
        self.client.send("received".encode())
        print(3)
        message = message.split(" ")
        id = int(message[0])
        coins = int(message[1])
        card_count = int(message[2])
        cards: list[CardType] = []
        
        for i in range(card_count):
            cards.append(CardType[message[3 + i]])
        
        player: Player
        for player_ in self.players:
            if player_.id == id:
                player = player_
                break
        
        if player is None:
            return
        player.coins = coins
        player.set_cards(cards)

    def set_player(self):
        self.client.send("received".encode())
        message = self.get_packege()
        self.client.send("received".encode())
        message = message.split(" ")
        id = int(message[0])
        coins = int(message[1])
        card_count = int(message[2])
        cards: list[CardType] = []
        
        for i in range(card_count):
            cards.append(CardType[message[3 + i]])
        
        player: Player
        if self.this_player.id == id:
            player = self.this_player
            for card in CardType:
                if card.value == 0:
                    continue
                self.card_buttons[card.value - 1].set_texture(os.path.join("src", "textures", "buttons", card.name + ".png"))
            for card in cards:
                self.card_buttons[card.value - 1].set_texture(os.path.join("src", "textures", "buttons", card.name + "_select.png"))
        else:
            for player_ in self.players:
                if player_.id == id:
                    player = player_
                    break
        
        player.coins = coins
        player.set_cards(cards)

    def make_move(self, stop_event: threading.Event, screen: pygame.Surface):
        self.client.send("received".encode())
        self.show_choises = 1
        while not stop_event.is_set() and self.move == -1:
            pass
        if self.move == 6:
            self.client.send("passive_income".encode())
        elif self.move == 7:
            self.client.send("foreign_aid".encode())
        else:
            self.client.send(CardType(self.move).name.encode())
        self.move = -1
        self.show_choises = 0

    def handler(self, stop_event: threading.Event, screen: pygame.Surface):
        while not stop_event.is_set():
            message = self.client.recv(Coup.header).decode()
            print(f"[MESSAGE] {message}")
            match message:
                case "set_player":
                    threading.Thread(target=self.set_player).start()
                case "set_oponents":
                    threading.Thread(target=self.set_oponents).start()
                case "make_move":
                    threading.Thread(target=self.make_move, args=(stop_event, screen)).start()
                case "update_opponent":
                    threading.Thread(target=self.update_opponent).start()
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


    def draw(self, screen: pygame.Surface):
        screen.fill((255, 255, 255))
        res = self.this_player.draw(screen)
        if res != 0:
            self.add_to_discard(self.this_player.remove_card(res))

        for card in self.discard:
            card.draw(screen)

        for player in self.players:
            player.draw(screen)
        
        if self.show_choises == 1:
            index = 1
            for button in self.card_buttons:
                if button.draw(screen):
                    if index != 1:
                        self.move = index
                index += 1

        self.name.draw(screen)

        for event in pygame.event.get():
            # if confirm.draw(screen):
            #     pass
            if event.type == pygame.QUIT:
                self.running = False
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

    def start(self):
        icon = pygame.image.load(os.path.join('src', 'textures', 'icon.png'))
        pygame.display.set_icon(icon)
        pygame.display.set_caption("Coup")
        screen.fill((255, 255, 255))
        self.running = True

        stop_event = threading.Event()
        self.thread = threading.Thread(
            target=self.handler, args=(stop_event, screen))
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

        while self.running:
            self.draw(screen)

        pygame.quit()
        self.client.close()
        stop_event.set()


if __name__ == '__main__':
    coup = Coup()
    coup.start()
