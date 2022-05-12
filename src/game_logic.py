import src.player
import src.deck
import src.card as c

hand_type_val = {"high card": 0,
                 'pair': 1,
                 "two pairs": 2,
                 "three of a kind": 3,
                 'straight': 5,
                 "flush": 6,
                 "full house": 7,
                 "four of a kind": 8,
                 "straight flush": 9,
                 "royal flush": 10,
                 None: -1}


class rank:
    def __init__(self, card=None, rank=None, conflict=[c.Card(0, 0)]):
        self.card = card
        self.rank = rank
        self.conflict = conflict

    def __lt__(self, other):
        if hand_type_val[self.rank] < hand_type_val[other.rank]:
            return True
        elif hand_type_val[self.rank] > hand_type_val[other.rank]:
            return False

        for self_condition, other_condition in zip(self.conflict, other.conflict):
            if self_condition < other_condition:
                return True
            elif self_condition > other_condition:
                return False

        return False

    def __eq__(self, other):
        if self < other or self > other:
            return False
        return True

    def __repr__(self):
        return f"card = {self.card}, rank = {self.rank}, conflict = {self.conflict}"


def flush(cards):
    sorter = {"Diamonds": [], "Clubs": [], "Spades": [], "Hearts": []}
    for card in cards:
        sorter[card.suit].append(card)
    for suit_arr in sorter.values():
        if len(suit_arr) >= 5:
            # suit_arr.sort() # dane in straight
            straight_flush = straight(suit_arr)
            if straight_flush.rank is not None:
                if straight_flush.card[0].value == 14:
                    straight_flush.rank = "royal flush"
                else:
                    straight_flush.rank = "straight flush"
                return straight_flush
            return rank(card=suit_arr[:5], rank="flush", conflict=suit_arr[:5])
    return rank()


def straight(cards):
    cards.sort(reverse=True)
    for i in range(len(cards)-5):
        if is_straight(cards[i:i+5]):
            return rank(card=cards[i:i+5], rank="straight", conflict=[cards[i]])
    #[14,...,5,4,3,2]
    if [cards[i].value for i in range(-4, 1)] == [5, 4, 3, 2, 14]:
        return rank(card=[cards[i] for i in range(-4, 1)], rank="straight", conflict=[cards[-4]])
    return rank()


def is_straight(cards):
    for i in range(4):
        if cards[i].value - cards[i + 1].value != 1:
            return False
    return True


def card_counter(cards):
    counts = same_card_counter(cards)
    first_max, second_max = max_list_in_dict(counts)
    # FOUR OF A KIND
    if len(counts[first_max]) == 4:
        return rank(card=counts[first_max] + [max(set(cards) - set(counts[first_max]))],
                    rank="four of a kind",
                    conflict=[counts[first_max][0]])
    # FULL HOUSE
    if len(counts[first_max]) == 3 and len(counts[second_max]) >= 2:
        return rank(card=counts[first_max] + counts[second_max][:2],
                    rank="full house",
                    conflict=[counts[first_max][0], counts[second_max][0]])
    # THREE OF A KIND
    if len(counts[first_max]) == 3:
        kicker = list(set(cards) - set(counts[first_max]))
        kicker.sort(reverse=True)
        return rank(card=counts[first_max] + kicker[:2],
                    rank="three of a kind",
                    conflict=[counts[first_max][0]] + kicker[:2])
    # TWO PAIRS
    if len(counts[first_max]) == 2 and len(counts[second_max]) == 2:
        return rank(card=counts[first_max] + counts[second_max] + [
            max(set(cards) - set(counts[first_max]) - set(counts[second_max]))],
                    rank="two pairs",
                    conflict=[counts[first_max][0], counts[second_max][0],
                              max(set(cards) - set(counts[first_max]) - set(counts[second_max]))])
    # PAIR
    if len(counts[first_max]) == 2:
        kicker = list(set(cards) - set(counts[first_max]))
        kicker.sort(reverse=True)
        return rank(card=counts[first_max] + kicker[:3],
                    rank='pair',
                    conflict=[counts[first_max][0]] + kicker[:3])
    # HIGH CARD
    if len(counts[first_max]) == 1:
        conflict = list(cards)
        conflict.sort(reverse=True)
        return rank(card=conflict[:5],
                    rank="high card",
                    conflict=conflict[:5])
    return rank()


def same_card_counter(cards):
    counts = {i: [] for i in range(1, 15)}
    for card in cards:
        counts[card.value].append(card)
    return counts


def max_list_in_dict(cards_dict):
    first_max = 1
    second_max = 1
    for i in cards_dict.keys():
        if len(cards_dict[i]) >= len(cards_dict[first_max]):
            second_max = first_max
            first_max = i
        elif len(cards_dict[i]) >= len(cards_dict[second_max]):
            second_max = i

    return first_max, second_max


def check_hand(player, board):
    total_hand = player.hand + board

    flush_cards = flush(total_hand)
    if flush_cards.rank in ["royal flush", "straight flush"]:
        return flush_cards

    card_counter_cards = card_counter(total_hand)
    if card_counter_cards.rank in ["four of a kind", "full house"]:
        return card_counter_cards

    if flush_cards.rank in ["flush"]:
        return flush_cards

    straight_cards = straight(total_hand)
    if straight_cards.rank in ['straight']:
        return straight_cards

    return card_counter_cards

def find_bast_hands(players, board):
    for player in players:
        player.bast_hand = check_hand(player, board)


def compare_hands(players):

    winner = max(players)
    winners = [player for player in players if player.bast_hand == winner.bast_hand]
    return winners
