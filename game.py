import os
LAYOUT = "0-2-o,5-5-x,7-3-x,11-5-o,12-5-x,16-3-o,18-5-o,23-2-x"

NUMCOLS = 24
QUAD = 6
OFF = 'off'
ON = 'on'

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
            if s==ON:
                piece = self.barPieces[token].pop()
            else:
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

        if self.barPieces[token]:
            self.onboard_piece(moves,token,r1,r2)
            self.onboard_piece(moves,token,r2,r1)
            return moves

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
        self.players.reverse()

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
        Get winner.
        """
        return self.offPieces[self.players[0]]==self.numPieces[self.players[0]]

    def is_over(self):
        """
        Checks if the game is over.
        """
        for t in self.players:
            if len(self.offPieces[t])==self.numPieces[t]:
                return True
         
        return False

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
        if count+len(self.offPieces[token]) == self.numPieces[token]:
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

    def onboard_piece(self,moves,player,r1,r2):
        start = -1
        if player==self.players[1]:
            start = NUMCOLS
        piece = self.barPieces[player].pop()
        if len(self.grid[start+r1])<=1 or self.grid[start+r1][0]==player:
            move1 = (ON,start+r1)
            self.grid[start+r1].append(piece)
            if self.barPieces[player]:
                if len(self.grid[start+r2])<=1 or self.grid[start+r2][0]==player:
                    move2 = (ON,start+r2)
                    moves.add((move1,move2))
                else:
                    moves.add((move1,))
            else:
                for j in range(NUMCOLS):
                    if self.is_valid_move(j,j+r2,player):
                        move2 = (j,j+r2)
                        moves.add((move1,move2))
            self.grid[start+r1].pop()
        self.barPieces[player].append(piece)


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
