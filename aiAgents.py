import agent
import numpy as np

def extractFeatures(state):

    def extractColumnFeatures(column,player):
        feats = [0.]*4
        if len(column)>0 and column[0]==player:
            for i in range(len(column)):
                feats[min(i,3)] += 1
            feats[-1] = feats[-1]/2.
        return feats

    game,player = state
    features = []
    for p in game.players:
        for col in game.grid:
            feats = extractColumnFeatures(col,p)
            features += feats
        features.append(float(len(game.barPieces[p]))/2.)
        features.append(float(len(game.offPieces[p]))/game.numPieces[p])
    if player == game.players[0]:
        features += [1.,0.]
    else:
        features += [0.,1.]
    features += [1.0] # bias
    return features

class TDAgent(agent.Agent, object):

    def __init__(self, player, weights, gamma=None, update=False):
        super(self.__class__, self).__init__(player)
        self.w1,self.w2,self.b1,self.b2 = weights
        self.gamma = gamma
        self.V = []
        self.grads = []
        self.update = update

    def getAction(self, actions, game):
        """
        Return best action according to self.evaluationFunction,
        with no lookahead.
        """
        bestV = 0
        if self.update:
            feats = np.array(extractFeatures((game,self.player))).reshape(-1,1)
            hiddenAct = 1/(1+np.exp(-(self.w1.dot(feats)+self.b1)))
            v = 1/(1+np.exp(-(self.w2.dot(hiddenAct)+self.b2)))
            self.grads.append(self.backprop(feats,hiddenAct,v))
            self.V.append(v)

        for a in actions:
            tmpGame = game.clone()
            tmpGame.takeAction(a,self.player)
            features = np.array(extractFeatures((tmpGame,game.opponent(self.player)))).reshape(-1,1)
            hiddenAct = 1/(1+np.exp(-(self.w1.dot(features)+self.b1)))
            v = 1/(1+np.exp(-(self.w2.dot(hiddenAct)+self.b2)))
            if v>bestV:
                action = a
                bestFeats = features
                bestAct = hiddenAct.copy()
                bestV = v
        if self.update:
            self.grads.append(self.backprop(bestFeats,bestAct,bestV))
            self.V.append(bestV)

        return action

    def backprop(self,a1,a2,v):
        del2 = v*(1-v)
        del1 = self.w2.T*del2*a2*(1-a2)
        return [del1*a1.T,del2*a2.T,del1,del2]

    def computeUpdate(self,outcome):
        self.V.append(outcome)
        updates = [np.zeros(self.w1.shape),np.zeros(self.w2.shape),
                   np.zeros(self.b1.shape),np.zeros(self.b2.shape)]
        gradsums = [np.zeros(self.w1.shape),np.zeros(self.w2.shape),
                   np.zeros(self.b1.shape),np.zeros(self.b2.shape)]

        for t in range(len(self.V)-1):
            currdiff = self.V[t+1]-self.V[t]
            for update,gradsum,grad in zip(updates,gradsums,self.grads[t]):
                gradsum += self.gamma*gradsum+grad
                update += currdiff*gradsum
        return updates


def nnetEval(state,weights):
    w1,w2,b1,b2 = weights
    features = np.array(extractFeatures(state)).reshape(-1,1)
    hiddenAct = 1/(1+np.exp(-(w1.dot(features)+b1)))
    v = 1/(1+np.exp(-(w2.dot(hiddenAct)+b2)))


class ExpectimaxAgent(agent.Agent, object):

    def getAction(self, actions, game):

        def allDiceRolls(game):
            # Helper function to return all possible dice rolls for a game object
            return [(i, j) for i in range(1, game.die + 1) for j in range(1, game.die + 1)]

        def computeV(game,player):
            total = 0
            for roll in allDiceRolls(game):
                actions = game.getActions(roll,player)
                rollTotal = 0.
                for a in actions:
                    tmpGame = game.clone()
                    tmpGame.takeAction(a,player)
                    rollTotal += self.evaluationFunction((tmpGame,self.player),self.evaluationArgs)
                if actions:
                    total += rollTotal/float(len(actions))
            return total/float(game.die**2)

        outcomes = []
        for a in actions:
            tmpGame = game.clone()
            tmpGame.takeAction(a,self.player)
            score = computeV(tmpGame,game.opponent(self.player))
            outcomes.append((score, a))
        action = max(outcomes)[1]
        return action


    def __init__(self, player, evalFn, evalArgs=None):
        super(self.__class__, self).__init__(player)
        self.evaluationFunction = evalFn
        self.evaluationArgs = evalArgs

class ExpectiMiniMaxAgent(agent.Agent, object):

    def allDiceRolls(game):
        # Helper function to return all possible dice rolls for a game object
        return [(i, j) for i in range(1, game.die + 1) for j in range(1, game.die + 1)]

    def miniMaxNode(game,player,roll,depth):
        actions = game.getActions(roll,player)
        rollScores = []

        if player==self.player:
            scoreFn = max
        else:
            scoreFn = min
            depth -= 1

        if not actions:
            return expectiNode(tmpGame,game.opponent(player),depth)

        for a in actions:
            tmpGame = game.clone()
            tmpGame.takeAction(a,player)
            rollScores.append(expectiNode(tmpGame,game.opponent(player),depth))

        return scoreFn(rollScores)

    def expectiNode(game,player,depth):
        if depth==0:
            return self.evaluationFunction((game,player),self.evaluationArgs)

        total = 0
        for roll in allDiceRolls(game):
            total += miniMaxNode(game,player,roll,depth)

        return total/float(game.die**2)

    def getAction(self, actions, game):
        depth = 1
        outcomes = []
        for a in actions:
            tmpGame = game.clone()
            tmpGame.takeAction(a,self.player)
            score = expectiNode(tmpGame,game.opponent(self.player),depth)
            outcomes.append((score, a))
        action = max(outcomes)[1]
        return action


    def __init__(self, player, evalFn, evalArgs=None):
        super(self.__class__, self).__init__(player)
        self.evaluationFunction = evalFn
        self.evaluationArgs = evalArgs

