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
        self.serverip = '192.168.0.104'# socket.gethostbyname(socket.gethostname())
        self.server.bind((self.serverip, Server.port))
        self.players: list[Player] = []
        self.deck: list[Card] = []
        self.connections: list[socket.socket] = []
        self.packeges = []
        self.player_to_start = 0
        self.alive: list[bool] = []
        self.count_alive = 0
        self.card_lost: list[int] = []

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
        self.alive.append(False)
        self.count_alive += 1
        self.card_lost.append(0)

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
    
    def update_opponent(self, index: int):
        for conn in self.connections:
            conn.send("update_opponent".encode())
            print(1)
            self.get_packege(conn)
            print(2)
            data = ""
            data += str(self.players[index].id) + " "
            data += str(self.players[index].coins) + " "
            data += str(len(self.players[index].cards)) + " "
            mask = 1
            for card in self.players[index].cards:
                if self.card_lost[index] & 1 == 0:
                    data += "back "
                    mask *= 2
                else:
                    data += str(card.card_type.name) + " "
            conn.send(data.encode())
            print(3)
            self.get_packege(conn)
            print(4)
            print(f"[UPDATE_OPPONENT] {self.players[index].name} - {self.players[index].id}")

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
                    self.card_lost.pop(index)
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

    def move_handler(self, conn: socket.socket, data: str):
        match data:
            case "contessa":
                pass
            case "duke":
                pass
            case "captain":
                pass
            case "assassin":
                pass
            case "ambassador":
                pass
            case "passive_income":
                self.players[self.player_to_start].coins += 1
                self.update_player(self.players[self.player_to_start], conn)
                self.update_opponent(self.player_to_start)
            case "foreign_aid":
                pass


    def make_move(self,  stop_event: threading.Event):
        if self.count_alive <= 1:
            return
        
        conn = self.connections[self.player_to_start]
        conn.send("make_move".encode())
        print(f"[MAKE_MOVE] {self.players[self.player_to_start].name} - {self.players[self.player_to_start].id}")
        self.get_packege(conn)
        data = self.get_packege(conn)
        self.move_handler(conn, data)

        self.player_to_start += 1
        self.player_to_start %= len(self.players)
        
        while not self.alive[self.player_to_start]:
            self.player_to_start += 1
            self.player_to_start %= len(self.players)
        
        self.make_move(stop_event)

    def begin(self):
        for i in range(0, len(self.players)):
            self.alive[i] = True

        if len(self.players) > 0:
            self.player_to_start = random.randint(0, len(self.players) - 1)
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

        stop_event = threading.Event()
        self.move_thread = threading.Thread(
            target=self.make_move, args=(stop_event,))
        self.move_thread.daemon = True
        self.move_thread.start()
        


if __name__ == "__main__":
    server = Server()
    server.start()
