import DotsBoard as Dots
import random
import itertools
import pandas as pd
import numpy as np
import time
from pathos.pools import ProcessPool
import pathos as pa
import os

class DotsPlayer:
    """
    A player will play a dots and boxes game (that is, an instance of the Dots
    class you've already built) and learn from it (using a Q-table).
    The format of the Q-table is a pandas DataFrame whose row index is all game
    states and whose column index is all legal moves; the entries in the table
    are the best predictions (learned so far) of long-term reward for that move
    from that state.  Example:
    my_player.q_table.index is a pd.Series containing all board states; for a
      1x2 game this is something like "0000000", "0000001", "0000010",
      "0000011", and so on...
    my_player.q_table.columns contains the list of legal moves from a blank
      board, which in the 1x2 case is 0,1,2,3,4,5,6
    my_player.q_table.loc["0011010",3] is the value (as best as the player has
      learned it so far) of making move 3 when in state "0011010"
    """

    def __init__ ( self, n, m ):
        """
        Set up a new player capable of playing nxm Dots-and-Boxes games.  Make
        an empty Q-table with the appropriate set of row and column headings.
        Also initialize the alpha and gamma values to be used in the Bell
        equation when learning.
        """
        self.count = 0
        a = Dots.DotsBoard(n,m)
        self.n = n
        self.m = m
        self.num_cores = pa.helpers.cpu_count()
        self.pool = ProcessPool( nodes=self.num_cores )
        
        self.legal_boards = []
        for i in range((2**len(a.board))-1):
            self.legal_boards.append(format(i, "b").zfill(len(a.board)))

        if self.n == self.m:
            self.N = a.nothing()
            self.H = a.horizontal_flip()
            self.R = a.rotate()
            self.RR = a.combine(self.R,self.R)
            self.RRR = a.combine(self.R,self.RR)
            self.HR = a.combine(self.H,self.R)
            self.HRR= a.combine(self.HR,self.R)
            self.HRRR = a.combine(self.HRR,self.R)
            self.symmetries = [self.N,self.H,self.R,self.RR,self.RRR,self.HR,self.HRR,self.HRRR]
        else: 
            self.N = a.nothing()
            self.H = a.horizontal_flip()
            self.V = a.vertical_flip()
            self.HV = a.combine(self.H,self.V)
            self.symmetries = [self.N,self.H,self.V,self.HV]
        
        self.row_index = []
        for i in itertools.product(['0','1'],repeat=len(a.board)): 
            self.row_index.append("".join(i)) 
            
        self.column_index = []
        for i in range(len(a.board)):
            self.column_index.append(i)
        
        self.qtable = pd.DataFrame(index= range(len(self.row_index)), columns=range(len(self.column_index)))
        self.qtable.columns = self.column_index 
        self.qtable.index = self.row_index
        self.movetable = self.qtable.copy()
        self.qtable.loc[:,:] = 0

        for i in self.legal_boards:
            b = Dots.DotsBoard(n,m)
            b.get_index_positions(i,'0')
           
            for j in b.index_pos_list:
                b.read_board(i)
                start_score = b.score()
                b.play(j)
                end_score = b.score()
                self.qtable.loc[i,j] = end_score-start_score
                self.movetable.loc[i,j] = b.show_board()
        
        self.rewards = self.qtable.copy()
        self.alpha = 1
        self.gamma = 1 # or whatever values you want to try
        
    
    def reorder(self, original, order):
    """This is used for the use of symmetries to reduce the amount of exploration necessary, combines two lists"""
         listed = tuple(original)
         result = [listed[i] for i in order]
         return ''.join(result)
    
    def reorder_move(self,move,order):
    """Orders a move implementing a symmetrical equivalency such as a horizontal flip of the board"""
        return order.index(move)
    
    def best_move ( self, board ):
        """
        Computes the best move according to the current contents of the Q-table,
        for the state of the given board.  Returns the move (not its value).  So
        the return value for this function will be some item from the list
        self.legal_moves(board).  (If some things are tied for best move, you
        can return a random one.)  
        """

        legal_moves = [ i for i in range(len(board)) if board[i] == '0' ]
        
        if len(legal_moves) > 0:
            best = max( [ self.qtable.loc[board, m] for m in legal_moves ] )
            options = [ m for m in legal_moves if self.qtable.loc[board,m] == best ]
            return random.choice( options ) if len( options ) > 0 else None
        else:
            pass
    
    def random_move ( self, board ):
        """
        Just like best_move(), except it ignores the Q-table and picks randomly
        from the legal moves.  This is useful when learning by experimentation.
        """
            
        legal_moves = [ i for i in range(len(board)) if board[i] == '0' ]

        if len(legal_moves) > 0:
            random_num = random.choice(legal_moves)
            return random_num
        else:
            pass
 
    def learn_from_move ( self, old_state, move, new_state, reward, best_move ):
        """
        This method can be called to tell this player that they were given information
        about a move from old_state to new_state and the generated reward.  This
        method uses this information to update this player's Q-table,
        thus learning from the information given.
        """
        gamma = self.gamma if reward > 0 else -self.gamma
        
        if best_move is not None:
            self.qtable.loc[ old_state , move ] = ( 1 - self.alpha ) * self.qtable.loc[old_state , move] \
                + self.alpha * ( reward + gamma * self.qtable.loc[new_state, best_move] )
        else:
            self.qtable.loc[old_state , move] = ( 1 - self.alpha ) * self.qtable.loc[old_state , move] \
                + self.alpha * ( reward )
    
    def learn_from_move_symm( self, old_state,move,new_state,reward,best_move):
    """This method is the same as .learn_from_move() but also adds the associated symmetries in a given board to update the Qtable at all 
    relevant and related boards"""
        gamma = self.gamma if reward > 0 else -self.gamma
    
        if best_move is not None:
            for order in self.symmetries:
                old = self.reorder(old_state,order)
                move_re = self.reorder_move(move,order)
                self.qtable.loc[ old , move_re ] = \
                        ( 1 - self.alpha ) * self.qtable.loc[old , move_re] + self.alpha * ( reward + gamma * \
                        self.qtable.loc[self.reorder(new_state,order), \
                        self.reorder_move(best_move,order)] )
        else:
            for order in self.symmetries:
                old = self.reorder(old_state,order)
                move_re = self.reorder_move(move,order)
                self.qtable.loc[old , move_re] = \
                        ( 1 - self.alpha ) * self.qtable.loc[old , move_re] \
                        + self.alpha * (reward)
   
    def generate_multiple_experiences(self, num_games):
    """This method uses pathos to call the create_experience() method multiple time and take advantage of multiple cores to generate experiences""" 
        def get_experiences ( x ):
            return self.create_experience( num_games // self.num_cores )

        sets = self.pool.map( get_experiences, range(self.num_cores) )
        bigset = [ experience for a_set in sets for experience in a_set ]
        return bigset


    def create_experience (self,num_games):
    """This method generates num_games number of experience to train on wherein an experience is defines as a collection of a start_state
    my_move, the new_state, a reward, and the best_move from the new_state"""
        experiences = set()
        
        legal_boards = self.legal_boards
        
        for i in range(num_games):
            start_state = random.choice(legal_boards)
            
            my_move = self.random_move(start_state)
            
            new_state = self.movetable.loc[start_state,my_move]
            
            reward = self.rewards.loc[start_state,my_move]
            
            best_move = self.best_move(new_state)
                
            experiences.add( (start_state,my_move,new_state,reward,best_move) )

        return experiences
         
    def learn_from_games( self, num_games ):
    """Generates num_games number of experiences and and calls the .learn_from_move() method to learn from them"""
        for i in range(num_games):
            start_state = random.choice(self.legal_boards)
            
            my_move = self.random_move(start_state)

            new_state = self.movetable.loc[start_state,my_move]
            
            reward = self.rewards.loc[start_state,my_move]
            
            best_move = self.best_move(new_state)

            self.learn_from_move(start_state,my_move,new_state,reward,best_move)

   
    def learn_from_games_symm( self, num_games ):
        """Same as .learn_from_games() but calls learn_from_move_symm() instead"""
        
        for i in range(num_games):
            start_state = random.choice(self.legal_boards)
            
            my_move = self.random_move(start_state)

            new_state = self.movetable.loc[start_state,my_move]
            
            reward = self.rewards.loc[start_state,my_move]
            
            best_move = self.best_move(new_state)

            self.learn_from_move_symm(start_state,my_move,new_state,reward,best_move)

    def learn_from_games_mp(self,games):
    """Calls .learn_from_move() to learn from each experience given"""
        for arguments in games:
            self.learn_from_move(*arguments)

    def learn_from_games_mp_symm(self,games):
    """Same as .learn_from_games_mp() but calls .learn_from_move_symm() instead"""
        for arguments in games:
            self.learn_from_move_symm(*arguments)
           
    def is_fully_trained(self):
    """This function makes a backup of p.qtable, then calls p.learn_from_games(1000),
    then checks to see if q_table_difference(backup,p.qtable) is very small.
    If so, it returns True--training didn't make any progress--this guy is fully trained.
    Otherwise, it returns False--training made progress--this guy is still learning. 
    At the end of training it returns the number of experiences it used to train"""
        
        condition = True
        diff = 999
        tolerance = 0.001

        while diff > tolerance:
                table = self.qtable.copy()
                self.learn_from_games(1000)
                self.count += 1000
                diff = (table - self.qtable).abs().max().max()

        return self.count

    def is_fully_trained_symm(self):
    """Same as is_fully_trained() but calls .learn_from_games_symm() instead to take advantage of symmetries"""
        condition = True
        diff = 999
        tolerance = 0.001

        while diff > tolerance:
                table = self.qtable.copy()
                self.learn_from_games_symm(1000)
                self.count += 1000
                diff = (table - self.qtable).abs().max().max()
                

        return self.count

    def is_fully_trained_mp(self):
    """This method generates a batch of experiences to train on and then progressively trains through that batch determining if progress was made or not
    it operates the same as .is_fully_trained() but takes advantage of multiprocessing"""
    
        building_batch_size = 5000
        learning_batch_size = 1000
        diff = 999
        tolerance = 0.001

        while diff > tolerance:
            to_learn_from = self.generate_multiple_experiences(building_batch_size)
            while len(to_learn_from) > 0 and diff > tolerance:
                table = self.qtable.copy()
                self.learn_from_games_mp(to_learn_from[:learning_batch_size])
                to_learn_from = to_learn_from[learning_batch_size:]
                self.count += learning_batch_size
                diff = (table - self.qtable).abs().max().max()

        return self.count

    def is_fully_trained_mp_symm(self):
    """The same as is_fully_trained_mp() but calls .learn_from_games_mp_symm() to take advantage of symmetries"""
        building_batch_size = 5000
        learning_batch_size = 1000
        diff = 999
        tolerance = 0.001

        while diff > tolerance:
            to_learn_from = self.generate_multiple_experiences(building_batch_size)
            while len(to_learn_from) > 0 and diff > tolerance:
                table = self.qtable.copy()
                self.learn_from_games_mp_symm(to_learn_from[:learning_batch_size])
                to_learn_from = to_learn_from[learning_batch_size:]
                self.count += learning_batch_size
                diff = (table - self.qtable).abs().max().max()

        return self.count
