
import game, player, random, submission

def run_game():
    g = game.Game(game.layout)
    g.new_game()
    g.draw()
    
    players = [player.HumanPlayer(g.colors[0],0), player.HumanPlayer(g.colors[1],1)]
    
    playernum = -1
    over = False
    while not over:
        playernum = (playernum+1)%2
        turn(players[playernum],g)
        g.draw()
        over = g.is_over()
        
    print "The winner is Player %d"%players[playernum].num

def turn(player,g):
    roll = roll_dice()
    print "Player %d rolled <"%player.num+str(roll[0])+", "+str(roll[1])+">"
    moves = g.get_moves(roll,player.color)
    print moves
    move = player.take_turn(moves)
    if move:
        g.take_turn(move,player.color)

def roll_dice():
    return (random.randint(1,game.quad), random.randint(1,game.quad))

if __name__=="__main__":
    run_game()
