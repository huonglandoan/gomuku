import pygame
import time
from env.gomoku_env import GomokuEnv, CURRENT, OPPONENT, COLOR, BLACK, WHITE
from mcts.mcts_uct import MCTS
from ui.board import create_buttons, compute_board_geometry, center_of_cell, W, H, BOARD_COLOR
from ui.config import black_img, white_img


def play_pvsm(screen, clock, board_size=15):

    font = pygame.font.SysFont('comicsans', 28, bold=True)
    big = pygame.font.SysFont('comicsans', 40, bold=True)

    # ---- geometry ----
    cell, piece_size, board_x, board_y = compute_board_geometry(board_size)

    p1_img = pygame.transform.smoothscale(black_img, (piece_size, piece_size))
    p2_img = pygame.transform.smoothscale(white_img, (piece_size, piece_size))

    undo_btn, redo_btn, restart_btn, quit_btn = create_buttons()

    # ---- ENV + MCTS ----
    env = GomokuEnv(board_size=board_size, n_history=2)
    mcts = MCTS(board_size, 2, n_simul=1000)

    state, board = env.reset()

    winner = None
    turn = "Player"
    start_time = time.time()
    final_elapsed = None

    # ================= MAIN LOOP =================
    while True:
        clock.tick(30)
        screen.fill(BOARD_COLOR)

        pygame.draw.rect(screen, (230,235,240), (0, 0, 400, H))

        # -------- TIMER --------
        elapsed = time.time() - start_time if final_elapsed is None else final_elapsed
        m, s = divmod(int(elapsed), 60)
        cs = int((elapsed * 100) % 100)

        screen.blit(big.render("Game time", True, (0,0,0)), (60, 80))
        screen.blit(font.render(f"{m:02}:{s:02}:{cs:02}", True, (20,100,200)), (120,140))
        screen.blit(big.render("Turn", True, (0,0,0)), (130,220))
        screen.blit(font.render(turn, True, (0,100,200)), (120,270))

        undo_btn.draw(screen)
        redo_btn.draw(screen)
        restart_btn.draw(screen)
        quit_btn.draw(screen)

        # -------- DRAW BOARD --------
        cur = env.board[CURRENT].reshape(board_size, board_size)
        opp = env.board[OPPONENT].reshape(board_size, board_size)
        color = env.board[COLOR][0]

        for i in range(board_size):
            for j in range(board_size):
                x = board_x + j * cell
                y = board_y + i * cell
                pygame.draw.rect(screen, (0,0,0), (x,y,cell,cell), 1)

                cx, cy = center_of_cell(board_x, 
                                        
                                        board_y, cell, i, j)
                rect = (cx - piece_size//2, cy - piece_size//2)

                if color == BLACK:
                    if cur[i,j]: screen.blit(p1_img, rect)
                    if opp[i,j]: screen.blit(p2_img, rect)
                else:
                    if cur[i,j]: screen.blit(p2_img, rect)
                    if opp[i,j]: screen.blit(p1_img, rect)

        if winner:
            screen.blit(big.render(f"{winner} Wins!", True, (255,0,0)), (70,480))

        pygame.display.flip()

        # ================= EVENTS =================
        for e in pygame.event.get():

            if e.type == pygame.QUIT:
                return

            if e.type != pygame.MOUSEBUTTONDOWN:
                continue

            pos = e.pos

            if restart_btn.is_over(pos):
                state, board = env.reset()
                mcts.reset_tree()
                winner = None
                turn = "Player"
                start_time = time.time()
                final_elapsed = None
                continue

            if quit_btn.is_over(pos):
                return

            if winner:
                continue

            # ===== PLAYER MOVE =====
            if turn == "Player" and pos[0] >= board_x and pos[1] >= board_y:
                j = (pos[0] - board_x) // cell
                i = (pos[1] - board_y) // cell

                if not (0 <= i < board_size and 0 <= j < board_size):
                    continue

                action = i * board_size + j
                filled = env.board[CURRENT] + env.board[OPPONENT]
                if filled[action] != 0:
                    continue

                state, board, reward, done = env.step(action)

                if done:
                    winner = "Player"
                    final_elapsed = time.time() - start_time
                else:
                    turn = "AI"

        # ===== AI MOVE (OUTSIDE EVENT LOOP) =====
        if turn == "AI" and not winner:
            pygame.time.delay(300)
            action = mcts.get_action(state, board)
            state, board, reward, done = env.step(action)

            if done:
                winner = "AI"
                final_elapsed = time.time() - start_time
            else:
                turn = "Player"
