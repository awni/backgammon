"""
Defines a Backgammon Game object.

Methods and instance variables of a Game object you may find 
useful include:

game.clone() - returns a copy of the current game.

game.takeAction(action,player) - takes the action for the 
player.

game.getActions(roll,player) - returns the set of legal
actions for a given roll and player.

game.die - the number of sides on the die.

game.opponent(player) - returns the opponent of the given player.

game.grid - 2-D array (list of lists) with current piece placement 
on board. For example game.grid[0][3] = 'x'

game.barPieces - dictionary with key as playe and value a
list of pieces on the bar for that player. Recall on the bar
means the piece was "clobbered" by the opponent. In our simplified
backgammon these pieces can't return to play.

game.offPieces - dictionary with key as playe and value a
list of pieces successfully taken of the board by the player.

game.numPieces - dictionary with key as player and value
number of total pieces for that player.

game.players - list of players 1 and 2 in order

To see what's available on a game object you can try running this 
in the python shell:

import game
g = game.Game(game.LAYOUT)
dir(g)
"""
import os
LAYOUT = "0-1-o,3-2-x,5-2-o,8-2-o,7-2-x,10-2-x,12-2-o,15-1-x"
#LAYOUT="3-3-x,5-3-o,7-2-x,8-2-o,9-1-x,12-2-o,14-1-x"
NUMCOLS = 16
QUAD = 4
OFF = 'off'

class Game:

    def __init__(self,layout=None,grid=None,offPieces=None,
                 barPieces=None,numPieces=None,gPlayers=None):
        """
        Define a new game object
        """
        self.die = QUAD
        self.layout = layout
        if grid:
            import copy
            self.grid = copy.deepcopy(grid)
            self.offPieces = copy.deepcopy(offPieces)
            self.barPieces = copy.deepcopy(barPieces)
            self.numPieces = copy.deepcopy(numPieces)
            self.players = gPlayers
            return
        self.players = Game.TOKENS
        self.grid = [[] for _ in range(NUMCOLS)]
        self.offPieces = {}
        self.barPieces = {}
        self.numPieces = {}
        for t in self.players:
            self.barPieces[t] = []
            self.offPieces[t] = []
            self.numPieces[t] = 0

    TOKENS = ['o','x']
            
    def clone(self):
        """
        Return an exact copy of the game. Changes can be made
        to the cloned version without affecting the original.
        """
        return Game(None,self.grid,self.offPieces,
                    self.barPieces,self.numPieces,self.players)
    
    def takeAction(self,action,token):
        """
        Makes given move for player, assumes move is valid, 
        will remove pieces from play
        """
        for s,e in action:
            piece = self.grid[s].pop()
            if e==OFF:
                self.offPieces[token].append(piece)
                continue
            if len(self.grid[e])>0 and self.grid[e][0] != token:
                bar_piece = self.grid[e].pop()
                self.barPieces[bar_piece].append(bar_piece)
            self.grid[e].append(piece)

    def getActions(self,roll,token):
        """
        Get set of all possible move tuples
        """
        moves = set()

        r1,r2 = roll
        if token == self.players[1]:
            r1,r2 = -r1,-r2

        rolls = [(r1,r2),(r2,r1)]
        offboarding = self.can_offboard(token)
        for r1,r2 in rolls:
            for i in range(len(self.grid)):
                if self.is_valid_move(i,i+r1,token):
                    move1 = (i,i+r1)
                    piece = self.grid[i].pop()
                    bar_piece = None
                    if len(self.grid[i+r1])==1 and self.grid[i+r1][-1]!=token:
                        bar_piece = self.grid[i+r1].pop()
                    self.grid[i+r1].append(piece)
                    self.get_second_move(token,r2,moves,move1)
                    self.grid[i+r1].pop()
                    self.grid[i].append(piece)
                    if bar_piece:
                        self.grid[i+r1].append(bar_piece)

                if offboarding and self.remove_piece(token,i,r1):
                    move1 = (i,OFF)
                    piece = self.grid[i].pop()
                    self.offPieces[token].append(piece)
                    self.get_second_move(token,r2,moves,move1,offboarding)
                    if len(self.offPieces[token])+len(self.barPieces[token])==self.numPieces[token]:
                        moves.add((move1,))
                    self.offPieces[token].pop()
                    self.grid[i].append(piece)

        # has no moves, try moving only one piece
        if not moves:
            for i in range(len(self.grid)):
                for r in rolls[0]:
                    if self.is_valid_move(i,i+r,token):
                        move1 = (i,i+r)
                        moves.add((move1,))

        return moves

    def opponent(self,token):
        """
        Retrieve opponent players token for a given players token.
        """
        for t in self.players:
            if t!= token: return t

    def isWon(self,player):
        """
        If game is over and player won, return True, else return False
        """
        return self.is_over() and player==self.players[self.winner()]

    def isLost(self,player):
        """
        If game is over and player lost, return True, else return False
        """
        return self.is_over() and player!=self.players[self.winner()]


    def reverse(self):
        """
        Reverses a game allowing it to be seen by the opponent
        from the same perspective
        """
        self.grid.reverse()
        for col in self.grid:
            for i in range(len(col)):
                if col[i]=='x':
                    col[i]='o'
                else:
                    col[i]='x'
        oP = self.barPieces['o']
        xP = self.barPieces['x']
        self.barPieces['o'] = ['o' for _ in xP]
        self.barPieces['x'] = ['x' for _ in oP]
        oP = self.offPieces['o']
        xP = self.offPieces['x']
        self.offPieces['o'] = ['o' for _ in xP]
        self.offPieces['x'] = ['x' for _ in oP]
                  
        #self.players.reverse()

    def new_game(self):
        """
        Resets game to original layout.
        """
        for col in self.layout.split(','):
            loc,num,token = col.split('-')
            self.grid[int(loc)] = [token for _ in range(int(num))]
        for col in self.grid:
            for piece in col:
                self.numPieces[piece] += 1

    def winner(self):
        """
        Get winner.  TODO modify to change to token
        """
        if len(self.offPieces[self.players[0]]) > len(self.offPieces[self.players[1]]):
            return 0
        elif len(self.offPieces[self.players[0]]) < len(self.offPieces[self.players[1]]):
            return 1
        else:
            if len(self.barPieces[self.players[1]]) <= len(self.barPieces[self.players[0]]):
                return 1
            else:
                return 0

    def is_over(self):
        """
        Checks if the game is over.
        """
        for t in self.players:
            if len(self.offPieces[t])+len(self.barPieces[t])==self.numPieces[t]:
                return True
         
        return False

#### NO FUNCTIONS BELOW HERE SHOULD BE OF INTEREST ###
#### WARNING UNCOMMENTED CODE ###

    def get_second_move(self,token,r2,moves,move1,offboarding=None):
        if not offboarding:
            offboarding = self.can_offboard(token)
        for j in range(len(self.grid)):
            if offboarding and self.remove_piece(token,j,r2):
                move2 = (j,OFF)
                moves.add((move1,move2))
                
            if self.is_valid_move(j,j+r2,token):
                move2 = (j,j+r2)
                moves.add((move1,move2))

    def can_offboard(self,token):
        if token==self.players[1]:
            start=0
            end=self.die
        else:
            start=len(self.grid)-self.die
            end=len(self.grid)

        count = 0
        for i in range(start,end):
            if len(self.grid[i])>0 and self.grid[i][0]==token:
                count += len(self.grid[i])
        if count+len(self.offPieces[token])+len(self.barPieces[token]) == self.numPieces[token]:
            return True
        return False

    def remove_piece(self,token,start,r):
        if token==self.players[0] and start < len(self.grid)-self.die:
            return False
        if token==self.players[1] and start >= self.die:
            return False
        if len(self.grid[start]) == 0 or self.grid[start][0] != token:
            return False

        if token==self.players[1]:
            if start+r==-1:
                return True
            if start+r<-1:
                for i in range(start+1,self.die):
                    if len(self.grid[i]) != 0 and self.grid[i][0]==self.players[1]:
                        return False
                return True
        if token==self.players[0]:
            if start+r == len(self.grid):
                return True
            if start+r > len(self.grid):
                for i in range(start-1,len(self.grid)-self.die-1,-1):
                    if len(self.grid[i]) != 0 and self.grid[i][0]==self.players[0]:
                        return False
                return True
        return False

    def is_valid_move(self,start,end,token):
        if len(self.grid[start]) > 0 and self.grid[start][0] == token:
            if end < 0 or end >= len(self.grid):
                return False
            if len(self.grid[end]) <= 1:
                return True
            if len(self.grid[end])>1 and self.grid[end][-1] == token:
                return True
        return False


    def draw_col(self,i,col):
        print "|",
        if i==-2:
            if col<10:
                print "",
            print str(col),
        elif i==-1:
            print "--",
        elif len(self.grid[col])>i:
            print " "+self.grid[col][i],
        else:
            print "  ",

    def draw(self):
        os.system('clear')
        largest = max([len(self.grid[i]) for i in range(len(self.grid)/2,len(self.grid))])
        for i in range(-2,largest):
            for col in range(len(self.grid)/2,len(self.grid)):
                self.draw_col(i,col)
            print "|"
        print
        print
        largest = max([len(self.grid[i]) for i in range(len(self.grid)/2)])
        for i in range(largest-1,-3,-1):
            for col in range(len(self.grid)/2-1,-1,-1):
                self.draw_col(i,col)
            print "|"
        for t in self.players:
            print "<Player %s>  Off Board : "%(t),
            for piece in self.offPieces[t]:
                print t+'',
            print "   Bar : ",
            for piece in self.barPieces[t]:
                print t+'',
            print

if __name__=='__main__':
    g = Game(LAYOUT)
    g.new_game()
    g.draw()
