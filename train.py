import time
import game
import agent, random, aiAgents
import numpy as np
import cPickle as pickle

def saveGames(gameData,fileNum):
    feats = np.hstack(gameData['feats'])
    info = np.vstack([np.array(gameData['winners']), np.array(gameData['length'])]).T
    featId = open('gameFeats.0.%d'%fileNum,'w')
    infoId = open('gameInfo.0.%d'%fileNum,'w')
    feats.astype(np.float32).tofile(featId)
    featId.close()
    info.astype(np.int32).tofile(infoId)
    print info
    infoId.close()

def train(numGames=100000):
    alpha = 1.0
    numFeats = (game.NUMCOLS*6+3)*2
    numHidden = 50
    scales = [np.sqrt(6./(numFeats+numHidden)), np.sqrt(6./(1+numHidden))]
    weights = [scales[0]*np.random.randn(numHidden,numFeats),scales[1]*np.random.randn(1,numHidden),
               np.zeros((numHidden,1)),np.zeros((1,1))]    
    players = [aiAgents.TDAgent(game.Game.TOKENS[0],weights), 
               aiAgents.TDAgent(game.Game.TOKENS[1],weights)]

    gameData = {'winners':[],'length':[],'feats':[]}
    for it in xrange(numGames):
        g = game.Game(game.LAYOUT)
        g.new_game()
        playernum = random.randint(0,1)
        featsP = aiAgents.extractFeatures((g,players[playernum].player))
        if it==500:
	    alpha=.1

        over = False
        nt = 0
        while True:
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
            updateWeights(featsP,featsN,weights,alpha)
            if g.is_over():
                break
	    gameData['feats'].append(featsP)
            nt += 1
            featsP = featsN

        winner = g.winner()
	gameData['winners'].append(winner)
	gameData['length'].append(nt)
	if (it+1)%10000==0:
	    saveGames(gameData,it/10000)
	    gameData = {'winners':[],'length':[],'feats':[]}

        print "Game : %d/%d in %d turns"%(it,numGames,nt)

        updateWeights(featsP,featsN,weights,alpha,w=winner)

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

def updateWeights(featsP,featsN,weights,alpha,w=None):
    # compute vals and grad
    vP,grad = backprop(weights,featsP)
    if w is None:
        vN = backprop(weights,featsN,fpropOnly=True)
    else:
        vN = w

    scale = alpha*(vN-vP)
    for w,g in zip(weights,grad):
        w += scale*g

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

