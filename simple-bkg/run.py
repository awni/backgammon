
import game, player, random, submission
import numpy as np

def train():
    gamma = 0.7
    alpha = .1
    numFeats = game.num_cols*2*3+4
    numHidden = 30
    maxIter = 2000
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
            w = w-alpha*update
    fid = open("weights.npy",'w')
    import pickle
    pickle.dump(weights,fid)
    fid.close()
    return weights

def test(weights,numGames=100):
    winners = [0,0]
    for _ in xrange(numGames):
        g = game.Game(game.layout)
        players = [submission.TDExpectiMaxPlayer(g.colors[0],0,weights), 
                   player.RandomPlayer(g.colors[1],1)]
        winner = run_game(players,g)
        print winner
        winners[winner]+=1
    print winners

def run_game(players,g,draw=False):
    import time
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
        if draw:
            time.sleep(1)
            g.draw()

    if len(g.out_pieces[g.colors[0]]) > len(g.out_pieces[g.colors[1]]):
        return 0
    elif len(g.out_pieces[g.colors[0]]) < len(g.out_pieces[g.colors[1]]):
        return 1
    else:
        if len(g.bar_pieces[g.colors[0]]) > len(g.bar_pieces[g.colors[1]]):
            return 1
        else:
            return 0
            
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
    return (random.randint(1,game.quad), random.randint(1,game.quad))

if __name__=="__main__":
    ## TODO opts parer
    
    weights = train()
    test(weights)


