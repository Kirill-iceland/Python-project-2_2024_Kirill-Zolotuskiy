import socket
import random
import pygame
import threading
import os
from time import sleep

pygame.init()
pygame.font.init()
width = 1500
height = 1000
screen = pygame.display.set_mode([1500, height])
from src.card.player import Player
from src.card.card_type import CardType
from src.card.card import Card
from src.ui.button import Button


class Server:
    port = 5050
    header = 64

    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverip = '192.168.0.105'# socket.gethostbyname(socket.gethostname())
        self.server.bind((self.serverip, Server.port))
        self.players: list[Player] = []
        self.deck: list[Card] = []
        self.connections: list[socket.socket] = []
        self.packeges = []

    def add_player(self, conn: socket.socket, addr: tuple[str, int]):
        id = random.randint(0, 2**32)
        while id in [player.id for player in self.players]:
            id = random.randint(0, 2**32)
        y = 10
        x = len(self.players) * (Player.width + 70) + 10
        if len(self.players) >= 3:
            y = Player.height + 20
            x = (len(self.players) - 3) * (Player.width + 70) + 10

        self.players.append(Player("Player " + str(len(self.players) + 1), [
                            CardType.back, CardType.back], id, x, y))
        conn.send(str(id).encode())
        self.connections.append(conn)

    def add_connection(self, stop_event: threading.Event):
        while not stop_event.is_set():
            conn, addr = self.server.accept()
            print(f"[CONNECTED] {addr} connected to the server")
            self.add_player(conn, addr)
            thread = threading.Thread(
                target=self.handler, args=(conn, stop_event))
            thread.daemon = True
            thread.start()
    
    def set_name(self, conn: socket.socket):
        conn.send("received".encode())
        name = self.get_packege(conn)
        index = self.connections.index(conn)
        player = self.players[index]
        player.name = name
        print(f"[SET_NAME] {player.name} - {player.id}")
        conn.send("received".encode())

    def handler(self, conn: socket.socket, stop_event: threading.Event):
        while not stop_event.is_set():
            message = conn.recv(Server.header).decode()
            print(f"[MESSAGE] {conn.getpeername()} - {message}")
            match message:
                case "set_name":
                    threading.Thread(target=self.set_name, args=(conn,)).start()
                case _:
                    self.packeges.append((conn, message))

    def get_packege(self, conn: socket.socket) -> str:
        while len(self.packeges) == 0 or self.packeges[-1][0] != conn:
            pass
        return self.packeges.pop()[1]

    
    def send_players(self):
        data = ""
        
        for player in self.players:
            data += str(player.id) + "+"
            data += player.name + "+"

        data = data[0:-1]

        for conn in self.connections:
            conn.send("set_oponents".encode())
            self.get_packege(conn)
            conn.send(data.encode())
            self.get_packege(conn)
            print(f"[SEND_PLAYERS] {conn.getpeername()}")

    def start(self):
        pygame.display.set_icon(pygame.image.load(os.path.join('src', 'textures', 'icon_server.png')))
        pygame.display.set_caption("Coup server")

        self.server.listen()
        print(f"[LISTENING] Server is listening on {self.serverip}")
        running = True

        stop_event = threading.Event()
        self.thread = threading.Thread(
            target=self.add_connection, args=(stop_event,))
        self.thread.daemon = True
        self.thread.start()

        cards_width = (3 * (Player.width + 70) + 10)
        button_x = (width - cards_width) // 2 - 300 // 2 + cards_width
        self.begin_button = Button(button_x, 50, 300, 66)
        self.begin_button.set_texture(os.path.join(Button.button_path, "start.png"))
        self.begin_button.set_hover(os.path.join(Button.button_path, "start_hover.png"))

        while running:
            screen.fill((255, 255, 255))

            index = 0
            for player in self.players:
                if player.draw(screen) != 0:
                    self.players.remove(player)
                    self.connections[index].close()
                    self.connections.pop(index)
                index += 1

            if self.begin_button.draw(screen):
                self.begin()

            for card in self.deck:
                card.draw(screen)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            pygame.display.flip()

        pygame.quit()
        stop_event.set()
        for conn in self.connections:
            conn.close()
        self.server.close()

    def update_player(self, player: Player, socket: socket.socket):
        socket.send("set_player".encode())
        self.get_packege(socket)
        data = ""
        data += str(player.id) + " "
        data += str(player.coins) + " "
        data += str(len(player.cards)) + " "
        data += " ".join([str(card.card_type.name) for card in player.cards])
        socket.send(data.encode())
        self.get_packege(socket)
        print(f"[SET_PLAYER] {player.name} - {player.id}")

    def begin(self):
        self.deck = []
        repeat = 3
        if len(self.players) <= 4:
            repeat = 2

        for type in CardType:
            if type == CardType.back:
                continue
            for i in range(repeat):
                self.deck.append(Card(type, 0, 0))

        random.shuffle(self.deck)

        self.send_players()

        index = 0
        for player in self.players:
            player.set_cards([self.deck.pop().card_type, self.deck.pop().card_type])
            self.update_player(player, self.connections[index])
            index += 1
            

        index = 0
        for card in self.deck:
            card.button.rect.x = index * (Card.width + 10) + 10
            card.button.rect.y = height - Card.height - 10
            index += 1


if __name__ == "__main__":
    server = Server()
    server.start()
