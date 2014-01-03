import time
import game
import agent, random, aiAgents
import pickle

def play(players):
    g = game.Game(game.LAYOUT)
    winner = run_game(players,g)
    print "The winner is : Player %s"%players[not winner].player
    g.draw()
    time.sleep(10)

def run_game(players,g):
    g.new_game()
    playernum = random.randint(0,1)
    over = False
    while not over:
        nodups = False
        roll = roll_dice(g)
        g.draw(roll)
        playernum = (playernum+1)%2
        if playernum:
            nodups=True
            g.reverse()
        turn(players[playernum],g,roll,nodups)
        if playernum:
            g.reverse()
        over = g.is_over()
        time.sleep(.02)
    return g.winner()

def turn(player,g,roll,nodups):
    print "Player %s rolled <%d,%d>."%(player.player,roll[0],roll[1])
    moves = g.getActions(roll,g.players[0],nodups=nodups)
    if moves:
        move = player.getAction(moves,g)
    else:
        move = None
    if move:
        g.takeAction(move,g.players[0])

def roll_dice(g):
    return (random.randint(1,g.die), random.randint(1,g.die))

def load_weights():
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

    parser.add_option("-p","--player1",dest="player1",
                      default="random",help="Choose type of first player")

    (opts,args) = parser.parse_args(args)    

    evalArgs = load_weights() 
    evalFn = aiAgents.nnetEval
        
    p1 = None
    if opts.player1 == 'random':
        p1 = agent.RandomAgent(game.Game.TOKENS[0])
    elif opts.player1 == 'reflex':
        p1 = aiAgents.TDAgent(game.Game.TOKENS[0],evalArgs)
    elif opts.player1 == 'expectimax':
        p1 = aiAgents.ExpectimaxAgent(game.Game.TOKENS[0],evalFn,evalArgs)
    elif opts.player1 == 'expectiminimax':
        p1 = aiAgents.ExpectiMiniMaxAgent(game.Game.TOKENS[0],evalFn,evalArgs)
    elif opts.player1 == 'human':
        p1 = agent.HumanAgent(game.Game.TOKENS[0])

#    p2 = agent.RandomAgent(game.Game.TOKENS[1])
    p2 = aiAgents.ExpectiMiniMaxAgent(game.Game.TOKENS[1],evalFn,evalArgs)
    if p1 is None:
        print "Please specify legitimate player"
        import sys
        sys.exit(1)

    play([p1,p2])

if __name__=="__main__":
    main()
