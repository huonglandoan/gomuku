import pygame

BOARD_COLOR = (255, 255, 255)
GRAY = (180, 180, 180)
FPS = 90
MARGIN = 100

black_img = pygame.image.load("assets/char_x.png")
white_img = pygame.image.load("assets/char_o.png")

class Button:
    def __init__(self, color, x, y, width, height, text='', hover_color=None, click_color=None):
        self.color = color
        self.hover_color = hover_color if hover_color else (
            min(color[0] + 30, 255),
            min(color[1] + 30, 255),
            min(color[2] + 30, 255)
        )
        self.click_color = click_color if click_color else (
            max(color[0] - 30, 0),
            max(color[1] - 30, 0),
            max(color[2] - 30, 0)
        )
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.is_pressed = False  

    def draw(self, win, outline=None):
        mouse_pos = pygame.mouse.get_pos()
        color = self.color

        # hover animation
        if self.is_over(mouse_pos):
            color = self.hover_color
        # Click animation
        if self.is_pressed:
            color = self.click_color

        if outline:
            pygame.draw.rect(win, outline, (self.x - 2, self.y - 2, self.width + 4, self.height + 4), 0)

        pygame.draw.rect(win, color, (self.x, self.y, self.width, self.height), border_radius=8)

        if self.text != '':
            font = pygame.font.SysFont('comicsans', 50, bold=True)
            text = font.render(self.text, True, (0, 0, 0))
            text_x = self.x + (self.width - text.get_width()) // 2
            text_y = self.y + (self.height - text.get_height()) // 2
            win.blit(text, (text_x, text_y))

    def is_over(self, pos):
        return self.x < pos[0] < self.x + self.width and self.y < pos[1] < self.y + self.height

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_over(pygame.mouse.get_pos()):
                self.is_pressed = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.is_pressed and self.is_over(pygame.mouse.get_pos()):
                self.is_pressed = False
                return True  # Click valid
            self.is_pressed = False
        return False
