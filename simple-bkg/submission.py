import agent

# BEGIN_HIDE
import numpy as np
# END_HIDE

############################################################
# Problem 1a

def simpleEvaluation(state, evalArgs=None):
    """
    Evaluates the current game state with a simple heuristic.

    @param state : Tuple of (game,player), the game is
    a game object (see game.py for details, and player in
    {'o','x'} designates whose turn it is.

    @returns V : (scalar) evaluation of current game state
    """
    # BEGIN_SOLUTION
    game,player = state
    numHome = 0
    for c in range(12,16):
        col = game.grid[c]
        if len(col)>=1 and col[0]==player:
            numHome += len(col)
    V = 10*len(game.offPieces[player])
    V += numHome
    V -= .1*len(game.barPieces[player])
    # END_SOLUTION
    return V

############################################################
# Problem 1b

# Reflex Agent evaluates only the current game state and returns
# the best action.
class ReflexAgent(agent.Agent, object):

    def __init__(self, player, evalFunction, evalArgs=None):
        super(self.__class__, self).__init__(player)
        self.evaluationFunction = evalFunction
        self.evaluationArgs = evalArgs

    def getAction(self, actions, game):
        """
        Return best action according to self.evaluationFunction,
        with no lookahead.

        @param actions : A set() of possible legal actions for a given roll,
        player and game state.
        @param game : game object (see game.py for details).

        Methods and attributes that may come in handy include:

        self.player - the player this agent represents

        game.clone() - returns a copy of the current game

        game.takeAction(action, player) - takes the action for the
        player with the given player.

        @returns action : Best action according to
        self.evaluationFunction from set of actions.  If there are
        several best, pick the one with the lexicographically largest
        action.
        """
        # - Call the evaluation function using the instance attribute
        #
        #     self.evaluationFunction(state, self.evaluationArgs)
        #
        # - state is a pair: (game, player)
        # - self.evaluationArgs will be the weights when we are using
        #   a linear evaluation function.  For the simple evaluation
        #   this will be None.
        # BEGIN_SOLUTION
        def score(g, a):
            g = g.clone()
            g.takeAction(a, self.player)
            return self.evaluationFunction((g, self.player), self.evaluationArgs)
        outcomes = [(score(game, a), a) for a in actions]
        action = max(outcomes)[1]
        # END_SOLUTION
        return action

    def setWeights(self, w):
        """
        Updates weights of reflex agent.  Used for training.
        """
        self.evaluationArgs = w

############################################################
# Problem 1c

class ExpectimaxAgent(agent.Agent, object):

    def getAction(self, actions, game):
        """
        Return best action according to self.evaluationFunction,
        with 2-ply lookahead.

        @param actions : A set() of possible legal actions for a given roll,
        player and game state.
        @param game : game object (see game.py for details).

        Methods and instance variables that may come in handy include:

        game.getActions(roll, player) - returns the set of legal actions for
        a given roll and player.

        game.clone() - returns a copy of the current game

        game.takeAction(action, player) - takes the action for the
        player and CHANGES the game state. You probably want to use
        game.clone() to copy the game first.

        game.die - the number of sides on the die

        game.opponent(player) - returns the opponent of the given player

        @returns action : Best action according to
        self.evaluationFunction from set of actions.  If there are
        several best, pick the one with the lexicographically largest
        action.

        """
        # - Call the evaluation function using the instance attribute
        #
        #     self.evaluationFunction(state, self.evaluationArgs)
        #
        # - state is a pair: (game, player)
        # - self.evaluationArgs will be the weights when we are using
        #   a linear evaluation function.  For the simple evaluation
        #   this will be None.

        def allDiceRolls(game):
            # Helper function to return all possible dice rolls for a game object
            return [(i, j) for i in range(1, game.die + 1) for j in range(1, game.die + 1)]

        # BEGIN_SOLUTION
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
        # END_SOLUTION
        return action


    def __init__(self, player, evalFn, evalArgs=None):
        super(self.__class__, self).__init__(player)
        self.evaluationFunction = evalFn
        self.evaluationArgs = evalArgs

############################################################
# Problem 2a


def extractFeatures(state):
    """
    @param state : Tuple of (game, player), the game is
    a game object (see game.py for details, and player in
    {'o', 'x'} designates whose turn it is.

    @returns features : List of real valued features for given state.

    Methods and instance variables that may come in handy include:

    game.getActions(roll, player) - returns the set of legal actions for
    a given roll and player.

    game.clone() - returns a copy of the current game

    game.grid - 2-D array (list of lists) with current piece placement on
    board. For example game.grid[0][3] = 'x'

    game.barPieces - dictionary with key as player and value a list of
    pieces on the bar for that player. Recall on the bar means the piece was
    "clobbered" by the opponent. In our simplified backgammon these pieces
    can't return to play.

    game.offPieces - dictionary with key as player and value a list
    of pieces successfully taken of the board by the player.

    game.numPieces - dictionary with key as player and value number
    of total pieces for that player.

    game.players - list of players 1 and 2 in order
    """
    # BEGIN_SOLUTION
    def extractColumnFeatures(column,player):
        feats = [0.]*3
        if len(column)>0 and column[0]==player:
            for i in range(len(column)):
                feats[min(i,2)] += 1
        return feats

    game,player = state
    features = []
    for p in game.players:
        for col in game.grid:
            feats = extractColumnFeatures(col,p)
            features += feats
        features.append(float(len(game.barPieces[p])))
        features.append(float(len(game.offPieces[p]))/game.numPieces[p])
    if player == game.players[0]:
        features += [1.,0.]
    else:
        features += [0.,1.]
    features += [1.0] # bias
    # END_SOLUTION
    return features


############################################################
# Problem 2b

def logLinearEvaluation(state, w):
    """
    Evaluate the current state using the log-linear evaluation
    function.

    @param state : Tuple of (game, player), the game is
    a game object (see game.py for details, and player in
    {'o', 'x'} designates whose turn it is.

    @param w : List of feature weights.

    @returns V : Evaluation of current game state.
    """
    # BEGIN_SOLUTION
    w = np.array(w).reshape(-1,1)
    features = np.array(extractFeatures(state)).reshape(-1,1)
    V = 1/(1+np.exp(-w.T.dot(features)))
    V = V.squeeze().tolist()
    # END_SOLUTION
    return V

############################################################
# Problem 2c

def TDUpdate(state, nextState, reward, w, eta):
    """
    Given two sequential game states, updates the weights
    with a step size of eta, using the Temporal Difference learning
    algorithm.

    @param state : Tuple of game state (game object, player).
    @param nextState : Tuple of game state (game object, player),
    note if the game is over this will be None. In this case, 
    the next value for the TD update will be 0.
    @param reward : The reward is 1 if the game is over and your
    player won, 0 otherwise.
    @param w : List of feature weights.
    @param eta : Step size for learning.

    @returns w : Updated weights.
    """
    # BEGIN_SOLUTION
    w = np.array(w).reshape(-1,1)
    features = np.array(extractFeatures(state)).reshape(-1,1)
    v = 1/(1+np.exp(-w.T.dot(features)))
    grad = v*(1-v)*features

    if nextState is None:
        nextV = 0
    else:
        features = np.array(extractFeatures(nextState)).reshape(-1,1)
        nextV = 1/(1+np.exp(-w.T.dot(features)))

    w += eta*(reward+nextV-v)*grad
    w = w.squeeze().tolist()
    # END_SOLUTION
    return w
