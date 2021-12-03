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
        the list- listOfElements '''
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
           
    #Returns a string showing all played moves on a board    
    def show_board(self):
        return ("".join(self.board))
    
    #Takes and string input and can interpret it into the board environment
    def read_board(self,binary):
        self.board = list(binary)

    #Returns a copy of the current instance of the Dots Board 
    def copy(self):
        result = Dots(self.r,self.c)
        result.read_board(self.show_board())
        return result
        
    #Returns which players turn it is    
    def whose_turn(self):
        if self.turn == 0:
            return 1
        else:
            return 2
    
    #This plays a moves and checks whether the move scored any boxes to assign that to the correct player and change turns if needed.
    def play(self, move):
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

    #Prints the dimensions row * column of the board    
    def dimensions(self):
        print(self.r,'*',self.c)

    #Returns the number of moves remaining    
    def moves_remaining(self):
        return self.lines-self.count()
    
    def count(self):
        return sum(map(int,self.board))
    
    #Returns the ored in which the moves were played
    def order(self):
        return self.orderofmoves

    #Computes the score of a given position    
    def score(self):
        s = 0
        
        for i in self.topstick_indices():
            
            if self.board[i] == '1' and self.board[i+self.c] =='1'             and self.board[i+self.c+1] == '1' and self.board[i+(2*self.c)+1] == '1':
                    
                s += 1
                        
        return s

    #Return a list with all possible legal moves yet to be played
    def legal_moves(self):
        legalmoves = []
        
        for i in range(len(self.board)):
            if self.board[i] == '0':
                legalmoves.append(i)
            else:
                pass
        return legalmoves    
    
    #Returns Player 1 score
    def player1(self):
        return self.score1
    
    #Returns Player 2 score
    def player2(self):
        return self.score2
    
    #Used in the GUI
    def topstick_indices(self):
        indices = []
        
        for i in range(self.r):
            for j in range(self.c):
                topstick = (i*(2*self.c + 1)) + j
                indices.append(topstick)
                
        return indices
    
    #Used in the GUI
    def horizontal(self):
        indices = []
        
        for i in range(self.r+1):
            for j in range(self.c):
                topstick = (i*(2*self.c + 1)) + j
                indices.append(topstick)
                
        return indices
    
    #Used in the GUI
    def lastinrow(self):
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
    
    #Used to flip the board horizonatlly
    def horizontal_flip(self):
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

    #Used to flip the board vertically        
    def vertical_flip(self):
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

    #Used to rotate the board        
    def rotate(self):
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

    #Used to produce a list with the original order of the board      
    def nothing(self):
        N = []
        for i in range(self.lines):
            N.append(i)
            
        return N

    #Used to combine multiple symmetries        
    def combine(self, original, order):
        return [original[i] for i in order]

    #Used to print the board        
    def GUI(self):
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