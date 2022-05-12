class Card:
    def __init__(self, value, suit_type):
        dict_suit = {"♥": "Hearts", "♠": "Spades", "♣": "Clubs", "♦": "Diamonds"}
        dict_value = {"J": 11, "Q": 12, "K": 13, "A": 14}
        if suit_type in dict_suit.keys():
            suit_type = dict_suit[suit_type]
        if value in dict_value.keys():
            value = dict_value[value]
        self.value = value
        self.suit = suit_type

    def __repr__(self):
        dict_suit = {"Hearts": "♥", "Spades": "♠", "Clubs": "♣", "Diamonds": "♦", 0: "?"}
        dict_value = {0: "?", 1: 'A', 2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7', 8: '8', 9: '9', 10: '10', 11: 'J',
                      12: 'Q', 13: 'K', 14: 'A'}
        return dict_value[self.value] + dict_suit[self.suit]

    def __lt__(self, other):
        return self.value < other.value
