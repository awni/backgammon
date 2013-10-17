
#layout = "0-2-o,5-5-x,7-3-x,11-5-o,12-5-x,16-3-o,18-5-o,23-2-x"
#layout = "0-2-o,4-2-x,6-2-x,9-2-o,10-2-x,13-2-o,15-2-o,19-2-x"
layout = "0-1-o,3-2-x,5-2-o,8-2-o,7-2-x,10-2-x,12-2-o,15-1-x"
#layout = "0-6-x,1-1-x,14-2-o,15-4-o"

num_cols = 16
quad = 4
OFF = 'off'
ON = 'on'

import os

class Game:

    def __init__(self,layout=None,grid=None,out_pieces=None,
                 bar_pieces=None,numpieces=None):
        """
        Define a new game object
        """
        self.layout = layout
        self.colors = ['o','x']
        if grid:
            import copy
            self.grid = copy.deepcopy(grid)
            self.out_pieces = copy.deepcopy(out_pieces)
            self.bar_pieces = copy.deepcopy(bar_pieces)
            self.numpieces = copy.deepcopy(numpieces)
            return
        self.grid = [[] for _ in range(num_cols)]
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
        return Game(None,self.grid,self.out_pieces,
                    self.bar_pieces,self.numpieces)

    def new_game(self):
        for col in self.layout.split(','):
            loc,num,color = col.split('-')
            self.grid[int(loc)] = [color for _ in range(int(num))]
        for col in self.grid:
            for piece in col:
                self.numpieces[piece] += 1
        

    def get_moves(self,roll,color):
        """
        Get set of all possible move tuples
        """
        moves = set()

        r1,r2 = roll
        if color == self.colors[1]:
            r1,r2 = -r1,-r2

       #if self.bar_pieces[color]:
         #self.onboard_piece(moves,color,r1,r2)
         #self.onboard_piece(moves,color,r2,r1)
         #return moves
        
        offboarding = self.can_offboard(color)
        for i in range(num_cols):
            if self.is_valid_move(i,i+r1,color):
                move1 = (i,i+r1)
                piece = self.grid[i].pop()
                bar_piece = None
                if len(self.grid[i+r1])==1 and self.grid[i+r1][-1]!=color:
                    bar_piece = self.grid[i+r1].pop()
                self.grid[i+r1].append(piece)
                self.get_second_move(color,r2,moves,move1)
                self.grid[i+r1].pop()
                self.grid[i].append(piece)
                if bar_piece:
                    self.grid[i+r1].append(bar_piece)

            if offboarding and self.remove_piece(color,i,r1):
                move1 = (i,OFF)
                piece = self.grid[i].pop()
                self.out_pieces[color].append(piece)
                self.get_second_move(color,r2,moves,move1,offboarding)
                if len(self.out_pieces[color])+len(self.bar_pieces[color])==self.numpieces[color]:
                    moves.add((move1,))
                self.out_pieces[color].pop()
                self.grid[i].append(piece)

        # has no moves, try moving only one piece
        if not moves:
            for i in range(num_cols):
                for r in [r1,r2]:
                    if self.is_valid_move(i,i+r,color):
                        move1 = (i,i+r)
                        moves.add((move1,))

        return moves

    def get_second_move(self,color,r2,moves,move1,offboarding=None):
        if not offboarding:
            offboarding = self.can_offboard(color)
        for j in range(num_cols):
            if offboarding and self.remove_piece(color,j,r2):
                move2 = (j,OFF)
                moves.add((move1,move2))
                
            if self.is_valid_move(j,j+r2,color):
                move2 = (j,j+r2)
                moves.add((move1,move2))

    def onboard_piece(self,moves,color,r1,r2):
        start = -1
        if color==self.colors[1]:
            start = num_cols
        piece = self.bar_pieces[color].pop()
        if len(self.grid[start+r1])<=1 or self.grid[start+r1][0]==color:
            move1 = (ON,start+r1)
            self.grid[start+r1].append(piece)
            if self.bar_pieces[color]:
                if len(self.grid[start+r2])<=1 or self.grid[start+r2][0]==color:
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
            end=quad
        else:
            start=num_cols-quad
            end=num_cols

        count = 0
        for i in range(start,end):
            if len(self.grid[i])>0 and self.grid[i][0]==color:
                count += len(self.grid[i])
        if count+len(self.out_pieces[color])+len(self.bar_pieces[color]) == self.numpieces[color]:
            return True
        return False


    def remove_piece(self,color,start,r):
        if color==self.colors[0] and start < num_cols-quad:
            return False
        if color==self.colors[1] and start >= quad:
            return False
        if len(self.grid[start]) == 0 or self.grid[start][0] != color:
            return False

        if color==self.colors[1]:
            if start+r==-1:
                return True
            if start+r<-1:
                for i in range(start+1,quad):
                    if len(self.grid[i]) != 0 and self.grid[i][0]==self.colors[1]:
                        return False
                return True
        if color==self.colors[0]:
            if start+r == num_cols:
                return True
            if start+r > num_cols:
                for i in range(start-1,num_cols-quad-1,-1):
                    if len(self.grid[i]) != 0 and self.grid[i][0]==self.colors[0]:
                        return False
                return True
        return False

    def is_valid_move(self,start,end,color):
        if len(self.grid[start]) > 0 and self.grid[start][0] == color:
            if end < 0 or end >= num_cols:
                return False
            if len(self.grid[end]) <= 1:
                return True
            if len(self.grid[end])>1 and self.grid[end][-1] == color:
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
            if len(self.grid[e])>0 and self.grid[e][0] != color:
                bar_piece = self.grid[e].pop()
                self.bar_pieces[bar_piece].append(bar_piece)
            self.grid[e].append(piece)

    def is_over(self):
        """
        Checks if the game is over.
        """
        for c in self.colors:
            if len(self.out_pieces[c])+len(self.bar_pieces[c])==self.numpieces[c]:
                return True
         
        return False

    def draw(self):
        os.system('clear')
        largest = max([len(self.grid[i]) for i in range(num_cols/2,num_cols)])
        for i in range(-2,largest):
            for col in range(num_cols/2,num_cols):
                print "|",
                if i==-2:
                    print str(col),
                elif i==-1:
                    print "--",
                elif len(self.grid[col])>i:
                    print " "+self.grid[col][i],
                else:
                    print "  ",
            print "|"
        print
        print
        largest = max([len(self.grid[i]) for i in range(num_cols/2)])
        for i in range(largest-1,-3,-1):
            for col in range(num_cols/2-1,-1,-1):
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
            print "|"
        pnum = 0
        for c in self.colors:
            print "<Player %d - %s>  Off Board : "%(pnum,c),
            for piece in self.out_pieces[c]:
                print c+'',
            print "   Bar : ",
            for piece in self.bar_pieces[c]:
                print c+'',
            print
            pnum+=1

if __name__=='__main__':
    g = Game(layout)
    g.new_game()
    g.draw()
