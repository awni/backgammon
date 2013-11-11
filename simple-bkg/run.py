import time
import game
import agent, random, submission

def train(numGames=2000):
    alpha = 1e-1
    numFeats = game.NUMCOLS*2*3+7
    evalFn = submission.logLinearEvaluation
    w = [random.gauss(0,1e-2) for _ in range(numFeats)]
    w[-1] = 0

    for it in xrange(numGames):

        g = game.Game(game.LAYOUT)
        players = [submission.ReflexAgent(g.players[0],evalFn,w), 
                   submission.ReflexAgent(g.players[1],evalFn,w)]

        g.new_game()
        playernum = random.randint(0,1)
        state = (g.clone(),g.players[playernum])
        over = False
        while not over:
            if playernum:
                g.reverse()
            turn(players[playernum],g)
            if playernum:
                g.reverse()
            playernum = (playernum+1)%2
            nextState = (g.clone(),g.players[playernum])
            w = submission.TDUpdate(state,nextState,0,w,alpha)
            state = nextState
            for p in players: p.setWeights(w)
            over = g.is_over()

        winner = g.winner()

        if it%100 == 0:
            print "Game : %d/%d"%(it,numGames)

        # flip outcome for training
        winner = 1.0-winner
        w = submission.TDUpdate(state,None,winner,w,alpha)

    # save weights
    fid = open("weights.bin",'w')
    import pickle
    pickle.dump(w,fid)
    fid.close()
    return w

def test(players,numGames=100,draw=False):
    winners = [0,0]
    for _ in xrange(numGames):
        g = game.Game(game.LAYOUT)
        winner = run_game(players,g,draw)
        print "The winner is : Player %s"%players[winner].player
        winners[winner]+=1
    print "Summary:"
    print "Player %s : %d/%d"%(players[0].player,winners[0],sum(winners))
    print "Player %s : %d/%d"%(players[1].player,winners[1],sum(winners))

def run_game(players,g,draw=False):
    g.new_game()
    playernum = random.randint(0,1)
    over = False
    while not over:
        if draw:
            g.draw()
            time.sleep(1.5)
        playernum = (playernum+1)%2
        if playernum:
            g.reverse()
        turn(players[playernum],g,draw)
        if playernum:
            g.reverse()
        over = g.is_over()
        if draw:
            time.sleep(1.5)

    return g.winner()

def turn(player,g,draw=False):
    roll = roll_dice(g)
    if draw:
        print "Player %s rolled <%d,%d>."%(player.player,roll[0],roll[1])
    moves = g.getActions(roll,g.players[0])
    if moves:
        move = player.getAction(moves,g)
    else:
        move = None
    if move:
        g.takeAction(move,g.players[0])

def roll_dice(g):
    return (random.randint(1,g.die), random.randint(1,g.die))

def load_weights(weights):
    if weights is None:
        try:
            import pickle
            weights = pickle.load(open('weights.bin','r'))
        except IOError:
            print "You need to train the weights to use the better evaluation function"
    return weights

def main(args=None):
    from optparse import OptionParser
    usage = "usage: %prog [options]"
    parser = OptionParser(usage=usage)
    parser.add_option("-t","--train", dest="train",action="store_true",
                      default=False,help="Train TD Player")
    parser.add_option("-d","--draw",dest="draw",action="store_true",default=False,
                      help="Draw game")
    parser.add_option("-n","--num",dest="numgames",default=1,help="Num games to play")
    parser.add_option("-p","--player1",dest="player1",
                      default="random",help="Choose type of first player")
    parser.add_option("-e","--eval",dest="eval",action="store_true",default=False,
                        help="Play with the better eval function for player")

    (opts,args) = parser.parse_args(args)    

    weights = None
    if opts.train:
        weights = train()
        
    if opts.eval:
        weights = load_weights(weights)
        evalFn = submission.logLinearEvaluation
        evalArgs = weights
    else:
        evalFn = submission.simpleEvaluation
        evalArgs = None
        
    p1 = None
    if opts.player1 == 'random':
        p1 = agent.RandomAgent(game.Game.TOKENS[0])
    elif opts.player1 == 'reflex':
        p1 = submission.ReflexAgent(game.Game.TOKENS[0],evalFn,evalArgs)
    elif opts.player1 == 'expectimax':
        p1 = submission.ExpectimaxAgent(game.Game.TOKENS[0],evalFn,evalArgs)
    elif opts.player1 == 'human':
        p1 = agent.HumanAgent(game.Game.TOKENS[0])

    p2 = agent.RandomAgent(game.Game.TOKENS[1])

    if p1 is None:
        print "Please specify legitimate player"
        import sys
        sys.exit(1)

    test([p1,p2],numGames=int(opts.numgames),draw=opts.draw)

if __name__=="__main__":
    main()
