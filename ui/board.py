import sys
import time
import pygame
import numpy as np
from ui.config import Button, BOARD_COLOR, black_img, white_img

LEFT_PANEL = 400
BOARD_MARGIN = 80
W, H = 1600, 900

def center_of_cell(board_x, board_y, cell, i, j):
    cx = board_x + j * cell + cell // 2
    cy = board_y + i * cell + cell // 2
    return (cx, cy)

def create_buttons():
    undo_btn = Button((255,200,0), 80, 550, 180, 55, "Undo")
    redo_btn = Button((255,200,0), 80, 625, 180, 55, "Redo")
    restart_btn = Button((0,180,0), 80, 700, 180, 55, "Restart")
    quit_btn = Button((200,100,100), 80, 775, 180, 55, "Quit")
    buttons = [undo_btn, redo_btn, restart_btn, quit_btn]
    return buttons

def compute_board_geometry(board_size):
    from ui.board import W, H, LEFT_PANEL, BOARD_MARGIN

    available_w = W - LEFT_PANEL - 2 * BOARD_MARGIN
    available_h = H - 200
    cell = min(available_w // board_size, available_h // board_size)
    piece_size = int(cell * max(0.4, min(1.2, 9 / board_size)))

    board_x = LEFT_PANEL + BOARD_MARGIN + (available_w - board_size * cell) // 2
    board_y = (H - board_size * cell) // 2

    return cell, piece_size, board_x, board_y

