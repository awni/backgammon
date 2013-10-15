
import player
import numpy as np

def get_col_feats(column,color):
    feats = [0.]*4
    if len(column)>0 and column[0].color==color:
        for i in range(len(column)):
            feats[min(i,3)] += 1
    return feats
            
def extract_features(game):
    """
    @params game: state of backgammon board
    
    @returns features: list of real valued features
    """
    features = []
    for color in ['w','b']:
        for col in game.grid:
            feats = get_col_feats(col,color)
            features += feats
        features.append(float(len(game.bar_pieces[color])))
        features.append(float(len(game.out_pieces[color])))
    return features

class NNPlayer(player.Player, object):
    
    def __init__(self,color,num,weights):
        super(self.__class__,self).__init__(color,num)
        self.w1,self.w2,self.b1,self.b2 = weights


    def take_turn(self,moves,game):
        move = None
        bestScore = 0
        for m in list(moves):
            
            # take the move
            tmpGame = game.clone()
            tmpGame.take_turn(m,self.color)

            # evaluate the state
            features = np.array(extract_features(tmpGame)).reshape(-1,1)
            hiddenAct = 1/(1+np.exp(-(self.w1.dot(features)+self.b1)))
            pred = 1/(1+np.exp(-(self.w2.dot(hiddenAct)+self.b2)))
            if pred>bestScore:
                move = m
                bestScore = pred
        return move
            
