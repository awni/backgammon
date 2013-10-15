
import game, player, random, submission
import numpy as np

colors = ['w','b']

def train():
    numFeats = 196
    numHidden = 20
    maxIter = 1
    weights = [np.random.randn(numHidden,numFeats),np.random.randn(1,numHidden),np.zeros((numHidden,1)),np.zeros(1)]
    weightsOpp = []
    alpha = 1e-2

    for _ in range(maxIter):
        for w in weights:
            weightsOpp.append(w+1e-3*np.random.standard_normal(w.shape))
        
        players = [submission.NNPlayer(colors[0],0,weights), 
                   submission.NNPlayer(colors[1],1,weightsOpp)]

        winner = run_game(players)
        
        #update if we lose
        print "Winner is %d"%(winner+1)
        if winner==1:
            for w,wopp in zip(weights,weightsOpp):
                w = (1-alpha)*w + alpha*wopp

def run_game(players):
    import time
    g = game.Game(game.layout)
    g.new_game()
    
    playernum = -1
    over = False
    while not over:
        playernum = (playernum+1)%2
        if playernum:
            g.reverse()
        turn(players[playernum],g)
        if playernum:
            g.reverse()
        over = g.is_over()
        #g.draw()
        #time.sleep(1)
    
    return players[playernum].num

def turn(player,g):
    roll = roll_dice()
    moves = g.get_moves(roll,player.color)
    move = player.take_turn(moves,g)
    if move:
        g.take_turn(move,player.color)

def roll_dice():
    return (random.randint(1,6), random.randint(1,6))

if __name__=="__main__":
    train()
