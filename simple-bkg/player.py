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
        

class ReflexPlayer(Player):
    def take_turn(self,moves,game):
        """
        Simple Reflex Player - evaluates move as 
        score = 5*outPieces - barPieces - singletons
        """
        bestScore = -game.numpieces[self.color] #lowest possible score
        move = None
        for m in list(moves):
            tmpGame = game.clone()
            tmpGame.take_turn(m,self.color)

            score = submission.simpleEvaluate(game,self.color)
            if score > bestScore:
                bestScore = score
                move = m
        return move
            
    
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

class ExpectiMaxPlayer(Player,object):
    
    def __init__(self,color,num,evalFn,extraArgs=None):
        super(self.__class__,self).__init__(color,num)
        self.evalFn = evalFn
        self.extraArgs = extraArgs

    def take_turn(self,moves,game,depth=1):
        if depth==0:
            if extraArgs: return self.EvalFn(game,extraArgs)
            return self.EvalFn(game)
        move = None
        bestScore = 0
        for m in list(moves):
            tmpGame = game.clone()
            tmpGame.take_turn(m,self.color)
            score = self.expecti(tmpGame,depth,game.opponent[self.color])
            if score>bestScore:
                move = m
                bestScore = score
        return move
        
    def expecti(self,game,depth,color):
        total = 0
        for i in range(game.die):
            for j in range(i,game.die+1):
                moves = game.get_moves((i,j),color)
                for m in moves:
                    tmpGame = game.clone()
                    tmpGame.take_turn(m,color)
                    total += self.take_turn(None,tmpGame,depth-1)

        return total/(game.die*(game.die+1)/2.)

class NNPlayer(Player, object):
    
    def __init__(self,color,num,weights):
        super(self.__class__,self).__init__(color,num)
        self.w1,self.w2,self.b1,self.b2 = weights

    def take_turn(self,moves,game):
        move = None
        bestScore = 0
        for m in list(moves):
            
            # take the move
            tmpGame = game.clone()
            tmpGame.take_turn(m,self.color)

            # evaluate the state
            features = np.array(submission.extract_features(tmpGame)).reshape(-1,1)
            hiddenAct = 1/(1+np.exp(-(self.w1.dot(features)+self.b1)))
            pred = 1/(1+np.exp(-(self.w2.dot(hiddenAct)+self.b2)))
            if pred>bestScore:
                move = m
                bestScore = pred
        return move

import submission
