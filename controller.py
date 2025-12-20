import pygame
import sys

from ui.play_menu import menu_screen, BoardSize_menu
from ui.play_pvsp import play_pvp
from ui.play_pvsm import play_pvsm
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
            play_pvp(
                screen, clock,
                board_size=size
            )

        # --- PvM Mode ---
        if mode == "PvM":
            size = BoardSize_menu(screen, clock)
            play_pvsm(
                screen, clock,
                board_size=size
            )

       
