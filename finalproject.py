#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
testest
"""
#%%
import numpy as np

import pygame as pg
import math
import numpy


board = np.zeros((11,11), dtype=int)

print(board)


#%%
pg.quit()


#%%


# Drawing those dash lines outside the 11x11 board
def draw_dash_line(surface, color, start, end, width=1, dash_length=4):

    x1, y1 = start
    x2, y2 = end
    dl = dash_length

    if (x1 == x2):
        ycoords = [y for y in range(y1, y2, dl if y1 < y2 else -dl)]
        xcoords = [x1] * len(ycoords)
    elif (y1 == y2):
        xcoords = [x for x in range(x1, x2, dl if x1 < x2 else -dl)]
        ycoords = [y1] * len(xcoords)
    else:
        a = abs(x2 - x1)
        b = abs(y2 - y1)
        c = round(math.sqrt(a**2 + b**2))
        dx = dl * a / c
        dy = dl * b / c

        xcoords = [x for x in numpy.arange(x1, x2, dx if x1 < x2 else -dx)]
        ycoords = [y for y in numpy.arange(y1, y2, dy if y1 < y2 else -dy)]

    next_coords = list(zip(xcoords[1::2], ycoords[1::2]))
    last_coords = list(zip(xcoords[0::2], ycoords[0::2]))
    for (x1, y1), (x2, y2) in zip(next_coords, last_coords):
        start = (round(x1), round(y1))
        end = (round(x2), round(y2))
        pg.draw.line(surface, color, start, end, width)


####################################################################################################################
# create the initial empty chess board in the game window
def draw_board():
    
    global xbline, w_size, pad, sep
    
    xbline = bline + 8                        # Add 4 extra line on each boundaries to make chains of 5 that cross boundaries easier to see
    w_size = 720                              # window size
    pad = 36                                  # padding size
    sep = int((w_size-pad*2)/(xbline-1))      # separation between lines = [window size (720) - padding*2 (36*2)]/(Total lines (19) -1)
    
    surface = pg.display.set_mode((w_size, w_size))
    pg.display.set_caption("Gomuku (a.k.a Five-in-a-Row)")
    
    color_line = [0, 0, 0]
    color_board = [241, 196, 15]

    surface.fill(color_board)
    
    for i in range(0, xbline):
        draw_dash_line(surface, color_line, [pad, pad+i*sep], [w_size-pad, pad+i*sep])
        draw_dash_line(surface, color_line, [pad+i*sep, pad], [pad+i*sep, w_size-pad])
        
    for i in range(0, bline):
        pg.draw.line(surface, color_line, [pad+4*sep, pad+(i+4)*sep], [w_size-pad-4*sep, pad+(i+4)*sep], 4)
        pg.draw.line(surface, color_line, [pad+(i+4)*sep, pad+4*sep], [pad+(i+4)*sep, w_size-pad-4*sep], 4)

    pg.display.update()
    
    return surface


####################################################################################################################
# Draw the stones on the board at pos = [row, col]. 
# Draw a black circle at pos if color = 1, and white circle at pos if color =  -1
# row and col are be the indices on the 11x11 board array
# dark gray and light gray circles are also drawn on the dotted grid to indicate a phantom stone piece
def draw_stone(surface, pos, color=0):

    color_black = [0, 0, 0]
    color_dark_gray = [75, 75, 75]
    color_white = [255, 255, 255]
    color_light_gray = [235, 235, 235]
    
    matx = pos[0] + 4 + bline*np.array([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]]).flatten()
    matx1 = np.logical_and(matx >= 0, matx < xbline)
    maty = pos[1] + 4 + bline*np.array([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]]).T.flatten()
    maty1 = np.logical_and(maty >= 0, maty < xbline)
    mat = np.logical_and(np.logical_and(matx1, maty1), np.array([[True, True, True], [True, False, True], [True, True, True]]).flatten())

    if color==1:
        pg.draw.circle(surface, color_black, [pad+(pos[0]+4)*sep, pad+(pos[1]+4)*sep], 15, 0)
        for f, x, y in zip(mat, matx, maty):
            if f:
                pg.draw.circle(surface, color_dark_gray, [pad+x*sep, pad+y*sep], 15, 0)
                
    elif color==-1:
        pg.draw.circle(surface, color_white, [pad+(pos[0]+4)*sep, pad+(pos[1]+4)*sep], 15, 0)
        for f, x, y in zip(mat, matx, maty):
            if f:
                pg.draw.circle(surface, color_light_gray, [pad+x*sep, pad+y*sep], 15, 0)
        
    pg.display.update()
    

####################################################################################################################

def print_winner(surface, winner=0):
    if winner == 2:
        msg = "Draw! So White wins"
        color = [170,170,170]
    elif winner == 1:
        msg = "Black wins!"
        color = [0,0,0]
    elif winner == -1:
        msg = 'White wins!'
        color = [255,255,255]
    else:
        return
        
    font = pg.font.Font('freesansbold.ttf', 32)
    text = font.render(msg, True, color)
    textRect = text.get_rect()
    textRect.topleft = (0, 0)
    surface.blit(text, textRect)
    pg.display.update()

 
#%%

def check_row(rdata):    
    rstr = ''.join(map(str,rdata))
    if '11111' in rstr:
        return 1
    elif '99999' in rstr:
        return -1
    else:
        return 0
    
def check_2d(boarddata):
    for i in range(len(boarddata)):
        result = check_row(boarddata[i,:])
        if result == 1:
            return 1
        elif result == -1:
            return -1
    return 0
    
def roll_board(board):
    board_temp1 = board.copy()
    board_temp2 = board.copy()
    l = len(board_temp1)
    for i in range(l):
        board_temp1[i,:] = np.roll(board_temp1[i,:],-i)
        board_temp1[i,l-i:l] = 0

        board_temp2[i,:] = np.roll(board_temp2[i,:],i)
        board_temp2[i,0:i] = 0
    return board_temp1,board_temp2
    

def check_winner(board):
     # Input: board = current configuration of the 11x11 matrix
     # Output: 1 or -1 to indicate which color wins; 2 if it is a draw; 0 if the game is not yet over

     if sum(sum(board==0))>0:
          return 2
     ext_board = np.zeros((xbline,xbline), dtype=int)
     ext_board[4:4+bline,4:4+bline]=board
     ext_board[0:4,:] = ext_board[bline:4+bline,:]
     ext_board[4+bline:8+bline,:] = ext_board[4:8,:] 
     ext_board[:,0:4] = ext_board[:,bline:4+bline]
     ext_board[:,4+bline:8+bline] = ext_board[:,4:8]
     ext_board[np.where(ext_board==-1)]= 9
     
     winner = check_2d(ext_board)
     if winner == 0:
         winner = check_2d(np.transpose(ext_board))
         if winner == 0:
             b1,b2=roll_board(ext_board)
             winner = check_2d(np.transpose(b1))
             if winner == 0:
                 winner = check_2d(np.transpose(b2))
                 if winner == 0:
                     b1,b2=roll_board(np.transpose(ext_board))
                     winner = check_2d(np.transpose(b1))
                     if winner == 0:
                         winner = check_2d(np.transpose(b2))
     return winner

#%%
import pandas as pd

db_chessboard = pd.DataFrame(np.arange(bline**2).reshape((bline, bline)))



class MCTS_path:
    def __init__(self):
        self.value = 0
        self.times = 0
        self.layer = 0
        # Parents is a list of (row, column)
        self.parents = []

    def ucb(self):
        first_parent = self.parents[-1]
        for i in db_chessboard[first_parent]:
            if i.layer == self.layer - 1:
                N_value = i.times
        return self.value/self.times + 2 * np.sqrt(np.log(N_value)/self.times)

def avoid_win(board,color):
    
    legal_move = np.argwhere(board == 0)
    for i in legal_move:
        temp_board = board.copy()
        temp_board[i[0], i[1]] = color
        check_result = check_winner(temp_board)
        if check_result !=0:
            return i
    return None


def ai_move(board, color):
     # Input: board = current configuration of the 11x11 matrix
     #        color = the stone color of the AI
     # Output: [row, col] = a 1x2 array to indicate where the AI should place its next stone 
     check = avoid_win(board,-color)
     
     if check !=None:
         return check
     else:
 
    
#%%

def main(player_is_black=True):
    
    global bline
    bline = 11                  # the board size is 11x11 => need to draw 11 lines on the board
    
    pg.init()
    surface = draw_board()
    
    board = np.zeros((bline,bline), dtype=int)
    running = True
    gameover = False
    
    while running:
        
        ####################################################################################################
        ######################## Normally your edit should be within the while loop ########################
        ####################################################################################################
       
        for event in pg.event.get():              # A for loop to process all the events initialized by the player
            
            if event.type == pg.QUIT:             # terminate if player closes the game window 
                running = False
                
            if event.type == pg.MOUSEBUTTONDOWN and not gameover:        # detect whether the player is clicking in the window
                
                (x,y) = event.pos                                        # check if the clicked position is on the 11x11 center grid
                if (x > pad+3.75*sep) and (x < w_size-pad-3.75*sep) and (y > pad+3.75*sep) and (y < w_size-pad-3.75*sep):
                    row = round((x-pad)/sep-4)     
                    col = round((y-pad)/sep-4)
                    
                    if board[row, col] == 0:                             # update the board matrix if that position has not been occupied
                        color = 1 if player_is_black else -1
                        board[row, col] = color
                        draw_stone(surface, [row, col], color)
                        
                        
                        check_result = check_winner(board)              #check whether there is a winner
                        print_winner(surface,check_result)              #print the result
                        if check_result != 0 : 
                            gameover = True                             #end the game when there is a winner
                        else:
                            ai_color = -1 if player_is_black else 1
                            ai_pos = ai_move(board, ai_color)
                            board[ai_pos[0],ai_pos[1]] = ai_color
                            draw_stone(surface, ai_pos, ai_color)
                            check_result = check_winner(board)
                            print_winner(surface,check_result)
                            if check_result != 0 : 
                                gameover = True 
                
        ####################################################################################################
        ######################## Normally Your edit should be within the while loop ########################
        ####################################################################################################
        
    pg.quit()

    

    
    
if __name__ == '__main__':
    main(True)
