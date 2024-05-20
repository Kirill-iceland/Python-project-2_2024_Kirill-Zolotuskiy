import socket
import random
import threading
import os

import pygame

from src.card.player import Player
from src.card.card_type import CardType
from src.card.card import Card
from src.ui.button import Button
from config import Config


class Server:
    port = Config.port
    header = Config.header

    width = Config.width
    height = Config.height 
    screen: pygame.Surface

    def init():
        pygame.init()
        pygame.font.init()

        Server.screen = pygame.display.set_mode([1500, Server.height])

        Card.init()
        Player.init()

    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverip = Config.ip
        self.server.bind((self.serverip, Server.port))
        self.players: list[Player] = []
        self.deck: list[Card] = []
        self.connections: list[socket.socket] = []
        self.packeges = []
        self.player_to_start = 0
        self.alive: list[bool] = []
        self.count_alive = 0
        self.card_lost: list[list[CardType]] = []
        self.conformations_left = 0

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
        self.card_lost.append([])

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
            self.get_packege(conn)
            data = ""
            data += str(self.players[index].id) + " "
            data += str(self.players[index].coins) + " "
            data += str(2) + " "
            for card in self.players[index].cards:
                data += str(CardType.back.name) + " "
            for card in self.card_lost[index]:
                data += str(card.name) + " "
            conn.send(data.encode())
            self.get_packege(conn)
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
        button_x = (Server.width - cards_width) // 2 - 300 // 2 + cards_width
        self.begin_button = Button(button_x, 50, 300, 66)
        self.begin_button.set_texture(os.path.join(Button.button_path, "start.png"))
        self.begin_button.set_hover(os.path.join(Button.button_path, "start_hover.png"))

        while running:
            Server.screen.fill((255, 255, 255))

            index = 0
            for player in self.players:
                if player.draw(Server.screen) != 0:
                    self.players.remove(player)
                    self.connections[index].close()
                    self.connections.pop(index)
                    self.card_lost.pop(index)
                index += 1

            if self.begin_button.draw(Server.screen):
                self.begin()

            for card in self.deck:
                card.draw(Server.screen)

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

    def confirm_handler(self, conn: socket.socket):
        data = self.get_packege(conn)
        conn.send("received".encode())
        if data != "confirm" and self.conformation != "challenge":
            self.conformation = data
            self.conformation_player = self.connections.index(conn)
        self.conformations_left -= 1

    def lose_card(self, player: int):
        conn = self.connections[player]
        conn.send("lose_card".encode())
        card = int(self.get_packege(conn))
        conn.send("received".encode())
        print(f"[LOSE_CARD] {self.players[player].name} - {self.players[player].id} - {self.players[player].cards[card - 1].card_type.name}")
        self.card_lost[player].append(self.players[player].cards[card - 1].card_type)
        self.players[player].remove_card(card)
        if len(self.players[player].cards) == 0:
            self.alive[player] = False
            self.count_alive -= 1
        self.update_opponent(player)

    def challenge(self, challenger: int, player: int, card: CardType):
        for card_ in self.players[player].cards:
            if card_.card_type == card:
                self.lose_card(challenger)
                player_card = card_
                
                player_card.card_type, self.deck[-1].card_type = self.deck[-1].card_type, player_card.card_type
                player_card.button.texture, self.deck[-1].button.texture = self.deck[-1].button.texture, player_card.button.texture
                random.shuffle(self.deck)
                self.update_player(self.players[player], self.connections[player])
                return True
        
        self.lose_card(player)
        return False

    def confirm(self, player: int, confirm_type: str, card: CardType = CardType.back):
        self.conformations_left = len(self.players) - 1
        self.conformation = "confirm"
        index = 0

        for conn in self.connections:
            if index == player:
                index += 1
                continue
            conn.send("confirm".encode())
            self.get_packege(conn)
            conn.send(confirm_type.encode())
            self.get_packege(conn)
            threading.Thread(target=self.confirm_handler, args=(conn,)).start()
            index += 1
            print(f"[CONFIRM] {self.players[player].name} - {self.players[player].id}")
        
        while self.conformations_left > 0:
            pass
        
        match self.conformation:
            case "confirm":
                print(f"[CONFIRMED] {self.players[player].name} - {self.players[player].id}")
                return True
            
            case "block":
                print(f"[BLOCKED] {self.players[player].name} - {self.players[player].id} by {self.players[self.conformation_player].name} - {self.players[self.conformation_player].id}")
                card =  self.get_packege(self.connections[self.conformation_player])
                print(f"[BLOCK_CARD] {card}")
                card = CardType[card]
                self.connections[self.conformation_player].send("received".encode())
                return not self.confirm(self.conformation_player, "block", card)
            
            case "challenge":
                print(f"[CHALLENGED] {self.players[player].name} - {self.players[player].id} by {self.players[self.conformation_player].name} - {self.players[self.conformation_player].id}")
                return not self.challenge(self.conformation_player, player, card)


    def move_handler(self, conn: socket.socket, data: str):
        match data:
            case "contessa":
                # No action
                pass
            case "duke":
                if self.confirm(self.player_to_start, "duke", CardType.duke):
                    return
                self.players[self.player_to_start].coins += 3
                self.update_player(self.players[self.player_to_start], conn)
                self.update_opponent(self.player_to_start)

            case "captain":
                # Will be implemented later
                pass

            case "assassin":
                pass

            case "ambassador":
                # Will be implemented later
                pass

            case "passive_income":
                self.players[self.player_to_start].coins += 1
                self.update_player(self.players[self.player_to_start], conn)
                self.update_opponent(self.player_to_start)

            case "foreign_aid":
                if self.confirm(self.player_to_start, "foreign_aid"):
                    print(33333333)
                    return
                print(self.player_to_start)
                self.players[self.player_to_start].coins += 2
                self.update_player(self.players[self.player_to_start], conn)
                self.update_opponent(self.player_to_start)
            
            case "coup":
                pass
                # Will be implemented later

    def make_move(self, stop_event: threading.Event):
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
            card.button.rect.y = Server.height - Card.height - 10
            index += 1

        stop_event = threading.Event()
        self.move_thread = threading.Thread(
            target=self.make_move, args=(stop_event,))
        self.move_thread.daemon = True
        self.move_thread.start()
        


if __name__ == "__main__":
    Server.init()
    server = Server()
    server.start()
