import numpy as np
import random
import copy
import time

# from operator import itemgetter

# from tree_format import format_tree

# def get_tree(root):
#     if root == None:
#         return ()
#     return (str(root.state.board) + ' ' + str(root.q) + '/' + str(root.n), [get_tree(x) for x in root.child])

# player = 0 means the white player, player = 1 means the black player

class State:
    def __init__(self, board, player = 0, pre_game_over = False):
        self.player = player     #which player is going to move now
        self.board = board
        self.actions_num = 0       #how many actions are available
        self.actions = self.action()    
        self.game_over = False
        self.pre_game_over = pre_game_over

    def change(self):     #change the player
        self.player = 1 - self.player
        self.set_zero()
        self.actions = self.action()

    def action(self):
        opponent = 0
        own = 0
        move = []
        if self.player == 0:
            opponent = -1
            own = 1
        else:
            opponent = 1
            own = -1
        for i in range(8):
            for j in range(8):
                if self.board[i][j] == own:
                    for (dr, dc) in [(1, 1), (-1, 1), (-1, -1), (1, -1), (1, 0), (-1, 0), (0, 1), (0, -1)]:
                        r, c = i + dr, j + dc
                        while r < 8 and r >= 0 and c < 8 and c >= 0 and self.board[r][c] == opponent:
                            r += dr
                            c += dc
                        if not (r == i + dr and c == j + dc) and r < 8 and r >= 0 and c < 8 and c >= 0 and self.board[r][c] == 0 and (r,c) not in move:
                            move.append((r, c))
                            self.actions_num += 1                        
        return move

    def set_zero(self):
        self.actions_num = 0

    def move(self):    #for simulation
        if self.actions_num == 0:
            self.change()
        else:
            self.pre_game_over = False
            a = random.choice(self.actions)
            self.actions.remove(a)
            self.result(a)
            self.change()   

    def result(self, a):
        if self.player == 0:
            self.board[a[0]][a[1]] = 1
        else:
            self.board[a[0]][a[1]] = -1

        opponent = 0
        own = 0
        if self.player == 0:
            opponent = -1
            own = 1
        else:
            opponent = 1
            own = -1
        i, j = a[0], a[1]
        for (dr, dc) in [(1, 1), (-1, 1), (-1, -1), (1, -1), (1, 0), (-1, 0), (0, 1), (0, -1)]:
            r, c = i + dr, j + dc
            while r < 8 and r >= 0 and c < 8 and c >= 0 and self.board[r][c] == opponent:
                r += dr
                c += dc
            if r < 8 and r >= 0 and c < 8 and c >= 0 and self.board[r][c] == own:
                r -= dr
                c -= dc
                while not (r == i and c == j):
                    self.board[r][c] = own
                    r -= dr
                    c -= dc

class Node:
    def __init__(self, state = None, parent = None, q = 0, n = 1):
        self.state = state
        self.parent = parent
        self.child = []
        self.n = n
        self.q = q

    def is_fully_expanded(self):
        if self.state.actions_num == 0:
            return False
        return self.state.actions_num == len(self.child)

    def get_parent(self):
        return self.parent


def UTCSearch(s, iters = 200):
    s0 = copy.deepcopy(s)
    root = Node(s0)
    #root = v0
    for i in range(iters):
        CurNode = SelectPolicy(root)
        state_terminal = SimulatePolicy(CurNode)
        score = calculate_score(state_terminal)
        BackPropagate(CurNode, max(0, score))
    #tree = get_tree(root)
    #print(format_tree(tree, format_node=itemgetter(0), get_children=itemgetter(1)))
    return UCB1(root, 0)

def SelectPolicy(v):
    while not v.state.game_over:
        if not v.is_fully_expanded():
            return expand(v)
        else:
            v = UCB1(v, 2**0.5 / 2)
    return v

def SimulatePolicy(CurNode):    
    s = copy.deepcopy(CurNode.state)
    while not is_game_over(s):
        s.move()
    return s

def BackPropagate(v, score):
    v0 = v
    while v0 != None:
        v0.n += 1
        if v0.state.player == 0:
            v0.q -= score
        else:
            v0.q += score
        v0 = v0.get_parent()

def expand(v):
    if len(v.state.actions) == 0:
        s = State(copy.deepcopy(v.state.board), v.state.player, True)
        v0 = Node(s, parent = v)
        v0.state.change()
        v.child.append(v0)  
        is_game_over(v0.state) 
        return v0
    a = random.choice(v.state.actions)
    v.state.actions.remove(a)
    s = State(copy.deepcopy(v.state.board), v.state.player, False)
    s.result(a)
    v0 = Node(s, parent = v)
    v0.state.change()
    v.child.append(v0)
    is_game_over(v0.state)
    return v0

def UCB1(v, c):
    temp = -100000000
    v0 = None
    for i in v.child:
        if i.q / i.n + c * np.sqrt(2 * np.log(v.n) / i.n) > temp:
            v0 = i
            temp = i.q / i.n + c * np.sqrt(2 * np.log(v.n) / i.n)
    return v0

def calculate_score(st):
    b = st.board
    cnt_white = 0
    cnt_black = 0
    for i in range(8):
        for j in range(8):
            if b[i][j] == 1:
                cnt_white += 1
            if b[i][j] == -1:
                cnt_black += 1
    #print('the score is: ', cnt_white - cnt_black)
    return (cnt_white - cnt_black) / 5
    # if cnt_white > cnt_black:
    #     return 1
    # if cnt_white < cnt_black:
    #     return -1
    # return 0

def is_game_over(s):
    if s.actions_num == 0:
        if s.pre_game_over:
            s.game_over = True
            return True
        s.pre_game_over = True
    return False

# def display(s):
#     for i in range(8):
#         for j in range(8):
#             if s.board[i][j] == 1:
#                 print('o', end = '')
#             elif s.board[i][j] == -1:
#                 print('x', end = '')
#             else:
#                 print('-', end = '')
#         print('')
#     print('-----------------------------------------')  