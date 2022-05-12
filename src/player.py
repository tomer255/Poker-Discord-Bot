class Player:
    def __init__(self, balance, user):
        self.user = user
        self.ID = user.id
        self.name = user.name
        self.state = True
        self.hand = []
        self.balance = balance
        self.start_balance = 0
        self.bast_hand = None
        self.lest_bet = 0
        self.exit = False

    def add_card(self, card):
        self.hand.append(card)

    def bet(self, bet_amount):
        if self.balance >= bet_amount:
            self.balance -= bet_amount
            return True
        return False

    def throw_cards(self):
        self.hand = []
        self.bast_hand = None

    def __repr__(self):
        return f" Name :  {self.name} \n " \
               f"hand : {self.hand} \n " \
               f"balance:{self.balance} \n"

    def __lt__(self, other):
        if self.bast_hand < other.bast_hand:
            return True

    def __eq__(self, other):
        return self.ID == other.ID
        # if self.bast_hand < other.bast_hand or self.bast_hand > other.bast_hand:
        #     return False
        # return True
