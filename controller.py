import pygame
import sys

from ui.play_menu import menu_screen, BoardSize_menu
from ui.board import play_board

def run_controller():
    pygame.init()
    screen = pygame.display.set_mode((1600, 900))
    clock = pygame.time.Clock()

    while True:
        mode = menu_screen(screen, clock)  # return "PvP", "PvM", "Quit"

        if mode == "Quit":
            pygame.quit()
            sys.exit()

        # --- PvP Mode ---
        if mode == "PvP":
            size = BoardSize_menu(screen, clock)
            play_board(
                screen, clock,
                mode="PvP",
                board_size=size
            )

        # --- PvM Mode ---
        if mode == "PvM":
            size = BoardSize_menu(screen, clock)
            play_board(
                screen, clock,
                mode="PvM",
                board_size=size
            )

       
