#------------------
# User Instructions
#
# Hopper, Kay, Liskov, Perlis, and Ritchie live on
# different floors of a five-floor apartment building.
#
# Hopper does not live on the top floor.
# Kay does not live on the bottom floor.
# Liskov does not live on either the top or the bottom floor.
# Perlis lives on a higher floor than does Kay.
# Ritchie does not live on a floor adjacent to Liskov's.
# Liskov does not live on a floor adjacent to Kay's.
#
# Where does everyone live?
#
# Write a function floor_puzzle() that returns a list of
# five floor numbers denoting the floor of Hopper, Kay,
# Liskov, Perlis, and Ritchie.import itertools

def top_floor(f): return f == 5
def bottom_floor(f): return f == 1
def adjacent_floor(f1, f2): return abs(f1 - f2) == 1

def floor_puzzle():
    return next([Hopper, Kay, Liskov, Perlis, Ritchie]
        for Hopper in range(1, 6)
            if not top_floor(Hopper)
        for Kay in  range(1, 6)
            if not bottom_floor(Kay)
        for Liskov in range(1, 6)
            if not top_floor(Liskov) and not bottom_floor(Liskov)
        for Perlis in range(1, 6)
            if Perlis > Kay
        for Ritchie in range(1, 6)
            if not adjacent_floor(Ritchie, Liskov)
            if not adjacent_floor(Liskov, Kay)
            if len(set([Hopper, Kay, Liskov, Perlis, Ritchie])) == 5)
    #return [Hopper, Kay, Liskov, Perlis, Ritchie]
def main():
    print floor_puzzle()

if __name__ == '__main__':
    main()

