import pygame
import time
import numpy as np
from env.gomoku_env import GomokuEnv, CURRENT, OPPONENT, COLOR
from ui.board import create_buttons, compute_board_geometry, center_of_cell, W, H, BOARD_COLOR
from ui.config import black_img, white_img

def play_pvp(screen, clock, board_size=15):

    font = pygame.font.SysFont('comicsans', 28, bold=True)
    big = pygame.font.SysFont('comicsans', 40, bold=True)

    # ---- geometry ----
    cell, piece_size, board_x, board_y = compute_board_geometry(board_size)

    # ---- pieces ----
    p1_img = pygame.transform.smoothscale(black_img, (piece_size, piece_size))
    p2_img = pygame.transform.smoothscale(white_img, (piece_size, piece_size))

    # ---- buttons ----
    undo_btn, redo_btn, restart_btn, quit_btn = create_buttons()

    # ---- gomoku env ----
    env = GomokuEnv(board_size=board_size, n_history=2)
    state, _ = env.reset()

    undo_stack = []
    redo_stack = []

    winner = None
    turn = 'P1'
    start_time = time.time()
    end_time = None


    # ==================================================
    # MAIN LOOP
    # ==================================================
    while True:
        dt = clock.tick(30)
        screen.fill(BOARD_COLOR)

        # ---------------- LEFT PANEL ----------------
        pygame.draw.rect(screen, (230,235,240), (0, 0, 400, H))

        if winner is None:
            elapsed = time.time() - start_time
        else:
            elapsed = end_time - start_time

        m, s = divmod(int(elapsed), 60)
        cs = int((elapsed * 100) % 100)

        screen.blit(big.render("Game time", True, (0,0,0)), (60, 80))
        screen.blit(font.render(f"{m:02}:{s:02}:{cs:02}", True, (20,100,200)), (120,140))

        screen.blit(big.render("Turn", True, (0,0,0)), (130,220))
        screen.blit(font.render(turn, True, (0,100,200)), (150,270))

        # buttons
        undo_btn.draw(screen)
        redo_btn.draw(screen)
        restart_btn.draw(screen)
        quit_btn.draw(screen)

        # ---------------- DRAW BOARD ----------------
        cur = env.board[CURRENT].reshape(board_size, board_size)
        opp = env.board[OPPONENT].reshape(board_size, board_size)
        color = env.board[COLOR][0]

        last = getattr(env, "action", None)
        last_xy = (last // board_size, last % board_size) if last is not None else None

        for i in range(board_size):
            for j in range(board_size):
                x = board_x + j * cell
                y = board_y + i * cell
                pygame.draw.rect(screen, (0,0,0), (x,y,cell,cell), 1)

                cx, cy = center_of_cell(board_x, board_y, cell, i, j)
                rect = (cx - piece_size//2, cy - piece_size//2)

                if (i,j) == last_xy:
                    pygame.draw.circle(screen, (255,215,0), (cx,cy), piece_size//2+4, 4)

                if color == 1:
                    if cur[i,j] == 1: screen.blit(p1_img, rect)
                    if opp[i,j] == 1: screen.blit(p2_img, rect)
                else:
                    if cur[i,j] == 1: screen.blit(p2_img, rect)
                    if opp[i,j] == 1: screen.blit(p1_img, rect)

        if winner:
            screen.blit(big.render(f"{winner} Wins!", True, (255,0,0)), (80,480))

        pygame.display.flip()

        # ---------------- EVENTS ----------------
        for e in pygame.event.get():

            if e.type == pygame.QUIT:
                return

            if e.type != pygame.MOUSEBUTTONDOWN:
                continue

            pos = e.pos

            # ---------------- UNDO ----------------
            if undo_btn.is_over(pos):
                if undo_stack:
                    redo_stack.append((env.state.copy(), turn, env.board[COLOR].copy()))

                    prev_state, prev_turn, prev_color = undo_stack.pop()
                    env.state = prev_state.copy()
                    env.board[CURRENT] = prev_state[:board_size**2]
                    env.board[OPPONENT] = prev_state[board_size**2:2*board_size**2]
                    env.board[COLOR] = prev_color.copy()

                    turn = prev_turn
                    winner = None
                continue

            # ---------------- REDO ----------------
            if redo_btn.is_over(pos):
                if redo_stack:
                    nxt_state, nxt_turn, nxt_color = redo_stack.pop()

                    undo_stack.append((env.state.copy(), turn, env.board[COLOR].copy()))
                    env.state = nxt_state.copy()
                    env.board[CURRENT] = nxt_state[:board_size**2]
                    env.board[OPPONENT] = nxt_state[board_size**2:2*board_size**2]
                    env.board[COLOR] = nxt_color.copy()

                    turn = nxt_turn
                    winner = None
                continue

            # ---------------- RESTART ----------------
            if restart_btn.is_over(pos):
                env.reset()
                undo_stack.clear()
                redo_stack.clear()
                winner = None
                turn = "P1"
                start_time = time.time()
                end_time = None
                continue

            # ---------------- QUIT ----------------
            if quit_btn.is_over(pos):
                return

            # ---------------- BOARD CLICK ----------------
            if not winner and pos[0] >= board_x and pos[1] >= board_y:

                j = (pos[0] - board_x) // cell
                i = (pos[1] - board_y) // cell

                if not(0 <= i < board_size and 0 <= j < board_size):
                    continue

                action = i * board_size + j
                filled = env.board[CURRENT] + env.board[OPPONENT]

                if filled[action] != 0:
                    continue

                # save before move
                undo_stack.append((env.state.copy(), turn, env.board[COLOR].copy()))
                redo_stack.clear()

                state_after, _, reward, done = env.step(action)

                if done:
                    winner = turn if reward == 1 else ("P2" if turn == "P1" else "P1")
                    end_time = time.time()
                    final_elapsed = end_time - start_time
                else:
                    turn = "P2" if turn == "P1" else "P1"
