# --------------
# User Instructions
#
# Write a function, longest_subpalindrome_slice(text) that takes
# a string as input and returns the i and j indices that
# correspond to the beginning and end indices of the longest
# palindrome in the string.
#
# Grading Notes:
#
# You will only be marked correct if your function runs
# efficiently enough. We will be measuring efficency by counting
# the number of times you access each string. That count must be
# below a certain threshold to be marked correct.
#
# Please do not use regular expressions to solve this quiz!

def is_palindrome(s):
    "Return true if string s is a palindrome. Case does not matter."
    s = s.lower()
    return s == s[::-1]

def grow(text, i, j):
    """Attempt to 'grow' a palindrom starting at slice text[i:j].
     Return the slice indices of the longest palindome centered around it"""
    while(i > 0 and j < len(text) and text[i-1] == text[j]):
        i -= 1; j += 1
    return (i, j)

def longest_subpalindrome_slice(text):
    "Return (i, j) such that text[i:j] is the longest palindrome in text."
    text = text.upper()
    maxlen = 0
    answer = (0, 0)
    for (p, _) in enumerate(text):
        for q in [p, p+1]:
            (i, j) =  grow(text, p, q)
            if j-i > maxlen:
                answer = (i, j)
                maxlen = j-i
    return answer

def test():
    L = longest_subpalindrome_slice
    assert L('racecar') == (0, 7)
    assert L('Racecar') == (0, 7)
    assert L('RacecarX') == (0, 7)
    assert L('Race carr') == (7, 9)
    assert L('') == (0, 0)
    assert L('something rac e car going') == (8,21)
    assert L('xxxxx') == (0, 5)
    assert L('Mad am I ma dam.') == (0, 15)
    return 'tests pass'

def main():
    print test()

if __name__ == '__main__':
    main()
