
import game, player, random, submission
import numpy as np

def train(maxIter=5000):
    gamma = 0.7
    alpha = 1e-1
    numFeats = game.num_cols*2*3+6
    numHidden = 30
    weights = [1e-2*np.random.randn(numHidden,numFeats),1e-2*np.random.randn(1,numHidden),
               np.zeros((numHidden,1)),np.zeros((1,1))]
    traces = [np.zeros(w.shape) for w in weights]

    for it in xrange(maxIter):

        g = game.Game(game.layout)
        players = [submission.ReflexPlayer(g.colors[0],0,submission.nnEvaluate,weights), 
                   submission.ReflexPlayer(g.colors[1],1,submission.nnEvaluate,weights)]


        g.new_game()
        playernum = random.randint(0,1)
        v,grads = submission.nnEvaluate(g,g.colors[playernum],weights,True)
        over = False
        while not over:
            if playernum:
                g.reverse()
            turn(players[playernum],g)
            if playernum:
                g.reverse()
            playernum = (playernum+1)%2
            vnext,gradsNext = submission.nnEvaluate(g,g.colors[playernum],weights,True)
            updates,traces = submission.computeUpdate(v,vnext,gamma,grads,traces)
            v = vnext
            grads = gradsNext

            for w,update in zip(weights,updates):
                w += alpha*update
            over = g.is_over()

        winner = g.winner()

        if it%10 == 0:
            print "iteration : %d"%it

        # flip outcome for training
        if winner==0:
            outcome = 1.0
        else:
            outcome = 0.0

        updates,traces = submission.computeUpdate(v,outcome,gamma,grads,traces)
        for w,update in zip(weights,updates):
            w += alpha*update

    # save weights
    fid = open("weights.npy",'w')
    import pickle
    pickle.dump(weights,fid)
    fid.close()
    return weights

def test(players,numGames=100,draw=False):
    winners = [0,0]
    for _ in xrange(numGames):
        g = game.Game(game.layout)
        winner = run_game(players,g,draw)
        print "The winner is : Player %d"%winner
        winners[winner]+=1
    print winners

def run_game(players,g,draw=False):
    import time
    g.new_game()
    
    playernum = random.randint(0,1)

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

    return g.winner()

def turn(player,g):
    roll = roll_dice(g)
    moves = g.get_moves(roll,player.color)
    if moves:
        move = player.take_turn(moves,g)
    else:
        move = None
    if move:
        g.take_turn(move,player.color)

def roll_dice(g):
    return (random.randint(1,g.die), random.randint(1,g.die))

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
    parser.add_option("-q","--player2",dest="player2",
                      default="random",help="Choose type of second player")
    parser.add_option("-e","--eval",dest="eval",default="simple",
                        help="Choose eval function for player if relevant")

    (opts,args) = parser.parse_args(args)    

    weights = None
    if opts.train:
        weights = train()
        
    if opts.eval == "nn":
        if not weights:
            try:
                import pickle
                weights = pickle.load(open('weights.npy','r'))
            except IOError:
                print "You need to train weights to use the Neural Net eval function"

        evalFn = submission.nnEvaluate
        evalArgs = weights
    else:
        evalFn = submission.simpleEvaluate
        evalArgs = None
        
    p1 = None
    p2 = None
    if opts.player1 == 'random':
        p1 = player.RandomPlayer(game.colors[0],0)
    elif opts.player1 == 'reflex':
        p1 = submission.ReflexPlayer(game.colors[0],0,evalFn,evalArgs)
    elif opts.player1 == 'expectimax':
        p1 = submission.ExpectiMaxPlayer(game.colors[0],0,evalFn,evalArgs)
    elif opts.player1 == 'human':
        p1 = player.HumanPlayer(game.colors[0],0)

    if opts.player2 == 'random':
        p2 = player.RandomPlayer(game.colors[1],1)

    if p1 is None or p2 is None:
        print "Please specify legitimate player"
        import sys
        sys.exit(1)

    #p2 = submission.ReflexPlayer(game.colors[1],1,evalFn,evalArgs)
    #p2 = player.ExpectiMaxPlayer(game.colors[1],1,evalFn,evalArgs)
    test([p1,p2],numGames=int(opts.numgames),draw=opts.draw)

if __name__=="__main__":
    ## TODO opts parer
    main()
