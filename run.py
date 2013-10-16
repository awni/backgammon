
import game, player, random, submission
import numpy as np

def train():
    gamma = 0.7
    alpha = 0.1
    numFeats = 196
    numHidden = 40
    maxIter = 1000
    weights = [1e-2*np.random.randn(numHidden,numFeats),1e-2*np.random.randn(1,numHidden),
               np.zeros((numHidden,1)),np.zeros((1,1))]

    for it in xrange(maxIter):

        g = game.Game(game.layout)
        players = [submission.TDPlayer(g.colors[0],0,weights,gamma), 
                   player.NNPlayer(g.colors[1],1,weights)]

        winner = run_game(players,g)
        if it%10 == 0:
            print "iteration : %d"%it
        #update if we lose
        #print "Winner is player %d"%(winner)

        # flip outcome for training
        if winner==0:
            outcome = 1
        else:
            outcome = 0

        updates = players[0].compute_update(outcome)
        for w,update in zip(weights,updates):
            w = w+alpha*update

    return weights

def test(weights,numGames=100):
    winners = [0,0]
    for _ in xrange(numGames):
        g = game.Game(game.layout)
        players = [player.NNPlayer(g.colors[0],0,weights), 
                   player.RandomPlayer(g.colors[1],1)]

        winner = run_game(players,g)
        winners[winner]+=1

    print winners

def run_game(players,g):
#    import time
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
#        g.draw()
#        time.sleep(1)
    
    return players[playernum].num

def turn(player,g):
    roll = roll_dice()
    moves = g.get_moves(roll,player.color)
    if moves:
        move = player.take_turn(moves,g)
    else:
        move = None
    if move:
        g.take_turn(move,player.color)

def roll_dice():
    return (random.randint(1,6), random.randint(1,6))

if __name__=="__main__":
    ## TODO opts parer
    
    weights = train()
    test(weights)


