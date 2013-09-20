# Name:        poker
# Purpose:     play poker!
#
# Author:      Herminio Gonzalez
#
# Created:     19/09/2013

import random
import time

def count_items(list):
    'return a dictionary with the number of times something occurs in list'
    dic = {}
    for item in list:
        if item in dict:
            dic[item] += 1
        else:
            dic[item] = 1
    return dic

class Shoe():
    'A shoe of playing cards, for shuffling and dealing out cards'
    def __init__(self, num_decks=1):
        'initialize with a given number of decks'
        a_deck = [r+s for s in 'HDSC' for r in '23456789TJQKA']
        self.shoe = [card for card in a_deck for i in range(num_decks)]

    def shuffle1(self):
        'shuffle the cards in the shoe'
        tmp_shoe = []
        for card in self.shoe:
            tmp_shoe.append((random.randint(0, 9999), card))
        # tmp_shoe is now a list of the form [(534,'2H'), (9035:'2H')...]
        del self.shoe
        self.shoe = [card for (r, card) in sorted(tmp_shoe)]

    def shuffle2(self):
        'shuffle the cards in the shoe using a swapping method'
        n = len(self.shoe)
        for _ in range(n/2):
            # pick two random cards and swap them
            i = random.randint(0, n-1)
            j = random.randint(0, n-1)
            tmp = self.shoe[i]
            self.shoe[i] = self.shoe[j]
            self.shoe[j] = tmp

    def deal(self, size=5):
        '''deal(size, default 5) --> list of cards
        Deal cards from the shoe '''
        if len(self.shoe) < size:
            raise Exception('Not enough cards in shoe.')
        hand = []
        for _ in range(size):
            hand.append( self.shoe.pop() )
        return Hand(hand)

class Hand():
    '''A poker hand. This is basically a list of cards,
    e.g. ['TD', 'TH', '2H', '2S', '2C'] (full house)'''
    def __init__(self, cards):
        self.cards = cards
        self.card_ranks = [self.card_rank(c[0]) for c in self.cards]
        self.card_suits = [c[1] for c in self.cards]

    def card_rank(self, rank):
        '''take a card (e.g. four of spades: '4S') and return its rank (4)'''
        r = rank[0]
        if r == 'T':
            return 10
        elif r == 'J':
            return 11
        elif r == 'Q':
            return 12
        elif r == 'K':
            return 13
        elif r == 'A':
            return 14   # ace is the highest rank
        else:
            return int(r)

    def is_straight(self):
        'return True if cards form an unbroken sequence'
        rs = sorted(self.card_ranks)
        diffs = [a-b for (a,b) in zip(rs[1:], rs)]
        # diffs is a list that holds the differences between a card and the next
        # if it is a sequence, the list should be [1, 1, 1, 1, 1]
        for diff in diffs:
            if diff <> 1:
                return False
        return True

    def is_flush(self):
        'return True if all cards are of the same suit'
        ss = sorted(self.card_suits)
        return ss[0] == ss[-1] # if first and last match, then all are the same.

    def rank(self):
        '''return a tuple that gives a metric of how strong the poker hand is
        (8, 12) --> straight flush, queen high
        (7, [12, 13]) --> 4 queens and a king kicker
        (6, [12, 13]) --> full house. 3 queens 2 kings
        (5, [6, 5, 4, 3, 2]) --> flush, card ranks given from high to low
        (4, 12) --> straight, queen high
        (3, [12, 2, 3]) --> 3 queens, a 2 and a 3
        (2, [13, 12, 4]) --> 2 kings, 2 queens and a 4
        (1, [12, 4, 3, 2]) --> 2 queens
        (0, [6, 5, 4, 3, 2]) --> got nothin'! 6 high...
        '''

        dic = count_items(self.card_ranks) # build a dictionary of rank counts
        # list of groups of equal-ranked cards, in decreasing counts
        # e.g. [(4,9), (1,11)] --> four 9's and one jack
        items = sorted(dic.items(), key=lambda (r,c): (c,r), reverse=True)
        ranks = [r for (r,c) in items]
        counts = [c for (r,c) in items]

        if self.is_straight() and self.is_flush():
            return (8, max(self.card_ranks))
        elif counts[0] == 4:
            return (7, ranks)
        elif counts[0] == 3 and counts[1] == 2:
            return (6, ranks)
        elif self.is_flush():
            return (5, sorted(ranks, reverse=True))
        elif self.is_straight():
            return (4, max(ranks))
        elif counts[0] == 3:
            return (3, ranks)
        elif counts[0] == 2 and counts[1] == 2:
            return (2, ranks)
        elif counts[0] == 2:
            return (1, ranks)
        else:
            return (0, ranks)


def run_tests():
    '''testing is very important'''
    t0 = time.clock()
    for num_decks in [0,1,2,3,4,5,6]:
        s = Shoe(num_decks)
        tmp_shoe = s.shoe[:]
        assert len(s.shoe) == num_decks * 52
        s.shuffle1()
        assert(len(s.shoe)) == num_decks * 52
        s.shuffle2()
        assert(len(s.shoe)) == num_decks * 52
        assert sorted(tmp_shoe) == sorted(s.shoe)
        if num_decks > 0:
            hand = s.deal()
            assert len(s.shoe) + 5 == num_decks * 52
            assert len(hand.cards) == 5
            hand = s.deal(7)
            assert len(s.shoe) + 5 + 7 == num_decks * 52
            assert len(hand.cards) == 7

    h1 = Hand('TD 8H 9H 6S 7C'.split(' '))  # straight, ten high
    h2 = Hand('TD TH 9H 6S 7C'.split(' '))  # one-pair, tens
    h3 = Hand('7C 6S 9H 8H TD'.split(' '))  # straight, ten high
    h4 = Hand('TD 8D 9D 6D 7D'.split(' '))  # straight flush, ten high
    assert h1.card_rank('T') == 10
    assert h1.card_rank('TD') == 10
    assert h1.card_rank('J') == 11
    assert h1.card_rank('Q') == 12
    assert h1.card_rank('K') == 13
    assert h1.card_rank('A') == 14
    assert h1.is_straight()
    assert h2.is_straight() == False
    assert h3.is_straight()
    assert h1.is_flush() == False
    assert h2.is_flush() == False
    assert h3.is_flush() == False
    assert h4.is_flush()

    h5 = Hand('TD TH TS TC 7D'.split(' '))  # 4 tens and a seven kicker
    h6 = Hand('7D TD TH TS TC'.split(' '))  # 4 tens and a seven kicker
    assert h4.rank() == (8, 10)
    assert h5.rank() == (7, [10, 7])
    assert h6.rank() == (7, [10, 7])
    h7 = Hand('KH QH KD KS QD'.split(' '))  # full house, queens over kings
    h8 = Hand('4H 5H 5D 4D 4C'.split(' '))  # full house, 4's over 5's
    assert h7.rank() == (6, [13, 12])
    assert h8.rank() == (6, [4, 5])
    h1 = Hand('5H 2H TH KH 3H'.split(' '))  # flush of hearts
    h2 = Hand('4D 5D 6D 3D AD'.split(' '))  # flush of diamonds
    assert h1.rank() == (5, [13, 10, 5, 3, 2])
    assert h2.rank() == (5, [14, 6, 5, 4, 3])
    h3 = Hand('2D 3D 4H 5D 6D'.split(' '))  # straight, 6 high
    h4 = Hand('6D 5D 4H 3D 2D'.split(' '))  # straight, 6 high
    assert h3.rank() == h4.rank() == (4, 6)
    h5 = Hand('QD QH QS 3D 4D'.split(' '))  # three queens, 4, 3
    h6 = Hand('2D 2H 2S 3D 4S'.split(' '))  # three 2's, 4, 3
    assert h5.rank() == (3, [12, 4, 3])
    assert h6.rank() == (3, [2, 4, 3])
    h7 = Hand('KD 9H 9S KD AD'.split(' '))  # 2-pair, kings over 9's, ace
    h8 = Hand('2D 2H 3S 3D 4S'.split(' '))  # 2-pair, 3's over 2's, 4
    assert h7.rank() == (2, [13, 9, 14])
    assert h8.rank() == (2, [3, 2, 4])
    h1 = Hand('TD 9H 9S KD AD'.split(' '))  # pair of 9s
    h2 = Hand('2D 2H 3S 5D 4S'.split(' '))  # pair of 2s
    assert h1.rank() == (1, [9, 14, 13, 10])
    assert h2.rank() == (1, [2, 5, 4, 3])
    h3 = Hand('2D 7H 3S 5D 4S'.split(' '))  # nothing
    assert h3.rank() == (0, [7, 5, 4, 3, 2])

    print 'Tests passed.'
    print 'Tests took %1.3f sec.' % (time.clock() - t0)

def timer():
    'measure time it takes to run stuff'
    s = Shoe(5)
    t0 = time.clock()
    s.shuffle1()
    t_shuf1 = time.clock() - t0

    t0 = time.clock()
    s.shuffle2()
    t_shuf2 = time.clock() - t0

    print 'shuffle1: %1.4f sec. shuffle2: %1.4f sec.' % (t_shuf1, t_shuf2)

def main():
    #run_tests()

    s = Shoe(3) # play with 3 decks
    s.shuffle1()
    s.shuffle2()
    while len(s.shoe) >= 5:
        raw_input('press any key to deal.')
        hand = s.deal()
        print '%s --> %s' % (hand.cards, hand.rank())
    print 'no more hands.'


if __name__ == '__main__':
    main()
