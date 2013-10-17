import player
import numpy as np

def featsForColumn(column,color):
    feats = [0.]*3
    if len(column)>0 and column[0]==color:
        for i in range(len(column)):
            feats[min(i,2)] += 1
    feats[-1] = feats[-1]/2.0
    return feats
            
def extractFeatures(game,color):
    """
    @params game: state of backgammon board
    
    @returns features: list of real valued features
    """
    features = []
    for c in game.colors:
        for col in game.grid:
            feats = featsForColumn(col,c)
            features += feats
        features.append(float(len(game.bar_pieces[c]))/2)
        features.append(float(len(game.out_pieces[c]))/game.numpieces[c])
    if color == game.colors[0]:
        features += [1.,0.] # player 0
    else:
        features += [0.,1.]
    return features

def nnEvaluate(game,color,weights,backprop=False):
    w1,w2,b1,b2 = weights
    features = np.array(extractFeatures(game,color)).reshape(-1,1)
    hidden = 1/(1+np.exp(-(w1.dot(features)+b1)))
    v = 1/(1+np.exp(-(w2.dot(hidden)+b2)))
    if backprop:
        del2 = v*(1-v)
        del1 = w2.T*del2*hidden*(1-hidden)
        return v,[del1*features.T,del2*hidden.T,del1,del2]
    return v

def computeUpdate(v,vnext,gamma,grads,traces):
    valdiff = vnext-v
    updates = []
    newTraces = []
    for trace,grad in zip(traces,grads):
        trace = gamma*trace+grad
        update = valdiff*trace
        updates.append(update)
        newTraces.append(trace)
    return updates,newTraces

def simpleEvaluate(game,color,evalArgs=None):
    numSingletons = 0
    for col in game.grid:
        if len(col)==1 and col[0]==color:
            numSingletons += 1

    score = 5.*len(game.out_pieces[color])
    #score += -0.5*len(game.bar_pieces[color]) 
    #score += 0.5*numSingletons
    return score


class ReflexPlayer(player.Player,object):

    def __init__(self,color,num,evalFn,evalArgs=None):
        super(self.__class__,self).__init__(color,num)
        self.evalFn = evalFn
        self.evalArgs = evalArgs

    def take_turn(self,moves,game):
        move = None
        bestVal = float("-inf")
        for m in moves:
            tmpGame = game.clone()
            tmpGame.take_turn(m,self.color)
            val = self.evalFn(tmpGame,self.color,self.evalArgs)
            if val > bestVal:
                bestVal = val
                move = m
        return move

class ExpectiMaxPlayer(player.Player,object):

    def __init__(self,color,num,evalFn,evalArgs=None):
        super(self.__class__,self).__init__(color,num)
        self.evalFn = evalFn
        self.evalArgs = evalArgs

    def take_turn(self,moves,game,depth=1):
        if depth==0:
            return self.evalFn(game,self.color,self.evalArgs)
        move = None
        bestScore = float("-inf")
        for m in moves:
            tmpGame = game.clone()
            tmpGame.take_turn(m,self.color)
            score = self.expecti(tmpGame,depth,game.opponent(self.color))
            if score>bestScore:
                move = m
                bestScore = score
        return move

    def expecti(self,game,depth,color):
        total = 0
        for i in range(1,game.die+1):
            for j in range(i,game.die+1):
                moves = game.get_moves((i,j),color)
                rollTotal = 0.
                for m in moves:
                    tmpGame = game.clone()
                    tmpGame.take_turn(m,color)
                    rollTotal += self.take_turn(None,tmpGame,depth-1)
                if moves:
                    total += rollTotal/float(len(moves))

        return total/(game.die*(game.die+1)/2.)
