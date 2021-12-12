import pygame
from copy import deepcopy
import random


class Board:
    # создание поля
    def __init__(self, width, height, left=15, top=15, cell_color=(255, 255, 255)):
        self.width = width
        self.height = height
        self.board = [[0] * width for _ in range(height)]
        # значения по умолчанию
        self.left = left
        self.top = top
        self.cell_size = 30
        self.color = cell_color

    # настройка внешнего вида
    def set_view(self, left=15, top=15, cell_size=30):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    def render(self, sc):
        for row in range(self.height):
            for col in range(self.width):
                left, top = self.left + col * self.cell_size, self.top + row * self.cell_size
                if self.board[row][col]:
                    w = 0
                else:
                    w = 1
                pygame.draw.rect(sc, self.color, (left, top, self.cell_size, self.cell_size), width=w)

    def get_click(self, mouse_pos):
        cell = self.get_cell(mouse_pos)
        if cell:
            self.on_click(cell)

    def get_cell(self, mouse_pos):
        x, y = (mouse_pos[0] - self.left), (mouse_pos[1] - self.left)
        if x <= 0 or y <= 0:
            return None
        if x >= self.cell_size * self.width or y >= self.cell_size * self.height:
            return None
        if x % self.cell_size == 0 or x % self.cell_size == 0:
            return None
        return (mouse_pos[1] - self.top) // self.cell_size, (mouse_pos[0] - self.left) // self.cell_size

    def on_click(self, c_cords):
        print(c_cords)

    def checked(self, c):
        return 0 <= c[0] < self.width and 0 <= c[1] < self.height

    def neighbours(self, col, row):
        raw_cords = [(col - 1, row - 1), (col, row - 1), (col + 1, row - 1),
                     (col - 1, row), (col + 1, row),
                     (col - 1, row + 1), (col, row + 1), (col + 1, row + 1)]
        cords = list(map(lambda x: int(self.board[x[1]][x[0]] == 10), filter(lambda x: self.checked(x), raw_cords)))
        return sum(cords)


class GrandSapper(Board):
    def __init__(self, width, height, left=15, top=15, cell_color=(255, 255, 255)):
        super().__init__(width, height, left=left, top=top, cell_color=cell_color)
        self.board = [[''] * width for _ in range(height)]
        bomb_count = int(0.15625 * self.width * self.height)
        for i in range(bomb_count):
            rand_x = random.randint(0, self.width - 1)
            rand_y = random.randint(0, self.height - 1)
            while self.board[rand_y][rand_x] == 10:
                rand_x = random.randint(0, self.width - 1)
                rand_y = random.randint(0, self.height - 1)
            self.board[rand_y][rand_x] = 10

    def render(self, sc):
        for row in range(self.height):
            for col in range(self.width):
                left, top = self.left + col * self.cell_size, self.top + row * self.cell_size
                pygame.draw.rect(sc, self.color, (left, top, self.cell_size, self.cell_size), width=1)
                if self.board[row][col] == '':
                    continue
                elif self.board[row][col] == 10:
                    pygame.draw.rect(sc, pygame.Color("red"), (left, top, self.cell_size, self.cell_size), width=0)
                else:
                    font = pygame.font.Font(None, self.cell_size)
                    text = font.render(str(self.board[row][col]), True, (0, 255, 0))
                    screen.blit(text, (left, top))

    def on_click(self, c_cords):
        if self.board[c_cords[0]][c_cords[1]] != 10:
            self.board[c_cords[0]][c_cords[1]] = self.neighbours(c_cords[1], c_cords[0])


if __name__ == '__main__':
    pygame.init()
    size = width, height = 500, 250
    screen = pygame.display.set_mode(size)
    screen.fill(pygame.Color("black"))
    clock = pygame.time.Clock()
    fps = 60
    board = GrandSapper(25, 15)
    board.set_view(0, 0, 25)
    running = True
    while running:
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                board.get_click(event.pos)
        screen.fill((0, 0, 0))
        board.render(screen)
        clock.tick(fps)
        pygame.display.flip()
    pygame.quit()
