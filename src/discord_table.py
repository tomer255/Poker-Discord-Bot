from src.deck import Deck
from src.game_logic import *
from src.player import Player
import json
import os
import discord
from dotenv import load_dotenv
load_dotenv()


class Discord_Table:
    def __init__(self):
        self.waiting_list = []
        self.players = []
        self.deck = None
        self.board = []
        self.jackpot = {}
        self.number_of_player = 0
        self.last_bet = 0
        self.running = False
        self.player_turn = None
        self.bet_amount = 0
        self.dict_of_players_balance = {}
        self.min_amount = 10
        self.commands = {
            "$balance": self.on_get_balance,
            "$join": self.on_join,
            "$start": self.on_start,
            "$exit": self.on_exit,
            "$give": self.on_give,
        }
        self.game_commands = {
            "call": self.on_call,
            "raise": self.on_raise,
            "check": self.on_check,
            "fold": self.on_fold,
        }

    async def handel_message(self, message):
        if isinstance(message.channel, discord.channel.DMChannel):
            # await message.author.send("Please do not send messages directly to the bot")
            return
        if message.channel.name not in os.getenv('WHITELIST').split(","):
            return
        command = message.content.split(sep=" ")[0].lower()
        if command in self.commands:
            await self.commands[command](message)
        if not self.running:
            return
        if command in self.game_commands:
            await self.game_commands[command](message)

    def give_all(self, amount):
        self.load_players_balance()
        for player_id in self.dict_of_players_balance:
            self.dict_of_players_balance[player_id] += amount
        self.save_players_balance()

    async def on_get_balance(self, message):
        player = next((player for player in self.players if message.author.id == player.ID), None)
        if player is not None:
            await message.author.send(f"balance : {player.balance}")
            return
        await message.author.send(self.dict_of_players_balance.get(message.author.id, "not fond"))
        return

    async def on_start(self, message):
        await self.init_game(message)

    async def on_give(self, message):
        command, player, amount = message.content.split(sep=" ")
        player_id = int(player.strip("<@>"))
        if amount.isnumeric():
            amount = float(amount)
        else:
            await message.channel.send("you must give player amount of money")
            return False
        if message.author.id in self.dict_of_players_balance and player_id in self.dict_of_players_balance:
            if self.dict_of_players_balance[message.author.id] < amount:
                await message.channel.send("you don't have enough money")
                return False
            self.dict_of_players_balance[message.author.id] -= amount
            self.dict_of_players_balance[player_id] += amount
            await message.channel.send(f"<@{message.author.id}> transferred {amount} to <@{player_id}>")
            self.save_players_balance()
            return True
        else:
            await message.channel.send("player was not found")
        return False

    def save_players_balance(self):
        for player in self.players:
            self.dict_of_players_balance[player.user.id] = player.balance
        with open('players.txt', 'w') as outfile:
            json.dump(self.dict_of_players_balance, outfile, indent=2)
        print(f"save : {self.dict_of_players_balance}")
        print('players saved')

    def load_players_balance(self):
        if os.path.exists('players.txt'):
            with open('players.txt') as json_file:
                json_data = json.load(json_file)
            self.dict_of_players_balance = {int(p): json_data[p] for p in json_data}
            print(f"Lode : {self.dict_of_players_balance}")
        else:
            print('"players.txt" Not found')
            self.dict_of_players_balance = {}

    async def on_join(self, message):
        balance = self.dict_of_players_balance.get(message.author.id, 3000)
        player = Player(balance, message.author)
        if player in self.waiting_list:
            await message.channel.send(f"<@{player.ID}> is already in the waiting list")
            return
        if player in self.players:
            await message.channel.send(f"<@{player.ID}> is already in table")
            return
        self.waiting_list.append(player)
        await message.channel.send(f"<@{player.ID}> join the waiting list")

    async def init_game(self, message):
        if self.running:
            await message.channel.send("game already running")
            return False
        for player in self.waiting_list:
            self.players.append(player)
        for player in self.players:
            if player.balance == 0 or player.exit:
                self.players.remove(player)
                await message.channel.send(f"<@{player.ID}> removed from the game")
            else:
                player.state = True
        if len(self.players) < 2:
            await message.channel.send("There are not enough players to get started")
            return False

        self.number_of_player = len(self.players)
        self.waiting_list = []
        self.jackpot = {player.ID: 0 for player in self.players}

        for player in self.players:
            self.jackpot[player.ID] += min(self.min_amount, player.balance)
            player.balance -= min(self.min_amount, player.balance)

        self.board = []
        self.running = True
        self.player_turn = 0
        await message.channel.send(f"""game start =) 
        is {self.players[0].name} turn to play""")
        self.bet_init()
        self.deck = Deck()
        await self.distribute_cards()
        return True

    async def on_exit(self, message):
        player = next((player for player in self.players if message.author.id == player.ID), None)
        if player is not None:
            player.exit = True
            player.state = False
            await message.channel.send(f"<@{player.ID}> exit the game")
            return

        player = next((player for player in self.waiting_list if message.author.id == player.ID), None)
        if player is not None:
            player.exit = True
            player.state = False
            await message.channel.send(f"<@{player.ID}> exit the waiting list")
            return

        await message.channel.send(f"{message.author.name} was not found")
        return

    def bet_init(self):
        for player in self.players:
            player.lest_bet = 0
        self.player_turn = 0
        self.last_bet = self.number_of_player - 1
        self.bet_amount = 0

    async def check_if_player_turn(self, message):
        if message.author.id == self.players[self.player_turn].ID:
            return True
        await message.channel.send(f"is {self.players[self.player_turn].name} turn =)")
        return False

    async def on_call(self, message):
        if not await self.check_if_player_turn(message):
            return
        delta = self.bet_amount - self.players[self.player_turn].lest_bet
        self.jackpot[self.players[self.player_turn].ID] += min(delta, self.players[self.player_turn].balance)
        self.players[self.player_turn].balance -= min(delta, self.players[self.player_turn].balance)
        await self.end_move(message)

    async def on_raise(self, message):
        if not await self.check_if_player_turn(message):
            return
        try:
            val = float(message.content.split(sep=" ")[1])
        except ValueError:
            await message.channel.send("To raise you must enter number")
            return
        except IndexError:
            await message.channel.send("To raise you must enter number")
            return
        if val - self.players[self.player_turn].lest_bet > self.players[self.player_turn].balance:
            await message.channel.send("you don't have enough money")
            return
        if val < self.min_amount:
            await message.channel.send(f"The minimum amount is {self.min_amount}")
            return
        if val <= self.bet_amount:
            await message.channel.send(f"you must bet more then {self.bet_amount}")
            return

        current_player = self.players[self.player_turn]
        self.jackpot[current_player.ID] += val - current_player.lest_bet
        current_player.balance -= val - current_player.lest_bet
        self.bet_amount = val
        current_player.lest_bet = val
        self.last_bet = (self.player_turn - 1) % self.number_of_player
        await self.end_move(message)

    async def on_check(self, message):
        if not await self.check_if_player_turn(message):
            return
        delta = self.bet_amount - self.players[self.player_turn].lest_bet
        if delta != 0:
            await message.channel.send(f"you must call, raise or fold")
            return
        await self.end_move(message)

    async def on_fold(self, message):
        self.players[self.player_turn].state = False
        await self.end_move(message)

    async def end_move(self, message):
        while True:
            if self.player_turn == self.last_bet:
                if len(self.board) == 5 or sum([player.state for player in self.players]) < 2 or sum(
                        [player.balance != 0 for player in self.players]) < 2:
                    await self.end_game(message)
                    return
                self.open_card()
                self.bet_init()
                if self.players[self.player_turn].state and self.players[self.player_turn].balance != 0:
                    break
            else:
                self.player_turn = (self.player_turn + 1) % self.number_of_player
                if self.players[self.player_turn].state and self.players[self.player_turn].balance != 0:
                    break
                else:
                    print(
                        f"player skip {self.players[self.player_turn].name} ,state {self.players[self.player_turn].state} ,balance {self.players[self.player_turn].balance}")
        await message.channel.send(f"```{str(self)}```")

    async def end_game(self, message):
        while len(self.board) < 5:
            self.open_card()
        await self.winners_check(message)
        self.save_players_balance()
        self.running = False

    def open_card(self):
        if len(self.board) == 0:
            self.board = [self.deck.draw_card() for _ in range(3)]
        else:
            self.board.append(self.deck.draw_card())

    async def winners_check(self, message):
        not_folded = [player for player in self.players if player.state]
        find_bast_hands(not_folded, self.board)
        response = str(self.board) + os.linesep
        for player in self.players:
            response += f"{player.name} : {player.hand}{os.linesep}"
        while not self.is_jackpot_empty():
            print(f"jackpot : {self.jackpot}")
            winners = compare_hands(not_folded)
            num_of_winners = len(winners)
            for winner in winners:
                wins_money: float = 0
                min_jackpot = min([self.jackpot[player.ID] for player in winners])
                for player in self.players:
                    if winner != player:
                        wins_money += min(self.jackpot[player.ID], min_jackpot) / num_of_winners
                        self.jackpot[player.ID] -= min(self.jackpot[player.ID], min_jackpot) / num_of_winners
                wins_money += min_jackpot / num_of_winners
                response += f"player {winner.name} wins {wins_money} with {winner.hand} {winner.bast_hand.rank} {os.linesep}"
                winner.balance += wins_money
                self.jackpot[winner.ID] -= min_jackpot / num_of_winners
                num_of_winners -= 1
            not_folded = [player for player in not_folded if self.jackpot[player.ID] != 0]
        for player in self.players:
            player.throw_cards()
        await message.channel.send(response)

    def is_jackpot_empty(self):
        for vel in self.jackpot.values():
            if vel != 0:
                return False
        return True

    async def distribute_cards(self):
        for player in self.players:
            for _ in range(2):
                player.add_card(self.deck.draw_card())
            player.start_balance = player.balance
            await player.user.send(
                f"""```your`s balance :{str(player.balance)}
            your`s cards :{str(player.hand)}```""")

    def __repr__(self):
        return f"""The board is: {self.board}
               The jackpot is: {sum(self.jackpot.values())}
               The player turn: {self.players[self.player_turn].name}"""
