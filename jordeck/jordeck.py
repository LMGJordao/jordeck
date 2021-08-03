# -*- coding: utf-8 -*-
"""jordeck.py - Pythonic OOP card decks and shuffling"""

__author__      = "Luís Jordão"
__copyright__   = "Copyright 2021, 21stacks"
__credits__     = ["Luís Jordão"]
__license__     = "MIT License"
__version__     = "1.0.0"
__email__       = "lmgjordao@gmail.com"
__status__      = "Release"

import random as rng
from math import floor

class Card:
    def __init__(self, suit: str, value: str) -> None:
        self.suit = str(suit)
        self.value = str(value)

    def __str__(self) -> str:
        return f"{self.value} of {self.suit}"

class Deck:     
    def __init__(self, size: int = 1, cards: list = None) -> None:
        try:
            size = int(size)
        except ValueError:
            raise ValueError("invalid literal for Deck.__init__() size")
        try:
            assert size > 0
        except AssertionError:
            raise ValueError("invalid size for Deck.__init__(): must be greater than 0")

        self.__deck_type = size
        self.__discarded_cards = list()

        if cards is None:           # new deck
            self.__cards = list()
            self.__deck()
        else:                       # deck from cards list
            self.__cards = cards

    def __deck(self) -> None:
        self.__cards = list()                                   # resets the list with cards
        for _ in range(self.__deck_type):                       # creates a deck with size number of 52-card decks
            # runs each permutation of suits and values
            for suit in ["Spades", "Clubs", "Diamonds", "Hearts"]:
                for value in ["2", "3", "4", "5", "6", "7", "8", "9", "10", "A", "K", "Q", "J"]:
                    self.__cards.append(Card(suit, value))      # creates a card and adds it to the top of the deck
    
    def draw(self) -> Card:
        return self.__cards.pop()   # removes the top card of the deck

    def deal(self, n) -> list:      # draws n cards from the top
        return [self.draw() for _ in range(n)]

    def insert_top(self, card) -> None:
        self.__cards.append(card)

    def insert_bottom(self, card) -> None:
        self.__cards.insert(0, card)

    def put_on_top_of(self, target) -> None:
        target.__cards.extend(self.__cards)     # merges self with target, so that self is on top of the target
        self.__cards = target.__cards

    def wash(self) -> None:
        rng.shuffle(self.__cards)   # randomizes the cards in the deck

    def shuffle(self) -> None:
        # shuffling reference https://www.vegas-aces.com/learn/deal-blackjack-02-shuffling/#shuffling-1
        if self.__deck_type == 1:
            self.__single_deck_shuffle()
        elif self.__deck_type == 2:
            self.__double_deck_shuffle()
        elif self.__deck_type in (4, 6, 8):
            self.__4_6_8_deck_shuffle()
        else:
            self.wash()

    def __single_deck_shuffle(self):
        # Strip 4 -> Riffle -> Strip 4 -> Riffle -> Box -> Riffle -> Cut 10
        self.__strip(4)
        self.__riffle()
        self.__strip(4)
        self.__riffle()
        self.__box()
        self.__riffle()
        self.__cut(edges=10)

    def __double_deck_shuffle(self):
        # Riffle -> Strip 7 -> 1/3 top to bot -> Riffle -> 1/3 bot to top -> Riffle -> Riffle -> Cut 20
        self.__riffle()
        self.__strip(7)
        self.__third_top_to_bot()
        self.__riffle()
        self.__third_bot_to_top()
        self.__riffle()
        self.__riffle()
        self.__cut(edges=20)

    def __4_6_8_deck_shuffle(self):             #TODO: reduce repeated code
        total_cards_in_deck = len(self.__cards)
        # Split in half -> Take +/- 1/4 of the deck from each stack and merge them
        left, right = self.__cards[:total_cards_in_deck // 2], self.__cards[total_cards_in_deck // 2:]  # splits the deck in two halves
        left_offset = len(left)                                 # pointer for the top card in the left half
        right_offset = len(right)                               # pointer for the top card in the right half

        chunk_max_size = (total_cards_in_deck // 2) // 4        # max size of the chunks to be removed
        chunk_max_size_variation = chunk_max_size // 4          # max variation of the max size of those chunks

        chunk_size = chunk_max_size - floor(rng.random() * chunk_max_size_variation)        # chunk size to take from left
        left_chunk = left[left_offset - chunk_size : left_offset]                           # "remove" the chunk from left
        left_offset -= chunk_size

        chunk_size = chunk_max_size - floor(rng.random() * chunk_max_size_variation)        # chunk size to take from right
        right_chunk = right[right_offset - chunk_size : right_offset]                       # "remove" the chunk from right
        right_offset -= chunk_size

        left_chunk.extend(right_chunk)                          # put the right chunk on top of the left
        # Riffle -> Strip 4 -> Riffle
        working_deck = Deck(cards=left_chunk)                   # deck to shuffle
        working_deck.__riffle()
        working_deck.__strip(4)
        working_deck.__riffle()

        # repeating until all the cards are shuffled
        while left_offset >= chunk_max_size and right_offset >= chunk_max_size:
            # take one chunk from left stack
            chunk_size = chunk_max_size - floor(rng.random() * chunk_max_size_variation)
            left_chunk = left[left_offset - chunk_size : left_offset]
            left_offset -= chunk_size

            # take one chunk from the working deck
            chunk_size = chunk_max_size - floor(rng.random() * chunk_max_size_variation)
            working_deck_chunk = working_deck.__cards[len(working_deck.__cards) - chunk_size:]

            left_chunk.extend(working_deck_chunk)
            # Riffle -> Strip 4 -> Riffle
            aux = Deck(cards=left_chunk)
            aux.__riffle()
            aux.__strip(4)
            aux.__riffle()

            # Place these cards on top of the working deck
            working_deck.__cards[len(working_deck.__cards) - chunk_size:] = aux.__cards[:chunk_size]
            working_deck.__cards.extend(aux.__cards[chunk_size:])

            # take one chunk from right stack
            chunk_size = chunk_max_size - floor(rng.random() * chunk_max_size_variation)
            right_chunk = right[right_offset - chunk_size : right_offset] 
            right_offset -= chunk_size

            # take one chunk from the working deck
            chunk_size = chunk_max_size - floor(rng.random() * chunk_max_size_variation)
            working_deck_chunk = working_deck.__cards[len(working_deck.__cards) - chunk_size:]

            right_chunk.extend(working_deck_chunk)
            # Riffle -> Strip 4 -> Riffle
            aux = Deck(cards=right_chunk)
            aux.__riffle()
            aux.__strip(4)
            aux.__riffle()

            # Place these cards on top of the working deck
            working_deck.__cards[len(working_deck.__cards) - chunk_size:] = aux.__cards[:chunk_size]
            working_deck.__cards.extend(aux.__cards[chunk_size:])
        
        # do the same for the last 2 chunks
        left_chunk = left[:left_offset]                 # remainder of the left stack

        # take one chunk from the working deck
        chunk_size = chunk_max_size - floor(rng.random() * chunk_max_size_variation)
        working_deck_chunk = working_deck.__cards[len(working_deck.__cards) - chunk_size:]

        left_chunk.extend(working_deck_chunk)
        # Riffle -> Strip 4 -> Riffle
        aux = Deck(cards=left_chunk)
        aux.__riffle()
        aux.__strip(4)
        aux.__riffle()

        # Place these cards on top of the working deck
        working_deck.__cards[len(working_deck.__cards) - chunk_size:] = aux.__cards[:chunk_size]
        working_deck.__cards.extend(aux.__cards[chunk_size:])

        right_chunk = right[:right_offset]              # remainder of the right stack

        # take one chunk from the working deck
        chunk_size = chunk_max_size - floor(rng.random() * chunk_max_size_variation)
        working_deck_chunk = working_deck.__cards[len(working_deck.__cards) - chunk_size:]

        right_chunk.extend(working_deck_chunk)
        # Riffle -> Strip 4 -> Riffle
        aux = Deck(cards=right_chunk)
        aux.__riffle()
        aux.__strip(4)
        aux.__riffle()

        # Place these cards on top of the working deck
        working_deck.__cards[len(working_deck.__cards) - chunk_size:] = aux.__cards[:chunk_size]
        working_deck.__cards.extend(aux.__cards[chunk_size:])

        # Split the deck in 2 equal parts
        left, right = working_deck.__cards[:total_cards_in_deck // 2], working_deck.__cards[total_cards_in_deck // 2:]
        left_offset = len(left)                                 # pointer for the top card in the left half
        right_offset = len(right)                               # pointer for the top card in the right half

        # Take 1/4 of a deck from each stack and riffle
        self.__cards = []                   # to stack the shuffled cards
        while left_offset >= chunk_max_size and right_offset >= chunk_max_size:
            chunk_size = chunk_max_size - floor(rng.random() * chunk_max_size_variation)        # chunk size to take from left
            left_chunk = left[left_offset - chunk_size : left_offset]                           # "remove" the chunk from left
            left_offset -= chunk_size

            chunk_size = chunk_max_size - floor(rng.random() * chunk_max_size_variation)        # chunk size to take from right
            right_chunk = right[right_offset - chunk_size : right_offset]                       # "remove" the chunk from right
            right_offset -= chunk_size

            left_chunk.extend(right_chunk)
            aux = Deck(cards=left_chunk)
            aux.__riffle()
            aux.put_on_top_of(self)
        
        # Last quarter
        left_chunk = left[:left_offset]
        right_chunk = right[:right_offset]

        left_chunk.extend(right_chunk)
        aux = Deck(cards=left_chunk)
        aux.__riffle()
        aux.put_on_top_of(self)

        self.__cut(edges=chunk_max_size)

    def __strip(self, times: int = 2) -> None:
        try:
            times = int(times)
        except ValueError:
            raise ValueError("invalid literal for Deck.__strip() times")
        try:
            assert times > 1
        except AssertionError:
            raise ValueError("invalid times for Deck.__strip(): must be greater than 1")

        total_cards_in_deck = len(self.__cards)
        strip_offset = total_cards_in_deck                  # points to the last card stripped
        aux_deck = list()                                   # stores the strip result

        # Define the interval of cards that is going to be striped each iteration
        # i.e. if s is the max number of cards each iteration can strip and v is
        # the maximum variation for each iteration, then the number of cards
        # stripped each iteration, x, is {x ∈ ℕ: s - v <= x <= s}
        strip_max_size = total_cards_in_deck // times       # this is s
        strip_max_size_variation = strip_max_size // 3      # this is v

        # Iterates until theres only a chunk of cards left
        while strip_offset >= strip_max_size:
            strip_size = strip_max_size - floor(rng.random() * strip_max_size_variation)   # provides randomness
            strip = self.__cards[strip_offset - strip_size : strip_offset]                      # picks a chunk of cards
            aux_deck.extend(strip)                                                              # adds the chunk to the top of the result
            strip_offset -= strip_size                                                          # iterates to the next chunk
        aux_deck.extend(self.__cards[0 : strip_offset])     # adds the last chunk to the result
        
        self.__cards = aux_deck                             # replaces the deck with the stripped one

    def __riffle(self) -> None:
        half = len(self.__cards) // 2                                               # magic number for half the deck
        left, right = self.__cards[:half], self.__cards[half:]                      # splits the deck in two halves
        self.__cards = [card for riffle in zip(left, right) for card in riffle]     # interleaves the cards from each half
        if walrus := (len(left) - len(right)) != 0:                                 # in case they have different sizes
            self.__cards.extend(left[-walrus:]) if walrus > 0 else self.__cards.extend(right[walrus:])

    def __box(self) -> None:
        third = len(self.__cards) // 3                              # magic number for a third of the deck                                      
        bottom, top = self.__cards[:third], self.__cards[third:]    # splits the first third of the deck (bottom) and the rest (top)
        top.extend(bottom)                                          # puts bottom on top
        self.__cards = top                                          # replaces de deck with the boxed one

    def __cut(self, cut = -1, edges = 0) -> None:
        total_cards_in_deck = len(self.__cards)
        try:
            cut = int(cut)
        except ValueError:
            raise ValueError("invalid literal for Deck.__cut() cut")
        try:
            edges = int(edges)
        except ValueError:
            raise ValueError("invalid literal for Deck.__cut() edges")
        try:
            assert edges >= 0 and edges < total_cards_in_deck // 2                                          # to create an interval for cutting cards
        except AssertionError:
            raise ValueError("invalid edges for Deck.__cut(): must be in the range [0, half number of cards in deck[")

        if cut == -1:
            cut = rng.randint(edges + 1, total_cards_in_deck - edges - 1)
        else:
            try:
                assert cut > edges and cut < total_cards_in_deck - edges                                    # make sure is cutting in the correct interval
            except AssertionError:
                raise ValueError("invalid cut for Deck.__cut(): must be in the range ]edges, total number of cards in deck - edges[")

        bottom, top = self.__cards[:total_cards_in_deck - cut], self.__cards[total_cards_in_deck - cut:]    # split the decks where they were cut
        top.extend(bottom)                                                                                  # puts bottom on top
        self.__cards = top                                                                                  # replaces de deck with the boxed one
        
    def __third_top_to_bot(self) -> None:
        total_cards_in_deck = len(self.__cards)
        third = total_cards_in_deck // 3                                                                        # magic number for a third of the deck                                      
        bottom, top = self.__cards[:total_cards_in_deck - third], self.__cards[total_cards_in_deck - third:]    # splits the last third of the deck (top) and the rest (bottom)
        top.extend(bottom)                                                                                      # puts bottom on top
        self.__cards = top                                                                                      # replaces de deck with the new one

    def __third_bot_to_top(self) -> None:
        third = len(self.__cards) // 3                              # magic number for a third of the deck                                      
        bottom, top = self.__cards[:third], self.__cards[third:]    # splits the first third of the deck (bottom) and the rest (top)
        top.extend(bottom)                                          # puts bottom on top
        self.__cards = top                                          # replaces de deck with the new one

    def discard(self, list_of_cards) -> None:       # places a list of cards in the discarded pile
        self.__discarded_cards.extend(list_of_cards)

    def refill_deck(self) -> None:                  # places the discarded pile back in the deck
        self.__cards.extend(self.__discarded_cards)

    def show(self) -> None:
        # Displays the deck in the terminal
        print(f"Deck size: {len(self.__cards)}")
        for card in self.__cards:
            print(card)
