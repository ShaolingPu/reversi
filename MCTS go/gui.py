import pygame
import sys
from pygame.locals import *
from mcts import *
import time
import copy
import math

cnt_white = 0
cnt_black = 0

t = 0
total_t = 0

difficulty = 0
its = [200, 500, 1000]
levels = ['easy', 'medium', 'hard']
firsts = ['AI first', 'human first']

player = 1

def choose():
    global difficulty
    global player
    choose_font = pygame.font.Font(None, 40)
    while True:
        x,y = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                if x >= 750 and x <= 900 and y >= 245 and y <= 280:
                    difficulty = (difficulty + 1) % 3
                if x >= 750 and x <= 900 and y >= 370 and y <= 405:
                    player = player ^ 1
                if x >= 750 and x <= 900 and y >= 495 and y <= 530:
                    return 
        screen.blit(choose_img, (630, 80))
        difficulty_str = choose_font.render(levels[difficulty], True, blue)
        who_first = choose_font.render(firsts[player], True, blue)
        screen.blit(difficulty_str, (780, 255))
        screen.blit(who_first, (755, 380))
        start = choose_font.render('start', True, blue)
        screen.blit(start, (780, 505))
        pygame.display.update()

                    

def draw_chessboard(screen):
    color = (233, 204, 138)
    position = (600, 80, 480, 480)
    width = 0
    pygame.draw.rect(screen, color, position, width)
    
    width = 1
    for i in range(0, 9):
        if i == 0 or i == 8:
            width = 2
        pygame.draw.line(screen, (0, 0, 0), (600 + 60 * i, 80), (600 + 60 * i, 560), width = width)
        pygame.draw.line(screen, (0, 0, 0), (600, 80 + 60 * i), (1080, 80 + 60 * i), width = width) 
        width = 1
    

def display(s, screen):
    global cnt_white
    global cnt_black
    cnt_white = 0
    cnt_black = 0
    for i in range(8):
        for j in range(8):
            if s.board[i][j] == 1:
                pygame.draw.circle(screen, (255, 255, 255), (630 + i * 60, 110 + 60 * j), 27)
                cnt_white += 1
            if s.board[i][j] == -1:
                pygame.draw.circle(screen, (0, 0, 0), (630 + i * 60, 110 + 60 * j), 27)
                cnt_black += 1
                
    if s.player == 1:
        for i in s.action():
            pygame.draw.circle(screen, (0, 0, 0), (630 + i[0] * 60, 110 + 60 * i[1]), 27, width = 2)
    screen.blit(panel,(433, 150))
    white_score = myfont.render('%2d' % cnt_white, False, (0, 0, 0))
    black_score = myfont.render('%2d' % cnt_black, False, (0, 0, 0))
    screen.blit(white_score, (540, 220))
    screen.blit(black_score, (540, 170))
    if s.player == 1:
        screen.blit(super_mario, (445, 160))
    else:
        screen.blit(super_mario, (445, 210))
    if t == 0:
        step_time = panel_font.render("AI time: ---", True, blue)
    else:
        step_time = panel_font.render("AI time: %.1f" % t, True, blue)
    screen.blit(step_time, (435, 290))
    total_time = panel_font.render("T total: %.1f" % total_t, True, blue)
    screen.blit(total_time, (435, 345))

    difficulty_str = panel_font.render(levels[difficulty], True, blue)
    screen.blit(difficulty_str, (435, 400))
        


pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((1280,591))

bg = pygame.image.load("bg.jpg").convert()
choose_img = pygame.image.load("choose.png").convert()

blue = 0,0,200
myfont = pygame.font.Font(None,60)
panel_font = pygame.font.Font(None,30)
winImage = myfont.render("You win!!!", True, blue)
loseImage = myfont.render("You lose!!!", True, blue)
tieImage = myfont.render("You tied!!!", True, blue)

panel = pygame.image.load("panel.png").convert()
super_mario = pygame.image.load("super_mario.png").convert()

pygame.display.set_caption('mini-go reversi')
pygame.display.update()

if __name__ == '__main__':
    board = np.zeros((8, 8), dtype = int)
    board[3][3] = 1
    board[4][4] = 1
    board[4][3] = -1
    board[3][4] = -1
    clock.tick(60)
    screen.fill((0,0,0))
    screen.blit(bg,(0,0))
    choose()
    s = State(board, player = player)
    draw_chessboard(screen)
    display(s, screen)

    pygame.display.update()
    while True:
        x,y = pygame.mouse.get_pos()
        if s.player == 1 and s.actions_num == 0 and not s.game_over:
            s.change()
        elif s.player == 0 and not s.game_over:
            if len(s.actions) == 0:
                s.change()
            else:
                start_time = time.time()
                v0 = UTCSearch(s, iters = its[difficulty])
                s = copy.deepcopy(v0.state)
                draw_chessboard(screen)
                display(s, screen)
                pygame.display.update()
                end_time = time.time()
                t = end_time - start_time
                total_t += t
                continue
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                if s.player == 1 and not s.game_over and x > 600 and x < 1080 and y > 80 and y < 560:
                    i, j = (x - 600) // 60, (y - 80) // 60
                    if s.board[i][j] == 0:
                        flag = False
                        for (dr, dc) in [(1, 1), (-1, 1), (-1, -1), (1, -1), (1, 0), (-1, 0), (0, 1), (0, -1)]:
                            r, c = i + dr, j + dc
                            while r < 8 and r >= 0 and c < 8 and c >= 0 and s.board[r][c] == 1:
                                r += dr
                                c += dc
                            if not (r == i + dr and c == j + dc) and r < 8 and r >= 0 and c < 8 and c >= 0 and s.board[r][c] == -1:
                                flag = True
                        if flag:
                            s.result((i, j))
                            s.change()

        draw_chessboard(screen)
        display(s, screen)
        if s.game_over:
            if calculate_score(s) < 0:
                screen.blit(winImage, (750,300))
            elif calculate_score(s) > 0:
                screen.blit(loseImage, (750,300))
            else:
                screen.blit(tieImage, (750,300))

        is_game_over(s)
        pygame.display.update()