
layout = "0-2-w,5-5-b,7-3-b,11-5-w,12-5-b,16-3-w,18-5-w,23-2-b"
#layout = "23-0-w,18-2-w,20-2-w,0-2-b,4-1-b,5-1-b,6-1-b,7-1-b,21-1-b"
#layout = "22-1-w,0-2-b,4-1-b,5-1-b,6-1-b,7-1-b,21-1-b"

num_cols = 24
OFF = 'off'
ON = 'on'

import os

class Game:

    def __init__(self,layout=None,grid=None,symbols=None,out_pieces=None,
                 bar_pieces=None,numpieces=None):
        """
        Define a new game object
        """
        self.layout = layout

        if grid:
            import copy
            self.grid = copy.deepcopy(grid)
            self.symbols = symbols
            self.out_pieces = copy.deepcopy(out_pieces)
            self.bar_pieces = copy.deepcopy(bar_pieces)
            self.numpieces = copy.deepcopy(numpieces)
            return
        self.colors = ['w','b']
        self.grid = [[] for _ in range(num_cols)]
        self.symbols = {self.colors[0]:'o',self.colors[1]:'x'}
        self.out_pieces = {}
        self.bar_pieces = {}
        self.numpieces = {}
        for c in self.colors:
            self.bar_pieces[c] = []
            self.out_pieces[c] = []
            self.numpieces[c] = 0

    def reverse(self):
        self.grid.reverse()
        self.colors.reverse()
            
    def clone(self):
        return Game(None,self.grid,self.symbols,self.out_pieces,
                    self.bar_pieces,self.numpieces)

    def new_game(self):
        for col in self.layout.split(','):
            loc,num,color = col.split('-')
            self.grid[int(loc)] = [Piece(int(loc),color,self.symbols[color]) for _ in range(int(num))]
        for col in self.grid:
            for piece in col:
                self.numpieces[piece.color] += 1

    def draw(self):
        os.system('clear')
        largest = max([len(self.grid[i]) for i in range(12,24)])
        for i in range(-2,largest):
            for col in range(12,24):
                print "|",
                if i==-2:
                    print str(col),
                elif i==-1:
                    print "--",
                elif len(self.grid[col])>i:
                    print " "+self.grid[col][i].symbol,
                else:
                    print "  ",
            print "|"
        print
        print
        largest = max([len(self.grid[i]) for i in range(12)])
        for i in range(largest-1,-3,-1):
            for col in range(11,-1,-1):
                print "|",
                if i==-2:
                    if col<10:
                        print "",
                    print str(col),
                elif i==-1:
                    print "--",
                elif len(self.grid[col])>i:
                    print " "+self.grid[col][i].symbol,
                else:
                    print "  ",
            print "|"
        pnum = 1
        for c in self.colors:
            print "<Player %d - %s>  Off Board : "%(pnum,self.symbols[c]),
            for piece in self.out_pieces[c]:
                print piece.symbol+'',
            print "   Bar : ",
            for piece in self.bar_pieces[c]:
                print piece.symbol+'',
            print
            pnum+=1

    def get_moves(self,roll,color):
        """
        Get set of all possible move tuples
        """
        moves = set()

        rolls = [roll]
        if roll[0]!=roll[1]:
            rolls.append((roll[1],roll[0]))
        if color == self.colors[1]:
            newrolls = [(-r1,-r2) for r1,r2 in rolls]
            rolls = newrolls

        if self.bar_pieces[color]:
            self.onboard_piece(moves,color,rolls)
            return moves

        for r1,r2 in rolls:
            for i in range(num_cols):
                if self.is_valid_move(i,i+r1,color):
                    move1 = (i,i+r1)
                    piece = self.grid[i].pop()
                    self.grid[i+r1].append(piece)
                    for j in range(num_cols):
                        if self.can_offboard(color) and self.remove_piece(color,j,r2):
                            move2 = (j,OFF)
                            moves.add((move1,move2))
                            
                        if self.is_valid_move(j,j+r2,color):
                            move2 = (j,j+r2)
                            moves.add((move1,move2))
                    self.grid[i+r1].pop()
                    self.grid[i].append(piece)

        if self.can_offboard(color):
            for r1,r2 in rolls:
                for i in range(num_cols):
                    if self.remove_piece(color,i,r1):
                        piece = self.grid[i].pop()
                        move1 = (i,OFF)
                        for j in range(num_cols):
                            if self.remove_piece(color,j,r2):
                                move2 = (j,OFF)
                                moves.add((move1,move2))
                            if self.is_valid_move(j,j+r2,color):
                                move2 = (j,j+r2)
                                moves.add((move1,move2))
                        if len(self.out_pieces[color])==self.numpieces[color]-1:
                            moves.add((move1,))
                        self.grid[i].append(piece)

        r = sum(rolls[0])
        for i in range(num_cols):
            if self.is_valid_move(i,i+r,color):
                move = (i,i+r)
                moves.add((move,))
            
        
        return moves

    def onboard_piece(self,moves,color,rolls):
        start = -1
        if color==self.colors[1]:
            start = 24
        piece = self.bar_pieces[color].pop()
        for r1,r2 in rolls:
            if len(self.grid[start+r1])==0 or self.grid[start+r1][0].color==color:
                move1 = (ON,start+r1)
                self.grid[start+r1].append(piece)
                if self.bar_pieces[color]:
                    if len(self.grid[start+r2])==0 or self.grid[start+r2][0].color==color:
                        move2 = (ON,start+r2)
                        moves.add((move1,move2))
                    else:
                        moves.add((move1,))
                else:
                    for j in range(num_cols):
                        if self.is_valid_move(j,j+r2,color):
                            move2 = (j,j+r2)
                            moves.add((move1,move2))
                self.grid[start+r1].pop()
        self.bar_pieces[color].append(piece)

    def can_offboard(self,color):
        if color==self.colors[1]:
            start=0
            end=6
        else:
            start=18
            end=24

        count = 0
        for i in range(start,end):
            if len(self.grid[i])>0 and self.grid[i][0].color==color:
                count += len(self.grid[i])
        if count+len(self.out_pieces[color]) == self.numpieces[color]:
            return True
        return False


    def remove_piece(self,color,start,r):
        if color==self.colors[0] and start < 18:
            return False
        if color==self.colors[1] and start > 5:
            return False
        if len(self.grid[start]) == 0 or self.grid[start][0].color != color:
            return False

        if color==self.colors[1]:
            if start+r==-1:
                return True
            if start+r<-1:
                for i in range(start+1,6):
                    if len(self.grid[i]) != 0 and self.grid[i][0].color==self.colors[1]:
                        return False
                return True
        if color==self.colors[0]:
            if start+r == 24:
                return True
            if start+r > 24:
                for i in range(start-1,17,-1):
                    if len(self.grid[i]) != 0 and self.grid[i][0].color==self.colors[0]:
                        return False
                return True
        return False

    def is_valid_move(self,start,end,color):
        if len(self.grid[start]) > 0 and self.grid[start][0].color == color:
            if end < 0 or end > 23:
                return False
            if len(self.grid[end]) == 0:
                return True
            if len(self.grid[end]) == 1:
                return True
            if len(self.grid[end])>1 and self.grid[end][0].color == color:
                return True
        return False

    def take_turn(self,move,color):
        """
        Makes given move for color, assumes move is valid, 
        will remove pieces from play
        """
        for s,e in move:
            if s==ON:
                piece = self.bar_pieces[color].pop()
            else:
                piece = self.grid[s].pop()
            if e==OFF:
                self.out_pieces[color].append(piece)
                continue
            if len(self.grid[e])>0 and self.grid[e][0].color != color:
                bar_piece = self.grid[e].pop()
                bar_piece.onboard = False
                bar_piece.onbar = True
                self.bar_pieces[bar_piece.color].append(bar_piece)
            self.grid[e].append(piece)

    def is_over(self):
        """
        Checks if the game is over and returns True,winner
        or False,None if not over.
        """
        for c in self.colors:
            if len(self.out_pieces[c])==self.numpieces[c]:
                return True

        return False

class Piece:
    def __init__(self,loc,color,symbol):
        """
        Define a piece object
        """
        self.loc = loc
        self.color = color
        self.onboard = True
        self.onbar = False
        self.symbol = symbol

if __name__=='__main__':
    g = Game(layout)
    g.new_game()
    g.draw()



    
