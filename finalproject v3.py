#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Final Project

"""
#%%
import numpy as np

import pygame as pg
import math
import random
import time
from scipy.signal import convolve2d

#%%

"""
When you encounter an error while testing your code, the pygame window will freeze. 
Trying to close the window will force python to restart the kernal. To avoid this, 
you have to manually run pg.quit() in the console/another notebook cell to kill the process.

"""

#pg.quit()


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

        xcoords = [x for x in np.arange(x1, x2, dx if x1 < x2 else -dx)]
        ycoords = [y for y in np.arange(y1, y2, dy if y1 < y2 else -dy)]

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

def check_winner(board):
     # Input: board = current configuration of the 11x11 matrix
     # Output: 1 or -1 to indicate which color wins; 2 if it is a draw; 0 if the game is not yet over
     
     bline = len(board)
     xbline = bline + 8
     
     if sum(sum(board==0)) == 0:
          return 2
     ext_board = np.zeros((xbline,xbline), dtype=int)
     ext_board[4:4+bline,4:4+bline]=board
     ext_board[0:4,:] = ext_board[bline:4+bline,:]
     ext_board[4+bline:8+bline,:] = ext_board[4:8,:] 
     ext_board[:,0:4] = ext_board[:,bline:4+bline]
     ext_board[:,4+bline:8+bline] = ext_board[:,4:8]
     
     winner = 0
     for row in range(xbline - 5 + 1):
            for col in range(xbline - 5 + 1):
                current_grid = ext_board[row: row + 5, col: col + 5]
                sum_horizontal = np.sum(current_grid, axis=1)
                sum_vertical = np.sum(current_grid, axis=0)
                sum_diagonal_1 = np.sum(current_grid.diagonal())
                sum_diagonal_2 = np.sum(np.flipud(current_grid).diagonal())
                if 5 in sum_horizontal or 5 in sum_vertical:
                    winner = 1
                if sum_diagonal_1 == 5 or sum_diagonal_2 == 5:
                    winner = 1
                if -5 in sum_horizontal or -5 in sum_vertical:
                    winner = -1
                if sum_diagonal_1 == -5 or sum_diagonal_2 == -5:
                    winner = -1

     return winner

#%%

def avoid_win(board,color):
    
    legal_move = np.argwhere(board == 0)
    for i in legal_move:
        temp_board = board.copy()
        temp_board[i[0], i[1]] = color
        check_result = check_winner(temp_board)
        if check_result !=0:
            return ([i[0], i[1]])
    return (999,999)

#%%  

def unvisited_pos(legal_move,children):
    temp_legal_move = legal_move.tolist()
    if len(children) == 0:
        return legal_move
    
    for child in children:
        if [child['row'],child['col']] in temp_legal_move:
            temp_legal_move.remove([child['row'],child['col']])
    return np.array(temp_legal_move)

def find_adj_empty_space(board):
    kernelx = np.array([[1, 1, 1],
           [0, 0, 0],
           [1, 1, 1]])
    kernely = np.array([[1, 0, 1],
           [1, 0, 1],
           [1, 0, 1]])
    boardx = convolve2d(board, kernelx, mode="same")
    boardy = convolve2d(board, kernely, mode="same")
    board2 = np.sqrt(boardx**2+boardy**2)
    legal_move = np.argwhere(board == 0)
    adj_move = np.argwhere(board2 != 0)
    overlap = [e for e in legal_move.tolist() if e in adj_move.tolist()]
    return np.array(overlap)
   

def select_child(node):
    ucb_list = [child['value']/child['num']+(-1)**(child['layer']+1)*2* math.sqrt(math.log(node['num'])/child['num']) 
                for child in node['children']]
    if (node['layer']+1) %2 == 1:
        select_id = ucb_list.index(np.max(ucb_list))
    else:
        select_id = ucb_list.index(np.min(ucb_list))
    return node['children'][select_id]


#%%

shape_score = [(50, (0, 1, 1, 0, 0)),
               (50, (0, 0, 1, 1, 0)),
               (200, (1, 1, 0, 1, 0)),
               (500, (0, 0, 1, 1, 1)),
               (500, (1, 1, 1, 0, 0)),
               (5000, (0, 1, 1, 1, 0)),
               (5000, (0, 1, 0, 1, 1, 0)),
               (5000, (0, 1, 1, 0, 1, 0)),
               (5000, (1, 1, 1, 0, 1)),
               (5000, (1, 1, 0, 1, 1)),
               (5000, (1, 0, 1, 1, 1)),
               (5000, (1, 1, 1, 1, 0)),
               (5000, (0, 1, 1, 1, 1)),
               (50000, (0, 1, 1, 1, 1, 0)),
               (99999999, (1, 1, 1, 1, 1))]

ratio = 1

def evaluation(is_ai, board):
    # Create the extended chess board.
    xbline=19
    bline = len(board)
    xbline= bline+8
    ext_board = np.zeros((xbline,xbline), dtype=int)
    ext_board[4:4+bline,4:4+bline]=board.copy()
    ext_board[0:4,:] = ext_board[bline:4+bline,:]
    ext_board[4+bline:8+bline,:] = ext_board[4:8,:] 
    ext_board[:,0:4] = ext_board[:,bline:4+bline]
    ext_board[:,4+bline:8+bline] = ext_board[:,4:8]
    # List1 is black stone; list2 is white.
    list1 = (np.argwhere(board==1)+4).tolist()
    list2 = (np.argwhere(board==-1)+4).tolist()
    total_score = 0

    if is_ai:
        my_list = list1
        enemy_list = list2
    else:
        my_list = list2
        enemy_list = list1

    # 算自己的得分
    score_all_arr = []  # 得分形状的位置 用于计算如果有相交 得分翻倍
    my_score = 0
    for pt in my_list:
        m = pt[0]
        n = pt[1]
        my_score += cal_score(m, n, 0, 1, enemy_list, my_list, score_all_arr)
        my_score += cal_score(m, n, 1, 0, enemy_list, my_list, score_all_arr)
        my_score += cal_score(m, n, 1, 1, enemy_list, my_list, score_all_arr)
        my_score += cal_score(m, n, -1, 1, enemy_list, my_list, score_all_arr)

    #  算敌人的得分， 并减去
    score_all_arr_enemy = []
    enemy_score = 0
    for pt in enemy_list:
        m = pt[0]
        n = pt[1]
        enemy_score += cal_score(m, n, 0, 1, my_list, enemy_list, score_all_arr_enemy)
        enemy_score += cal_score(m, n, 1, 0, my_list, enemy_list, score_all_arr_enemy)
        enemy_score += cal_score(m, n, 1, 1, my_list, enemy_list, score_all_arr_enemy)
        enemy_score += cal_score(m, n, -1, 1, my_list, enemy_list, score_all_arr_enemy)

    total_score = my_score - enemy_score*ratio*0.1
    
    return total_score

def cal_score(m, n, x_decrict, y_derice, enemy_list, my_list, score_all_arr):
    add_score = 0
    max_score_shape = (0, None)

    for item in score_all_arr:
        for pt in item[1]:
            if m == pt[0] and n == pt[1] and x_decrict == item[2][0] and y_derice == item[2][1]:
                return 0

    for offset in range(-5, 1):
        pos = []
        for i in range(0, 6):
            if [m + (i + offset) * x_decrict, n + (i + offset) * y_derice] in enemy_list:
                pos.append(2)
            elif [m + (i + offset) * x_decrict, n + (i + offset) * y_derice] in my_list:
                pos.append(1)
            else:
                pos.append(0)
        tmp_shap5 = (pos[0], pos[1], pos[2], pos[3], pos[4])
        tmp_shap6 = (pos[0], pos[1], pos[2], pos[3], pos[4], pos[5])

        for (score, shape) in shape_score:
            if tmp_shap5 == shape or tmp_shap6 == shape:
                if score > max_score_shape[0]:
                    max_score_shape = (score, ((m + (0+offset) * x_decrict, n + (0+offset) * y_derice),
                                               (m + (1+offset) * x_decrict, n + (1+offset) * y_derice),
                                               (m + (2+offset) * x_decrict, n + (2+offset) * y_derice),
                                               (m + (3+offset) * x_decrict, n + (3+offset) * y_derice),
                                               (m + (4+offset) * x_decrict, n + (4+offset) * y_derice)), (x_decrict, y_derice))


    if max_score_shape[1] is not None:
        for item in score_all_arr:
            for pt1 in item[1]:
                for pt2 in max_score_shape[1]:
                    if pt1 == pt2 and max_score_shape[0] > 10 and item[0] > 10:
                        add_score += item[0] + max_score_shape[0]

        score_all_arr.append(max_score_shape)


    return add_score + max_score_shape[0]


        
#%%
def selection(board, root_node):
    temp_board = board.copy()
    stop = False
    path = [root_node]
    selected_node = root_node
    count = 0
    
    while not(stop):
        count += 1
        children = selected_node['children']
        #legal_move = np.argwhere(temp_board == 0)
        legal_move = find_adj_empty_space(temp_board)

        if len(children) == len(legal_move):
            selected_node = select_child(selected_node)
            temp_board[selected_node['row'], selected_node['col']] = selected_node['color']
            path.append(selected_node)
            if len(legal_move) == 1:
                return path
        else:
            return path
            
 
#### !!!!!!!!!! need to improve !!!!! ####

def expand(board,path):
    temp_board = board.copy()
    leaf = path[-1]
    
    for node in path:
        if node['is leaf node']:
            temp_board[node['row'], node['col']] = node['color']
    
    #legal_move = np.argwhere(temp_board == 0)
    legal_move = find_adj_empty_space(temp_board)
    
    if len(legal_move)>0:
        unvisited_move = unvisited_pos(legal_move,leaf['children'])
        pos = random.choice(unvisited_move)   # => find better way than random to expand!
        new_child ={
              'value': 0,
              'num': 0,
              'is leaf node': True,
              'layer': leaf['layer']+1,
              'row': pos[0],
              'col': pos[1],
              'color': leaf['color'] *(-1),
              'children':[]
              }
        leaf['children'].append(new_child)
        path.append(new_child)
        print('expand layer ',leaf['layer']+1)
        return new_child
    else:
        return None



#### !!!!!!!!!! need to improve !!!!! ######
def simulate(board,new_leaf,ai_color):
    temp_board = board.copy()
    if ai_color == 1:
        is_ai = True
    else:
        is_ai = False
    return evaluation(is_ai,temp_board)
 
def backup(path,reward):
    for node in path:
        node['value'] += reward
        node['num'] += 1


           
def run(board, node, num_rollout,ai_color):
    path = selection(board, node)
    new_leaf = expand (board,path)
    
    if new_leaf != None:
        temp_board = board.copy()
        for node in path:
            if node['is leaf node']:
                temp_board[node['row'], node['col']] = node['color']
        reward = 0
        for i in range (num_rollout):
            reward += simulate(temp_board, new_leaf,ai_color)
        reward = reward / num_rollout
        backup(path, reward)


def ai_move(board, color):
     # Input: board = current configuration of the 11x11 matrix
     #        color = the stone color of the AI
     # Output: [row, col] = a 1x2 array to indicate where the AI should place its next stone 
    timeout = time.time() + 4.9
    
    board_width = len(board)
    
    if sum(sum(board==0)) == board_width**2:
        
         return (board_width//2,board_width//2)
    
    check = avoid_win(board,-color)
    if check == (999,999):
        
        check_ai = avoid_win(board,color)
        
        if check_ai == (999,999):
            Node={
                'value': 0,
                'num': 0,
                'is leaf node': False,
                'layer': 0,
                'row': 999,
                'col': 999,
                'color': - color,
                'children':[]
                }
            while time.time() < timeout:
                 run(board,Node,1,color)
            best_child = select_child(Node) 
            return (best_child['row'],best_child['col'])
        else:
            return check_ai
    else:      
        return check



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
                        
                    ############################################# added ##############################################################
                        check_result = check_winner(board)              #check whether there is a winner
                        print_winner(surface,check_result)              #print the result
                        if check_result != 0 : 
                            gameover = True                             #end the game when there is a winner
                        else:
                            ai_color = -1 if player_is_black else 1
                            (a,b) = ai_move(board, ai_color)            #position computed
                            board[a,b] = ai_color
                            draw_stone(surface, [a,b], ai_color)
                            check_result = check_winner(board)          #check whether there is a winner
                            print_winner(surface,check_result)          #print the result
                            if check_result != 0 :                      #end the game when there is a winner
                                gameover = True 
                    ##################################################################################################################
        
        
        ####################################################################################################
        ######################## Normally Your edit should be within the while loop ########################
        ####################################################################################################
        
    pg.quit()


if __name__ == '__main__':
    main(False)