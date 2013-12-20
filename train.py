import time
import game
import agent, random, aiAgents
import numpy as np
import cPickle as pickle

def train(numGames=100):
    gamma = 0.1
    alpha = 0.1
    numFeats = (game.NUMCOLS*4+3)*2
    numHidden = 50
    scales = [np.sqrt(6./(numFeats+numHidden)), np.sqrt(6./(1+numHidden))]
    weights = [scales[0]*np.random.randn(numHidden,numFeats),scales[1]*np.random.randn(1,numHidden),
               np.zeros((numHidden,1)),np.zeros((1,1))]    
    players = [aiAgents.TDAgent(game.Game.TOKENS[0],weights), 
               aiAgents.TDAgent(game.Game.TOKENS[1],weights)]

    for it in xrange(numGames):
        if it==10:
            gamma = 0.7
        trace = [np.zeros(w.shape) for w in weights]

        g = game.Game(game.LAYOUT)
        g.new_game()
        playernum = random.randint(0,1)
        featsP = aiAgents.extractFeatures((g,players[playernum].player))

        over = False
        while not over:
            roll = (random.randint(1,g.die), random.randint(1,g.die))
            if playernum:
                g.reverse()
            moves = g.getActions(roll,g.players[0],nodups=True)
            if moves:
                move = players[playernum].getAction(moves,g)
            else:
                move = None
            if move:
                g.takeAction(move,g.players[0])
            if playernum:
                g.reverse()
            playernum = (playernum+1)%2
            featsN = aiAgents.extractFeatures((g,players[playernum].player))
            updateWeights(featsP,featsN,weights,trace,alpha,gamma)
            featsP = featsN
            over = g.is_over()

        winner = g.winner()

        print "Game : %d/%d"%(it,numGames)

        # flip outcome for training
        winner = 1.0-winner
        updateWeights(featsP,featsN,weights,trace,alpha,gamma,w=winner)

        if it%100 == 0:
            # save weights
            fid = open("weights.bin",'w')
            pickle.dump(weights,fid)
            fid.close()

    return weights

def backprop(weights,a1,fpropOnly=False):
    w1,w2,b1,b2 = weights

    a2 = 1/(1+np.exp(-(w1.dot(a1)+b1)))
    v = 1/(1+np.exp(-(w2.dot(a2)+b2)))

    if fpropOnly:
        return v

    del2 = v*(1-v)
    del1 = w2.T*del2*a2*(1-a2)
    return v,[del1*a1.T,del2*a2.T,del1,del2]

def updateWeights(featsP,featsN,weights,trace,alpha,gamma,w=None):
    # compute vals and grad
    vP,grad = backprop(weights,featsP)
    if w is None:
        vN = backprop(weights,featsN,fpropOnly=True)
    else:
        vN = w

    for tr,gr in zip(trace,grad):
        tr += gamma*tr+gr
        
    scale = alpha*(vN-vP)
    for w,tr in zip(weights,trace):
        w += scale*tr

def load_weights(weights):
    if weights is None:
        try:
            import pickle
            weights = pickle.load(open('weights.bin','r'))
        except IOError:
            print "You need to train the weights to use the better evaluation function"
    return weights

if __name__=="__main__":
    weights = train()

