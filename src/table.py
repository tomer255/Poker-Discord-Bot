from src.deck import Deck
from src.game_logic import *
from src.player import Player
from src.card import Card
import time
import discord
import asyncio


class Table:
    def __init__(self):
        self.waiting_list = []
        self.players = []
        self.deck = Deck()
        self.board = []
        self.jackpot = {}
        # ------------
        self.running = False
        self.player_turn = None
        self.move = None
        self.message = "no message =("

    def get_move(self, player) -> str:
        for _ in range(180):
            if self.move is not None:
                if self.move.author == player.user:
                    return self.move.content
            time.sleep(1)
        self.message = f"time out for player {player.user}"
        return "fold"

    def init_game(self):
        # init
        for player in self.waiting_list:
            self.players.append(player)
        for player in self.players:
            if player.balance == 0 or player.exit:
                self.players.remove(player)
        if len(self.players) < 2:
            self.message = "There are not enough players to get started"
            return False
        self.waiting_list = []
        self.jackpot = {player.user: 0 for player in self.players}
        self.board = []
        self.distribute_cards()
        return True

    def game_rounds(self):
        self.bet_round()
        self.board = [self.deck.draw_card() for _ in range(3)]
        while len(self.board) < 5:
            print(f"{self.board} - jackpot: {self.jackpot}")
            self.bet_round()
            self.board.append(self.deck.draw_card())
        print(f"{self.board} - jackpot: {self.jackpot}")
        self.bet_round()

    def winners_check(self):
        not_folded = [player for player in self.players if player.state]
        find_bast_hands(not_folded, self.board)
        while not self.is_jackpot_empty():
            print(self.jackpot)
            winners = compare_hands(not_folded)
            num_of_winners = len(winners)
            for winner in winners:
                wins_money = 0
                min_jackpot = min([self.jackpot[player.user] for player in winner])
                for player in self.players:
                    if winner != player:
                        wins_money += min(self.jackpot[player.user], min_jackpot) / num_of_winners
                        self.jackpot[player.user] -= min(self.jackpot[player.user], min_jackpot) / num_of_winners
                wins_money += min_jackpot / num_of_winners
                print(f"player {winner.name} wins {wins_money}")
                winner.balance += wins_money
                self.jackpot[winner.user] -= min_jackpot / num_of_winners
                num_of_winners -= 1
            not_folded = [player for player in not_folded if self.jackpot[player.user] != 0]
        for player in self.players:
            player.throw_cards()

    def start_game(self):
        self.init_game()
        self.game_rounds()
        self.winners_check()

    def is_jackpot_empty(self):
        for vel in self.jackpot.values():
            if vel != 0:
                return False
        return True

    def bet_round(self):
        # init
        number_of_player = len(self.players)
        last_bet = number_of_player - 1
        i = 0
        bet_amount = 0
        for player in self.players:
            player.lest_bet = 0

        # bet loop
        while True:
            if sum([player.state for player in self.players]) < 2:
                break
            if self.players[i].state and (self.players[i].balance != 0):
                self.player_turn = self.players[i].name
                self.message = str(self) + self.players[i].name
                move = self.get_move(self.players[i])
                delta = bet_amount - self.players[i].lest_bet

                if "raise" in move:
                    val = move.split(sep=" ")[1]
                    val = int(val)
                    if val - self.players[i].lest_bet < self.players[i].balance and val > bet_amount * 2:
                        self.jackpot[self.players[i].ID] += val - self.players[i].lest_bet
                        self.players[i].balance -= val - self.players[i].lest_bet
                        bet_amount = val
                        last_bet = i - 1
                        last_bet = last_bet % number_of_player

                elif move == "call":
                    self.jackpot[self.players[i].ID] += min(delta, self.players[i].balance)
                    self.players[i].balance -= min(delta, self.players[i].balance)

                elif move == "check" and delta == 0:
                    pass
                elif move == "fold":
                    self.players[i].state = False
                else:  # No move
                    i -= 1

            if i == last_bet:
                break
            i = (i+1) % number_of_player

    def distribute_cards(self):
        for player in self.players:
            for _ in range(2):
                player.add_card(self.deck.draw_card())
            player.start_balance = player.balance

    def __repr__(self):
        return f"The board is : {self.board} \n" \
               f"The jackpot is : {self.jackpot}" \
               f"The player_turn {self.player_turn }"


    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~test~start~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def winner_test(self):
        self.players = [Player(0, "Adir"),
                        Player(0, "Tomer"),
                        Player(0, "Idan"),
                        Player(20, "Sefi")]
        self.board = [Card(2, "♣"),
                      Card(3, "♥"),
                      Card(5, "♦"),
                      Card(6, "♣"),
                      Card(7, "♠")]
        self.players[0].add_card(Card("A", "♥"))
        self.players[0].add_card(Card("A", "♣"))
        self.players[1].add_card(Card("K", "♥"))
        self.players[1].add_card(Card("K", "♣"))
        self.players[2].add_card(Card("Q", "♥"))
        self.players[2].add_card(Card("Q", "♣"))
        self.players[3].add_card(Card("A", "♥"))
        self.players[3].add_card(Card("A", "♣"))
        self.jackpot = {"Adir": 70, "Tomer": 80, "Idan": 100, "Sefi": 100}
        # winners
        # --------------------
        not_folded = [player for player in self.players if player.state]
        find_bast_hands(not_folded, self.board)
        while not self.is_jackpot_empty():
            print("jackpot : ", self.jackpot)
            winners = compare_hands(not_folded)
            num_of_winners = len(winners)
            for winner in winners:
                min_jackpot = min([self.jackpot[player.user] for player in winners])
                for player in self.players:
                    if winner != player:
                        winner.balance += min(self.jackpot[player.user], min_jackpot) / num_of_winners
                        self.jackpot[player.user] -= min(self.jackpot[player.user], min_jackpot) / num_of_winners
                winner.balance += min_jackpot / num_of_winners
                self.jackpot[winner.user] -= min_jackpot / num_of_winners
                num_of_winners -= 1
            not_folded = [player for player in not_folded if self.jackpot[player.user] != 0]
        for player in self.players:
            print(f"{player.user} : {player.balance}")

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~test~end~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
