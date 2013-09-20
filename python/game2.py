# coding: utf-8

# example game for Hibiki
# by Herminio Gonzalez, Sep 2013

import random
import os.path # for checking if game file exists
import pickle  # for writing and reading game file


def make_question():
    """prepare a question of the form 'A OP B' where A and B are integers
    and OP (operator) is one of [+, -, x].
    returns three things:
        - question: the question, string.
        - answer: the correct answer, int.
        - difficulty: 1, 2 or 3 for +, - or x respectively"""

    rand = random.randint # being lazy, don't like typing 'random.randint' over and over

    # secret bonus! about once every 100 times, ask a special question:
    if rand(1, 100) == 100:
        question = 'What did you eat yesterday? > '
        return (question, 'SECRET_BONUS', 4)

    a = rand(50, 100)
    b = rand( 0,  50)
    op = ['+', '-', 'x'][rand(0,2)]

    # %d is for a number, %s is for a string
    question = 'What is  %d %s %d ?  > ' % (a, op, b)
    if op == '+':
        answer = a + b
        difficulty = 1
    if op == '-':
        answer = a - b
        difficulty = 2
    if op == 'x':
        answer = a * b
        difficulty = 3
    return (question, answer, difficulty)

def main():
    gamefile = 'game2.save'
    if os.path.exists(gamefile):
        # file exists, so load up the game and continue from last time
        f = open(gamefile, 'rb')
        gamedata = pickle.load(f)
        f.close()
        (name, score, mult, turn) = gamedata
        print "Welcome back, %s." % name
    else:
        # file doesn't exist, start a new game
        name = raw_input('Enter name: ')
        score = 1.0  # score is multiplied by mult in every turn
        mult = 1.0   # +0.1 for correct answer. gets halved for wrong answer.
        turn = 1     # +1 for every turn

    print "NOTE: To quit, enter the letter 'q' as your answer. You game progress will be saved."

    while True:  # endless loop

        # %f is for a float (e.g. 1.23)
        print '%s, Turn:%d    Mult:%1.3f    Score:%d' % (name, turn, mult, score)

        (question, true_answer, difficulty) = make_question()
        raw_answer = raw_input(question)

        if raw_answer.strip() == 'q':
            print 'Leaving already? See ya!'
            break

        # check if player entered something that is not a number:
        try:
            answer = int(raw_answer)
        except ValueError:
            answer = 0

        if true_answer == 'SECRET_BONUS' or answer == true_answer:
            print 'Correct!'
            score = (score + (5.0 * difficulty)) * mult
            mult += 0.1
        else:
            print 'Sorry. The correct answer is %d.' % true_answer
            mult = max(1.0, mult * 0.5)   # mult gets halved, but does not go below 1.0

        # save game automatically after every turn
        gamedata = (name, score, mult, turn)
        f = open(gamefile, 'wb')
        pickle.dump(gamedata, f)
        f.close()

        turn +=1

main()
