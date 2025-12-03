
import time
import sys
import pygame
from env.gomoku_env import GomokuEnv, CURRENT, OPPONENT, COLOR
from ui.config import Button, BOARD_COLOR, GRAY, black_img, white_img
import time 
import numpy as np

# Dynamic config
LEFT_PANEL_WIDTH = 400
BOARD_MARGIN = 80
SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 900
FPS = 30
available_width = SCREEN_WIDTH - LEFT_PANEL_WIDTH - 2 * BOARD_MARGIN
available_height = SCREEN_HEIGHT - 200 

# Main Game
def play_board(board_size = 3):
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont('comicsans', 30, bold=True)
    big_font = pygame.font.SysFont('comicsans', 50, bold=True)
    
    # Button
    undo_button = Button((255, 200, 0), 80, 550, 180, 55, "Undo")
    redo_button = Button((255, 200, 0), 80, 625, 180, 55, "Redo")
    restart_button = Button((0,180,0), 80, 700, 180, 55, "Restart")
    quit_button = Button((200, 100, 100), 80, 775, 180, 55, "Quit")

    # Set pieces
    scale_factor = max(0.4, min(1.2, 9 / board_size))

    # Board setup
    cell_size = min(available_width // board_size, available_height // board_size)
    piece_size = int(cell_size * scale_factor)
    board_x = LEFT_PANEL_WIDTH + BOARD_MARGIN + (available_width - board_size * cell_size) // 2
    board_y = (SCREEN_HEIGHT - board_size * cell_size) // 2

    p1_img = pygame.transform.smoothscale(black_img, (piece_size, piece_size))
    p2_img = pygame.transform.smoothscale(white_img, (piece_size, piece_size))

    # Game init
    caro = GomokuEnv(board_size=board_size, n_history=2)
    state, board = caro.reset()
    undo_stack, redo_stack = [], []
    winner = None
    turn = "P1"
    start_time = time.time()
    elapsed_time = 0
    
    while True:
        dt = clock.tick(FPS) / 1000.0
        screen.fill(BOARD_COLOR)

        # Update time 
        if not winner:
            elapsed_time = time.time() - start_time

        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        centiseconds = int((elapsed_time * 100) % 100)
        
        # Left panel
        pygame.draw.rect(screen, (225, 230, 235), (0, 0, LEFT_PANEL_WIDTH, SCREEN_HEIGHT))

        # Show time
        time_label = big_font.render("Game time", True, (0,0,0))
        screen.blit(time_label, (60, 80))

        time_value = font.render(f"{minutes:02}:{seconds:02}:{centiseconds:02}", True, (20, 100, 200))
        screen.blit(time_value, (130, 140))  

        # Turn info
        turn_label = big_font.render("Turn", True, (0,0,0))
        screen.blit(turn_label, (130, 220))

        if turn == "P1":
            turn_value = font.render("Player 1 (X)", True, (0, 150, 0))
        else:
            turn_value = font.render("Player 2 (O)", True, (0, 0, 180))
        screen.blit(turn_value, (90, 270))


        # Buttons
        for btn in [undo_button, redo_button, restart_button, quit_button]:
            btn.draw(screen)

        # Draw board grid
        for i in range(board_size):
            for j in range(board_size):
                rect = pygame.Rect(board_x + j * cell_size, board_y + i * cell_size, cell_size, cell_size)
                pygame.draw.rect(screen, (0, 0, 0), rect, 1)
        
        current_board = caro.board[CURRENT].reshape(board_size, board_size)
        opponent_board = caro.board[OPPONENT].reshape(board_size, board_size)
        color_board = caro.board[COLOR]

        last_action = getattr(caro, "action", None)
        action_coord = None

        if last_action is not None:
            action_x = last_action // board_size
            action_y = last_action % board_size
            action_coord = (action_x, action_y)

            if (last_action + 1) % board_size != 0:
                action_right = ((last_action + 1) // board_size, (last_action + 1) % board_size)

        for i in range(board_size):
            for j in range(board_size):
                cx = board_x + j * cell_size + cell_size // 2
                cy = board_y + i * cell_size + cell_size // 2
                rect_center = (cx, cy)
                index = i * board_size + j

                if action_coord and (i, j) == action_coord:
                    pygame.draw.circle(screen, (255, 215, 0), rect_center, piece_size // 2 + 4, 4)

                if color_board[0] == 1:  # if CURRENT is Black
                    if current_board[i, j] == 1:
                            screen.blit(p1_img, p1_img.get_rect(center=rect_center))
                    elif opponent_board[i, j] == 1:
                            screen.blit(p2_img, p2_img.get_rect(center=rect_center))
                else:  # if CURRENT is White
                    if current_board[i, j] == 1:
                        screen.blit(p2_img, p2_img.get_rect(center=rect_center))
                    elif opponent_board[i, j] == 1:
                        screen.blit(p1_img, p1_img.get_rect(center=rect_center))

        # Winner
        if winner:
            msg = big_font.render(f"{winner} Wins!", True, (255, 0, 0))
            screen.blit(msg, (80, 480))

        pygame.display.flip()

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()

                # Buttons
                if undo_button.is_over(pos) and undo_stack:
                    prev_state, prev_turn, prev_color = undo_stack.pop()
                    redo_stack.append((caro.state.copy(), turn, caro.board[COLOR].copy()))
                    caro.state = prev_state.copy()
                    caro.board[CURRENT] = prev_state[:board_size**2].copy()
                    caro.board[OPPONENT] = prev_state[board_size**2:2*board_size**2].copy()
                    caro.board[COLOR] = prev_color.copy()
                    turn = prev_turn
                    board_fill = caro.board[CURRENT] + caro.board[OPPONENT]
                    if np.any(board_fill):  
                        _, _, reward, done = caro._check_win(caro.board[CURRENT].reshape(board_size, board_size), display=False)
                        winner = turn if done and reward != 0 else None
                    else:
                        winner = None  # chưa có nước đi

                elif redo_button.is_over(pos) and redo_stack:
                    next_state, next_turn, next_color = redo_stack.pop()
                    undo_stack.append((caro.state.copy(), turn, caro.board[COLOR].copy()))
                    caro.state = next_state.copy()
                    caro.board[CURRENT] = next_state[:board_size**2].copy()
                    caro.board[OPPONENT] = next_state[board_size**2:2*board_size**2].copy()
                    caro.board[COLOR] = next_color.copy()
                    turn = next_turn

                elif restart_button.is_over(pos):
                    caro.reset()
                    undo_stack.clear()
                    redo_stack.clear()
                    winner, turn = None, "P1"
                    start_time = time.time()
                    elapsed_time = 0

                elif quit_button.is_over(pos):
                    pygame.quit()
                    sys.exit()

                # Click on board
                elif pos[0] > board_x and pos[1] > board_y and not winner:
                    col = (pos[0] - board_x) // cell_size
                    row = (pos[1] - board_y) // cell_size
                    action = row * board_size + col
                    if 0 <= row < board_size and 0 <= col < board_size:
                        # check clear board
                        board_fill = caro.board[CURRENT] + caro.board[OPPONENT]
                        if board_fill[action] == 0:  
                            undo_stack.append((caro.state.copy(), turn, caro.board[COLOR].copy()))
                            redo_stack.clear()
                            state, board, reward, done = caro.step(action)  
                            if done:
                                winner = turn
                            else:
                                turn = "P2" if turn == "P1" else "P1"
                        else:
                            print("Invalid move!")  

# if __name__ == "__main__":
#     play_board(board_size=15)