import sys
import time
import pygame
import numpy as np

from env.gomoku_env import GomokuEnv, CURRENT, OPPONENT, COLOR
from ui.config import Button, BOARD_COLOR, black_img, white_img

LEFT_PANEL = 400
BOARD_MARGIN = 80
W, H = 1600, 900
FPS = 30


def center_of_cell(board_x, board_y, cell, i, j):
    cx = board_x + j * cell + cell // 2
    cy = board_y + i * cell + cell // 2
    return (cx, cy)


def play_board(screen, clock, board_size=15, mode="PvP"):

    font = pygame.font.SysFont('comicsans', 28, bold=True)
    big = pygame.font.SysFont('comicsans', 40, bold=True)

    # Buttons
    undo_btn = Button((255,200,0), 80, 550, 180, 55, "Undo")
    redo_btn = Button((255,200,0), 80, 625, 180, 55, "Redo")
    restart_btn = Button((0,180,0), 80, 700, 180, 55, "Restart")
    quit_btn = Button((200,100,100), 80, 775, 180, 55, "Quit")
    buttons = [undo_btn, redo_btn, restart_btn, quit_btn]

    # Board geometry
    available_w = W - LEFT_PANEL - 2 * BOARD_MARGIN
    available_h = H - 200
    cell = min(available_w // board_size, available_h // board_size)
    piece_size = int(cell * max(0.4, min(1.2, 9 / board_size)))

    board_x = LEFT_PANEL + BOARD_MARGIN + (available_w - board_size * cell) // 2
    board_y = (H - board_size * cell) // 2

    p1_img = pygame.transform.smoothscale(black_img, (piece_size, piece_size))
    p2_img = pygame.transform.smoothscale(white_img, (piece_size, piece_size))

    # Game init
    env = GomokuEnv(board_size=board_size, n_history=2)
    state, _ = env.reset()

    undo_stack = []
    redo_stack = []
    winner = None
    turn = 'P1'

    start_time = time.time()

    # -------------------------------
    # MAIN LOOP
    # -------------------------------
    while True:
        dt = clock.tick(FPS) / 1000
        screen.fill(BOARD_COLOR)

        # Left panel bg
        pygame.draw.rect(screen, (230,235,240), (0, 0, LEFT_PANEL, H))

        # Time
        elapsed = time.time() - start_time if not winner else elapsed
        m, s = divmod(int(elapsed), 60)
        cs = int((elapsed * 100) % 100)

        screen.blit(big.render("Game time", True, (0,0,0)), (60, 80))
        screen.blit(font.render(f"{m:02}:{s:02}:{cs:02}", True, (20,100,200)), (120, 140))

        # Turn
        screen.blit(big.render("Turn", True, (0,0,0)), (130, 220))
        turn_color = (0,150,0) if turn == "P1" else (0,0,180)
        screen.blit(font.render(f"{turn}", True, turn_color), (150, 270))

        # Buttons
        for b in buttons:
            b.draw(screen)

        # Draw board grid
        for i in range(board_size):
            for j in range(board_size):
                pygame.draw.rect(
                    screen, (0,0,0),
                    (board_x + j*cell, board_y + i*cell, cell, cell), 1
                )

        # Board data
        cur = env.board[CURRENT].reshape(board_size, board_size)
        opp = env.board[OPPONENT].reshape(board_size, board_size)
        color = env.board[COLOR][0]

        # Highlight last move
        last = getattr(env, "action", None)
        last_xy = (last // board_size, last % board_size) if last is not None else None

        # Draw pieces
        for i in range(board_size):
            for j in range(board_size):
                cx, cy = center_of_cell(board_x, board_y, cell, i, j)
                rect = (cx - piece_size//2, cy - piece_size//2)

                if (i, j) == last_xy:
                    pygame.draw.circle(screen, (255,215,0), (cx,cy), piece_size//2 + 4, 4)

                if color == 1:
                    if cur[i,j] == 1: screen.blit(p1_img, rect)
                    if opp[i,j] == 1: screen.blit(p2_img, rect)
                else:
                    if cur[i,j] == 1: screen.blit(p2_img, rect)
                    if opp[i,j] == 1: screen.blit(p1_img, rect)

        if winner:
            screen.blit(big.render(f"{winner} Wins!", True, (255,0,0)), (80, 480))

        pygame.display.flip()

        # ----------------------------------
        # EVENTS (fixed)
        # ----------------------------------
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return

            if e.type != pygame.MOUSEBUTTONDOWN:
                continue

            pos = e.pos

            # ---------- UNDO ----------
            if undo_btn.is_over(pos):
                if mode == "PvP":
                    if len(undo_stack) > 0:
                        # push current to redo
                        redo_stack.append((env.state.copy(), turn, env.board[COLOR].copy()))
                        prev_state, prev_turn, prev_color = undo_stack.pop()

                        env.state = prev_state.copy()
                        env.board[CURRENT] = prev_state[:board_size**2]
                        env.board[OPPONENT] = prev_state[board_size**2:2*board_size**2]
                        env.board[COLOR] = prev_color.copy()
                        turn = prev_turn
                        winner = None
                    else:
                        print("Nothing to undo (PvP).")
                    continue

                # PvM: undo 2 steps (player + bot)
                if mode == "PvM":
                    if len(undo_stack) < 2:
                        print("Cannot undo: need at least 2 steps (player+bot).")
                        continue

                    # pop bot state then player state
                    bot_state, bot_turn, bot_color = undo_stack.pop()
                    player_state, player_turn, player_color = undo_stack.pop()

                    # push current and bot_state into redo so we can redo 2 steps
                    redo_stack.append((env.state.copy(), turn, env.board[COLOR].copy()))
                    redo_stack.append((bot_state.copy(), bot_turn, bot_color.copy()))

                    # restore to player_state (state before player moved)
                    env.state = player_state.copy()
                    env.board[CURRENT] = player_state[:board_size**2]
                    env.board[OPPONENT] = player_state[board_size**2:2*board_size**2]
                    env.board[COLOR] = player_color.copy()
                    turn = player_turn
                    winner = None
                    continue

            # ---------- REDO ----------
            if redo_btn.is_over(pos):
                if mode == "PvP":
                    if len(redo_stack) > 0:
                        nxt_state, nxt_turn, nxt_color = redo_stack.pop()
                        undo_stack.append((env.state.copy(), turn, env.board[COLOR].copy()))

                        env.state = nxt_state.copy()
                        env.board[CURRENT] = nxt_state[:board_size**2]
                        env.board[OPPONENT] = nxt_state[board_size**2:2*board_size**2]
                        env.board[COLOR] = nxt_color.copy()
                        turn = nxt_turn
                        winner = None
                    else:
                        print("Nothing to redo (PvP).")
                    continue

                # PvM redo 2 steps
                if mode == "PvM":
                    if len(redo_stack) < 2:
                        print("Cannot redo: need 2 states for PvM redo.")
                        continue

                    # pop bot then player (we stored bot second)
                    bot_state, bot_turn, bot_color = redo_stack.pop()
                    player_state, player_turn, player_color = redo_stack.pop()

                    # push current to undo and bot state to undo to keep history
                    undo_stack.append((env.state.copy(), turn, env.board[COLOR].copy()))
                    undo_stack.append((bot_state.copy(), bot_turn, bot_color.copy()))

                    # restore to player_state advanced (player_state is after player moved? depends on how you stored)
                    # We stored player_state as the one to restore to when undo, for redo we restore the later state:
                    env.state = player_state.copy()
                    env.board[CURRENT] = player_state[:board_size**2]
                    env.board[OPPONENT] = player_state[board_size**2:2*board_size**2]
                    env.board[COLOR] = player_color.copy()
                    turn = player_turn
                    winner = None
                    continue

            # ---------- RESTART ----------
            if restart_btn.is_over(pos):
                env.reset()
                undo_stack.clear()
                redo_stack.clear()
                winner = None
                turn = "P1"
                start_time = time.time()
                continue

            # ---------- QUIT ----------
            if quit_btn.is_over(pos):
                return

            # ---------- CLICK ON BOARD ----------
            if not winner and pos[0] > board_x and pos[1] > board_y:
                j = (pos[0] - board_x) // cell
                i = (pos[1] - board_y) // cell
                if not (0 <= i < board_size and 0 <= j < board_size):
                    continue

                action = i * board_size + j
                filled = env.board[CURRENT] + env.board[OPPONENT]
                if filled[action] != 0:
                    # invalid move
                    print("Invalid move:", (i, j))
                    continue

                # --- Save state BEFORE player move ---
                undo_stack.append((env.state.copy(), turn, env.board[COLOR].copy()))
                redo_stack.clear()

                # Player move
                state_after, board_after, reward, done = env.step(action)

                # Print debug state to terminal (you asked for this earlier)
                print("\n--- MOVE ---")
                print("Action:", (i, j), "Index:", action)
                print("Reward:", reward, "Done:", done)
                print("State vector (first 50 elems):", state_after.flatten()[:50])
                print("CURRENT board:\n", env.board[CURRENT].reshape(board_size, board_size))
                print("OPPONENT board:\n", env.board[OPPONENT].reshape(board_size, board_size))

                # Determine winner based on reward
                if done:
                    if reward == 1:
                        # the player who just moved wins -> that's the player who made the action
                        winner = turn
                    elif reward == -1:
                        # opponent wins (since reward -1 for current player's perspective)
                        winner = ("P2" if turn == "P1" else "P1")
                    else:
                        winner = "Draw"
                    continue  # no bot move if game finished

                # switch turn
                turn = "P2" if turn == "P1" else "P1"

                # --- BOT MOVE for PvM ---
                if mode == "PvM":
                    legal = np.where((env.board[CURRENT] + env.board[OPPONENT]) == 0)[0]
                    if len(legal) > 0:
                        # save before bot move
                        undo_stack.append((env.state.copy(), turn, env.board[COLOR].copy()))
                        bot_action = np.random.choice(legal)
                        state_b, board_b, reward_b, done_b = env.step(bot_action)

                        # debug print
                        print("\n--- BOT MOVE ---")
                        print("Bot action index:", bot_action)
                        print("Reward_b:", reward_b, "Done_b:", done_b)
                        print("CURRENT board after bot:\n", env.board[CURRENT].reshape(board_size, board_size))
                        print("OPPONENT board after bot:\n", env.board[OPPONENT].reshape(board_size, board_size))

                        if done_b:
                            if reward_b == 1:
                                winner = turn  # bot (current at time of move)
                            elif reward_b == -1:
                                winner = ("P2" if turn == "P1" else "P1")
                            else:
                                winner = "Draw"
                        else:
                            # if no win, switch back to player
                            turn = "P1"
