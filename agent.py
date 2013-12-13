import random
import game as gamemod
import numpy as np
import pygame
from pygame.locals import *
import copy

OFF = gamemod.OFF
ON = gamemod.ON

class Agent:
    def __init__(self,player):
        self.player = player
    
    def getAction(self,moves,game=None):
        raise NotImplementedError("Override me")

class RandomAgent(Agent):
    def getAction(self,moves,game=None):
        if moves:
            return random.choice(list(moves))
        return None

class HumanAgent(Agent):

    def getAction(self,moves,game=None):
        loc = None
        movesLeft = copy.deepcopy(moves)
        tmpg = game.clone()
        pmove = []
        while True:
            # if no more moves we break
            if not movesLeft:
                break

            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONUP:
                    pos = pygame.mouse.get_pos()
                    if loc is not None:
                        # check to see if we can move the piece
                        newLoc = game.gridLocFromPos(pos,self.player)
                        if newLoc is not None:
                            move = (loc,newLoc)
                            moveLegit = False
                            newMoves = set()
                            for m in list(movesLeft):
                                if m[0]==move:
                                    moveLegit = True
                                    if m[1:]:
                                        newMoves.add(m[1:])
                            # if the move is legit we move it
                            if moveLegit:
                                pmove.append(move)
                                game.takeAction((move,),self.player)
                                game.draw()
                                movesLeft = newMoves
                                loc = None
                            else:
                                loc = newLoc
                    else:
                        # get a location to move
                        loc = game.gridLocFromPos(pos,self.player) # TODO implement this

    def getActionCommandLine(self,moves,game=None):
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
                mv2 = raw_input("Please enter a second move (enter to skip): ")
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
            if start != ON:
                start = int(start)
            if end != OFF:
                end = int(end)
            return (start,end)
        except:
            return False
