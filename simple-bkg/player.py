import random
import game as gamemod
import numpy as np


OFF = gamemod.OFF
ON = gamemod.ON

class Player:
    def __init__(self,color,num):
        self.color = color
        self.num = num
    
    def take_turn(self,moves,game=None):
        raise NotImplementedError("Override me")

class RandomPlayer(Player):
    def take_turn(self,moves,game=None):
        if moves:
            return random.choice(list(moves))
        return None
        

class ReflexPlayer(Player,object):
    
    def __init__(self,color,num,evalFn,evalArgs=None):
        super(self.__class__,self).__init__(color,num)
        self.evalFn = evalFn
        self.evalArgs = evalArgs

    def take_turn(self,moves,game):
        """
        Simple Reflex Player - evaluates move as 
        score = 5*outPieces - barPieces - singletons
        """
        bestScore = float("-inf")
        move = None
        for m in moves:
            tmpGame = game.clone()
            tmpGame.take_turn(m,self.color)
            score = self.evalFn(game,self.evalArgs)
            if score > bestScore:
                bestScore = score
                move = m
        return move

class ExpectiMaxPlayer(Player,object):
    
    def __init__(self,color,num,evalFn,evalArgs=None):
        super(self.__class__,self).__init__(color,num)
        self.evalFn = evalFn
        self.evalArgs = evalArgs

    def take_turn(self,moves,game,depth=1):
        if depth==0:
            return self.evalFn(game,self.evalArgs)
        move = None
        bestScore = float("-inf")
        for m in moves:
            tmpGame = game.clone()
            tmpGame.take_turn(m,self.color)
            score = self.expecti(tmpGame,depth,game.opponent(self.color))
            if score>bestScore:
                move = m
                bestScore = score
        return move
        
    def expecti(self,game,depth,color):
        total = 0
        for i in range(1,game.die+1):
            for j in range(i,game.die+1):
                moves = game.get_moves((i,j),color)
                rollTotal = 0.
                for m in moves:
                    tmpGame = game.clone()
                    tmpGame.take_turn(m,color)
                    rollTotal += self.take_turn(None,tmpGame,depth-1)
                if moves:
                    total += rollTotal/len(moves)

        return total/(game.die*(game.die+1)/2.)
            
    
class HumanPlayer(Player):

    def take_turn(self,moves,game=None):
        while True:
            if not moves:
                raw_input("No moves for you...(hit enter)")
                break
            while True:
                mv1 = raw_input("Please enter a move <location start,location end> ('%s' for off the board): "%OFF)
                mv1 = self.get_formatted_move(mv1)
                if not mv1:
                    print 'Bad format enter e.g. "3,4"'
                else:
                    break

            while True:
                mv2 = raw_input("Please enter a seond move (enter to skip): ")
                if mv2 == '':
                    mv2 = None
                    break
                mv2 = self.get_formatted_move(mv2)
                if not mv2:
                    print 'Bad format enter e.g. "3,4"'
                else:
                    break

            if mv2:
                move = (mv1,mv2)
            else:
                move = (mv1,)

            if move in moves:
                break
            elif move[::-1] in moves:
                move = move[::-1]
                break
            else:
                print "You can't play that move"

        return move

    def get_formatted_move(self,move):
        try:
            start,end = move.split(",")
            if start==ON:
                return (start,int(end))
            start = int(start)
            if end == OFF:
                return (start,end)
            end = int(end)
            return (start,end)
        except:
            return False
