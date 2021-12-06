#!/usr/bin/env python
# coding: utf-8

# In[7]:


class DotsBoard:
    def __init__(self, row, column):
        self.r = row
        self.c = column
        self.lines = column + ((2*column)+1)*row
        self.turn = 0
        self.board = list('0'*self.lines)
        self.score1 = 0
        self.score2 = 0
        self.orderofmoves = []
        self.index_pos_list = []
        
    def __repr__(self):
        return f'{self.r}*{self.c} Board:{"".join(self.board)}'
        
    def get_index_positions(self, binary, element):
        ''' Returns the indexes of all occurrences of give element in
        the a list. This is used in the creation of symmetries in order to minimize computation '''
        self.board = list(binary)
        index_pos_list = []
        index_pos = 0
    
        while True:
            try:
                # Search for item in list from indexPos to the end of list
                index_pos = self.board.index(element,index_pos)
                # Add the index position in list
                self.index_pos_list.append(index_pos)
                index_pos += 1
            except ValueError as e:
                break
                
    def show_board(self):
     """Returns a string showing all played moves on a board, the format of a will be in binary where a 0 represents an unplayed
     move and a 1 represents a played move"""
        return ("".join(self.board))
    
    def read_board(self,binary):
     """Takes a string input and can read it into an exits Dots instance"""
        self.board = list(binary)

    def copy(self):
    """Returns a copy of the current instance of the Dots Board """
        result = Dots(self.r,self.c)
        result.read_board(self.show_board())
        return result
           
    def whose_turn(self):
    """Returns which players turn it is """
        if self.turn == 0:
            return 1
        else:
            return 2

    def play(self, move):
    """Plays a moves and checks whether the move scored any boxes to assign that to the correct player and change turns. Moves are taken as a 
    int input which references an index of a binary string of the board"""
        before = self.score()
        if self.board[move] =='0':
            self.board[move]='1'
            self.orderofmoves.append(move)
            after = self.score()
            
            if before != after:
                if self.turn == 0:
                    self.score1 += 1
                else:
                    self.score2 += 1
            else:
                if self.turn == 0:
                    self.turn = 1
                else:
                    self.turn = 0
        else:
            pass
   
    def dimensions(self):
    """Returns the dimensions, row * column, of the board"""
        dimensions = str(self.r) + ' * ' + str(self.c)
        return dimensions
   
    def moves_remaining(self):
    """Returns the number of moves remaining"""
        return self.lines-self.count()
    
    def count(self):
    """Returns the number of played moves"""
        return sum(map(int,self.board))
    
    def order(self):
    """Returns the order which the moves were played. Will on display correctly when the game is played from start to finish without using .read_board()"""
        return self.orderofmoves
   
    def score(self):
    """Computes the score of a given position"""
        s = 0
        
        for i in self.topstick_indices():
            
            if self.board[i] == '1' and self.board[i+self.c] =='1'             and self.board[i+self.c+1] == '1' and self.board[i+(2*self.c)+1] == '1':
                    
                s += 1
                        
        return s

    def legal_moves(self):
    """Returns a list with the index of all possible moves yet to be played"""
        legalmoves = []
        
        for i in range(len(self.board)):
            if self.board[i] == '0':
                legalmoves.append(i)
            else:
                pass
        return legalmoves    
 
    def score_player_one(self):
    """Returns player one's score, only work when the whole game has been played without using .read_board()"""
        return self.score1
    
    def score_player_two(self):
    """Returns player two's score, only work when the whole game has been played without using .read_board()"""
        return self.score2

    def topstick_indices(self):
    """Used to produce the GUI"""
        indices = []
        
        for i in range(self.r):
            for j in range(self.c):
                topstick = (i*(2*self.c + 1)) + j
                indices.append(topstick)
                
        return indices
    
    def horizontal(self):
    """Used to produce the GUI"""
        indices = []
        
        for i in range(self.r+1):
            for j in range(self.c):
                topstick = (i*(2*self.c + 1)) + j
                indices.append(topstick)
                
        return indices
    
    def lastinrow(self):
    """Used to produce the GUI"""
        indices = []
        value = -1
        
        for i in range(2*self.r+1):
                if i%2 == 0:
                    value += self.c
                    indices.append(value)
                else:
                    value += self.c+1
                    indices.append(value)
        
        return indices
    
    def horizontal_flip(self):
    """Produces a list of the index positions of the moves reordered after a horizontal flip of the board"""
        H = []
        x = self.c - 1
        while True:
            for i in range(self.c):
                H.append(x)
                x-=1
                
            if len(H) == self.lines:
                return H
                
            x += 2*self.c + 1
            
            for i in range(self.c+1):
                H.append(x)
                x -= 1
                
            x += 2*self.c + 1
      
    def vertical_flip(self):
    """Produces a list of the index positions of the moves reordered after a vertical flip of the board"""
        V = []
        x = self.lines - self.c
        
        while True:
            y = x
            for i in range(self.c):
                V.append(y)
                y += 1
                
            x -= self.c + 1
            y = x
            
            if len(V) == self.lines:
                return V
                
            for i in range(self.c+1):
                V.append(y)
                y += 1
            
            x -= self.c
      
    def rotate(self):
     """Produces a list of the index positions of the moves reordered after a rotation of the board"""
        R = []
        x = self.lines - 2*self.c - 1
        y = self.lines - self.c
        
        while True:
            a = x
            for i in range(self.c):
                R.append(a)
                a -= 2*self.c + 1
        
            x += 1
            
            if len(R) == self.lines:
                return R
            
            b = y
            for i in range(self.c+1):
                R.append(b)
                b -= 2*self.c + 1 
                
            y +=1
     
    def nothing(self):
    """Used to produce a list with the original index positions of the board"""
        N = []
        for i in range(self.lines):
            N.append(i)
            
        return N
     
    def combine(self, original, order):
    """Used to combine two symmetries together"""
        return [original[i] for i in order]
  
    def GUI(self):
    """Used to print the board in a more comprehensible fashion, the turn and score counters work best when the entire game was played with read.board()"""
        graph = ''
        
        for i in range(len(self.board)):
            if i in self.horizontal():
                if i in self.lastinrow():
                    if self.board[i] == '1':
                        graph += '+---+\n'
                    else:
                        graph += '+   +\n'
                else:
                    if self.board[i] == '1':
                        graph += '+---'
                    else:
                        graph += '+   '
            else: 
                if i in self.lastinrow():
                    if self.board[i] == '1':
                        graph += '|\n'
                    else:
                        graph += ' \n'
                else:
                    if self.board[i] == '1':
                        graph += '|   '
                    else:
                        graph += '    '
                        
        graph += 'Turn: '+ str(self.whose_turn())
        graph += '\nScore Player 1: ' + str(self.player1())
        graph += '\nScore Player 2: ' + str(self.player2()) + '\n'
        
        return (graph)
