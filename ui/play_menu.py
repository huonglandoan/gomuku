import pygame
import sys
from ui.config import Button, FPS

# -------------------------------
#  UNIVERSAL MENU CHUNG
# -------------------------------
def universal_menu(screen, clock, title, buttons_info):
    """
    buttons_info = list of (label, return_value, color)
    """
    font = pygame.font.SysFont('comicsans', 90, bold=True)
    title_text = font.render(title, True, (0, 0, 0))

    start_y = 400
    spacing = 150
    buttons = []

    # Tạo button theo màu bạn muốn
    for i, (label, value, color) in enumerate(buttons_info):
        btn = Button(
            color,
            640,
            start_y + spacing * i,
            450,
            100,
            label
        )
        buttons.append((btn, value))

    while True:
        screen.fill((230, 230, 240))
        screen.blit(title_text, (screen.get_width() / 2 - title_text.get_width() / 2, 150))

        # Vẽ button
        for btn, _ in buttons:
            btn.draw(screen)

        pygame.display.update()
        clock.tick(FPS)

        # Event xử lý
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            for btn, return_val in buttons:
                if btn.handle_event(event):
                    return return_val


# -------------------------------
#  MENU CHÍNH
# -------------------------------
def menu_screen(screen, clock):
    return universal_menu(
        screen, clock,
        "Caro Game",
        [
            ("Play with Friend", "PvP", (0, 200, 0)),      
            ("Play with Robot", "PvM", (50, 150, 255)),    
            ("Quit", "Quit", (200, 50, 50))                
        ]
    )


# -------------------------------
#  MENU CHỌN KÍCH THƯỚC BÀN CỜ
# -------------------------------
def BoardSize_menu(screen, clock):
    return universal_menu(
        screen, clock,
        "Board Size",
        [
            ("3 x 3", 3, (0, 200, 0)),
            ("9 x 9", 9, (50, 150, 255)),
            ("15 x 15", 15, (60, 100, 100))
        ]
    )


