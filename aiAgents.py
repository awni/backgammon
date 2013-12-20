import agent
import numpy as np

def extractFeatures(state):
    game,player = state
    features = []
    for p in game.players:
        for col in game.grid:
            feats = [0.]*4
            if len(col)>0 and col[0]==p:
                for i in xrange(len(col)):
                    feats[min(i,3)] += 1
                feats[-1] = feats[-1]/2.
            features += feats
        features.append(float(len(game.barPieces[p]))/2.)
        features.append(float(len(game.offPieces[p]))/game.numPieces[p])
    if player == game.players[0]:
        features += [1.,0.]
    else:
        features += [0.,1.]
    return np.array(features).reshape(-1,1)

class TDAgent(agent.Agent, object):

    def __init__(self, player, weights):
        super(self.__class__, self).__init__(player)
        self.w1,self.w2,self.b1,self.b2 = weights

    def getAction(self, actions, game):
        """
        Return best action according to self.evaluationFunction,
        with no lookahead.
        """
        bestV = 0

        for a in actions:
            ateList = game.takeAction(a,self.player)
            features = extractFeatures((game,game.opponent(self.player)))
            hiddenAct = 1/(1+np.exp(-(self.w1.dot(features)+self.b1)))
            v = 1/(1+np.exp(-(self.w2.dot(hiddenAct)+self.b2)))
            if v>bestV:
                action = a
                bestV = v
            game.undoAction(a,self.player,ateList)

        return action

def nnetEval(state,weights):
    w1,w2,b1,b2 = weights
    features = np.array(extractFeatures(state)).reshape(-1,1)
    hiddenAct = 1/(1+np.exp(-(w1.dot(features)+b1)))
    v = 1/(1+np.exp(-(w2.dot(hiddenAct)+b2)))
    return v

class ExpectiMiniMaxAgent(agent.Agent, object):

    def miniMaxNode(self,game,player,roll,depth):
        actions = game.getActions(roll,player,nodups=True)
        rollScores = []

        if player==self.player:
            scoreFn = max
        else:
            scoreFn = min
            depth -= 1

        if not actions:
            return self.expectiNode(game,game.opponent(player),depth)
        for a in actions:
            ateList = game.takeAction(a,player)
            rollScores.append(self.expectiNode(game,game.opponent(player),depth))
            game.undoAction(a,player,ateList)

        return scoreFn(rollScores)

    def expectiNode(self,game,player,depth):
        if depth==0:
            return self.evaluationFunction((game,player),self.evaluationArgs)

        total = 0
        for i in range(1,game.die+1):
            for j in range(i+1,game.die+1):
                score = self.miniMaxNode(game,player,(i,j),depth)
                if i==j:
                    total += score
                else:
                    total += 2*score
            
        return total/float(game.die**2)

    def getAction(self, actions, game):
        depth = 1
        if len(actions)>100:
            depth = 0
        outcomes = []
        for a in actions:
            ateList = game.takeAction(a,self.player)
            score = self.expectiNode(game,game.opponent(self.player),depth)
            game.undoAction(a,self.player,ateList)
            outcomes.append((score, a))
        action = max(outcomes)[1]
        return action


    def __init__(self, player, evalFn, evalArgs=None):
        super(self.__class__, self).__init__(player)
        self.evaluationFunction = evalFn
        self.evaluationArgs = evalArgs

